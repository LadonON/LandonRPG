"""!dungeon — host a co-op dungeon run, accept invites, fight through rooms.

Combat happens via DM fan-out: every party member's DM gets every battle line,
plus a turn prompt when it's their turn.

Flow:
  1. Host runs `!dungeon <difficulty> @p1 @p2 ...` in a zone channel.
     A pending invite is created; each invitee runs `!dungeon accept`.
  2. When all invitees accept (or 60s elapses with at least the host), the
     run starts and the first room is populated.
  3. Each round: initiative is rolled; on a player's turn they DM
     `!<weapon_id> <attack_id> [target_index]` or `!<weapon_id> defend`.
  4. After every cleared room (and the boss room), each member gets a
     lootbox added to their inventory.
  5. After the boss falls, XP / loot / lootboxes are distributed.
"""
import asyncio
import random
import time
from dataclasses import dataclass, field

import discord
from discord.ext import commands

from ..services import players
from ..world import zones, dungeons as dungeon_world, lootboxes, weapons, stats as stats_mod
from ..pvp import engine as pvpe
from ..pve import engine as pvee
from ..dungeon import engine as dengine
from .. import style
from ..util import get_or_fetch_user, save_player_async


INVITE_TIMEOUT_SECONDS = 60


# ── Pending invite state ─────────────────────────────────────────────────────

@dataclass
class PendingInvite:
    host_id: int
    host_name: str
    zone_id: str
    zone_difficulty: int
    difficulty: str
    invitee_ids: set                                  # set[int]
    accepted_ids: set = field(default_factory=set)
    declined_ids: set = field(default_factory=set)
    channel_id: int = 0
    started_at: float = field(default_factory=time.time)


# user_id -> PendingInvite (host AND each invitee point at the same object)
_invites: dict[int, PendingInvite] = {}


def _drop_invite(invite: PendingInvite) -> None:
    for uid in [invite.host_id, *invite.invitee_ids]:
        if _invites.get(uid) is invite:
            _invites.pop(uid, None)


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _dm(bot, user_id: int, text: str) -> None:
    try:
        user = await get_or_fetch_user(bot, user_id)
        await user.send(text)
    except Exception:
        pass


async def _dm_embed(bot, user_id: int, embed) -> None:
    try:
        user = await get_or_fetch_user(bot, user_id)
        await user.send(embed=embed)
    except Exception:
        pass


async def _broadcast(bot, run: dengine.DungeonRun, text: str) -> None:
    for p in run.party:
        await _dm(bot, p.user_id, text)


async def _broadcast_embed(bot, run: dengine.DungeonRun, embed) -> None:
    for p in run.party:
        await _dm_embed(bot, p.user_id, embed)


# ── Cog ──────────────────────────────────────────────────────────────────────

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="dungeon", invoke_without_command=True)
    async def dungeon(self, ctx, difficulty: str = None, *invitees: discord.Member):
        # No args → status if in a run, otherwise zone-aware preview
        if difficulty is None:
            run = dengine.get_run(ctx.author.id)
            if run is not None:
                await ctx.send(self._render_run_state(run))
                return

            usage_text = (
                f"`!dungeon <{'|'.join(dungeon_world.DIFFICULTIES)}> [@player ...]` to host • "
                "`!dungeon accept` / `!dungeon decline` to respond • "
                "`!dungeon status` for active run • "
                "`!<weapon_id> defend` to brace • "
                "`!dungeon abandon` to leave."
            )

            if ctx.guild is not None:
                player = players.get_or_create(ctx.author.id, ctx.author.display_name)
                zone = zones.world.get((player.x, player.y))
                if zone is None:
                    embed = style.error(
                        "You aren't in a zone.",
                        "Use `!warp <zone name>` first."
                    )
                    style.add_fields(embed, [("Commands", usage_text, False)])
                    await ctx.send(embed=embed)
                    return
                cfg = dungeon_world.get(zone.zone_id)
                if cfg is None:
                    available = sorted(dungeon_world.DUNGEONS.keys())
                    fix = (f"Try one of: {', '.join(available)}."
                           if available else "No dungeons defined yet.")
                    embed = style.warning(
                        f"No dungeon in {zone.name}.",
                        fix,
                    )
                    style.add_fields(embed, [("Commands", usage_text, False)])
                    await ctx.send(embed=embed)
                    return

                embed = style.lookup(
                    cfg.name,
                    description=cfg.description,
                    footer_context=f"Zone: {zone.name}",
                )
                style.add_fields(embed, [
                    ("Rooms",    str(len(cfg.rooms)), True),
                    ("Boss",     f"`{cfg.boss_id}`", True),
                    ("Commands", usage_text, False),
                ])
                await ctx.send(embed=embed)
                return

            await ctx.send(embed=style.info("Dungeon command usage", usage_text))
            return

        if ctx.guild is None:
            await ctx.send("Run `!dungeon` from a zone channel, not DMs.")
            return

        difficulty = difficulty.lower()
        if difficulty not in dungeon_world.DIFFICULTIES:
            await ctx.send(f"Unknown difficulty `{difficulty}`. Pick one of: {', '.join(dungeon_world.DIFFICULTIES)}.")
            return

        host = players.get_or_create(ctx.author.id, ctx.author.display_name)
        host.user_id = ctx.author.id
        if dengine.in_dungeon(ctx.author.id) or pvpe.in_battle(ctx.author.id) or pvee.in_battle(ctx.author.id):
            await ctx.send("You're already in a battle or dungeon.")
            return

        zone = zones.world.get((host.x, host.y))
        if zone is None:
            await ctx.send("Stand in a zone before running `!dungeon`.")
            return
        dungeon_cfg = dungeon_world.get(zone.zone_id)
        if dungeon_cfg is None:
            await ctx.send(f"There is no dungeon in **{zone.name}** yet.")
            return

        # Validate invitees
        invitee_ids = set()
        for m in invitees[:4]:
            if m.bot or m.id == ctx.author.id:
                continue
            if dengine.in_dungeon(m.id) or m.id in _invites:
                await ctx.send(f"**{m.display_name}** is already busy.")
                return
            invitee_ids.add(m.id)

        invite = PendingInvite(
            host_id=ctx.author.id,
            host_name=ctx.author.display_name,
            zone_id=zone.zone_id,
            zone_difficulty=zone.difficulty,
            difficulty=difficulty,
            invitee_ids=invitee_ids,
            channel_id=ctx.channel.id,
        )
        _invites[ctx.author.id] = invite
        for uid in invitee_ids:
            _invites[uid] = invite

        if not invitee_ids:
            # Solo run — start immediately.
            await ctx.send(f"Solo dungeon run in **{zone.name}** [{difficulty}] starting...")
            await self._start_run(invite)
            return

        await ctx.send(
            f"**{ctx.author.display_name}** is forming a party for **{dungeon_cfg.name}** "
            f"[{difficulty}]. Invited: {', '.join(f'<@{u}>' for u in invitee_ids)}.\n"
            f"Each invitee: run `!dungeon accept` within {INVITE_TIMEOUT_SECONDS}s."
        )
        for uid in invitee_ids:
            await _dm(
                self.bot, uid,
                f"**{ctx.author.display_name}** invited you to **{dungeon_cfg.name}** "
                f"[{difficulty}]. Run `!dungeon accept` to join (or `!dungeon decline`)."
            )

        # Schedule auto-start / timeout
        self.bot.loop.create_task(self._invite_timeout(invite))

    async def _invite_timeout(self, invite: PendingInvite):
        await asyncio.sleep(INVITE_TIMEOUT_SECONDS)
        # If still pending after timeout, start with whoever's accepted.
        if _invites.get(invite.host_id) is invite:
            await self._start_run(invite)

    @dungeon.command(name="accept")
    async def dungeon_accept(self, ctx):
        invite = _invites.get(ctx.author.id)
        if invite is None or ctx.author.id == invite.host_id:
            await ctx.send("No pending dungeon invite for you.")
            return
        invite.accepted_ids.add(ctx.author.id)
        await ctx.send(f"Accepted invite to **{invite.zone_id}** dungeon.")
        # All accepted? Start now.
        if invite.accepted_ids >= invite.invitee_ids:
            await self._start_run(invite)

    @dungeon.command(name="decline")
    async def dungeon_decline(self, ctx):
        invite = _invites.get(ctx.author.id)
        if invite is None or ctx.author.id == invite.host_id:
            await ctx.send("No pending invite.")
            return
        invite.declined_ids.add(ctx.author.id)
        invite.invitee_ids.discard(ctx.author.id)
        _invites.pop(ctx.author.id, None)
        await _dm(self.bot, invite.host_id, f"**{ctx.author.display_name}** declined.")

    @dungeon.command(name="status")
    async def dungeon_status(self, ctx):
        run = dengine.get_run(ctx.author.id)
        if run is None:
            await ctx.send("You're not in a dungeon.")
            return
        await ctx.send(self._render_run_state(run))

    @dungeon.command(name="abandon")
    async def dungeon_abandon(self, ctx):
        run = dengine.get_run(ctx.author.id)
        if run is None:
            await ctx.send("You're not in a dungeon.")
            return
        member = next((p for p in run.party if p.user_id == ctx.author.id), None)
        if member:
            member.hp = 0
        await _broadcast(self.bot, run, f"**{member.name}** abandoned the run.")
        # If everyone's down, end the run.
        if not dengine.alive_party(run):
            await self._fail_run(run)

    # ── Listener: !<weapon_id> <attack_id> [target_index] in dungeon ─────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content.startswith("!"):
            return
        if pvpe.in_battle(message.author.id) or pvee.in_battle(message.author.id):
            return
        run = dengine.get_run(message.author.id)
        if run is None:
            return
        parts = message.content[1:].split()
        if len(parts) < 2:
            return
        weapon_id = parts[0].lower()
        if weapon_id not in weapons.WEAPONS:
            return
        action_id = parts[1].lower()
        if action_id == "defend":
            await self._handle_player_defend(message, run, weapon_id)
            return
        target_index = 0
        if len(parts) >= 3 and parts[2].isdigit():
            target_index = int(parts[2])
        await self._handle_player_attack(message, run, weapon_id, action_id, target_index)

    async def _handle_player_defend(self, message, run, weapon_id: str):
        member = next((p for p in run.party if p.user_id == message.author.id), None)
        if member is None or member.hp <= 0:
            return
        player = players.get_or_create(message.author.id, message.author.display_name)
        if player.equipped_weapon != weapon_id:
            weapon = weapons.get(weapon_id)
            wname = weapon.name if weapon else weapon_id
            await message.channel.send(f"You aren't wielding **{wname}**. Equip it first.")
            return
        member.is_defending = True
        ev = getattr(member, "_action_event", None)
        if ev is not None:
            ev.set()
        weapon = weapons.get(weapon_id)
        await _broadcast(
            self.bot, run,
            f"**{member.name}** raises **{weapon.name}** to brace. "
            f"Next hit on them does 50% damage."
        )

    # ── Run lifecycle ────────────────────────────────────────────────────────

    async def _start_run(self, invite: PendingInvite):
        # Build party from host + accepted invitees
        party_user_ids = [invite.host_id] + [
            uid for uid in invite.invitee_ids if uid in invite.accepted_ids
        ]
        party = []
        for uid in party_user_ids:
            user = await get_or_fetch_user(self.bot, uid)
            p = players.get_or_create(uid, user.display_name)
            p.user_id = uid
            party.append(dengine.PartyMember(
                user_id=uid, name=user.display_name,
                hp=p.max_health, max_hp=p.max_health,
            ))

        dungeon_cfg = dungeon_world.get(invite.zone_id)
        run = dengine.DungeonRun(
            id=dengine.new_run_id(),
            zone_id=invite.zone_id,
            difficulty=invite.difficulty,
            host_user_id=invite.host_id,
            party=party,
            dungeon=dungeon_cfg,
            zone_difficulty=invite.zone_difficulty,
        )
        dengine.RUNS[run.id] = run
        for p in party:
            dengine.PLAYER_RUN[p.user_id] = run.id

        _drop_invite(invite)

        await _broadcast(
            self.bot, run,
            f"⚔ **{dungeon_cfg.name}** [{invite.difficulty}] begins!\n"
            f"Party ({len(party)}): {', '.join(p.name for p in party)}\n"
            f"Dungeon id: `{run.id}`. Use `!<weapon_id> <attack_id> [target_index]` "
            f"to attack on your turn, `!<weapon_id> defend` to brace, or `!dungeon abandon` to leave."
        )
        await self._enter_room(run)

    async def _enter_room(self, run: dengine.DungeonRun):
        dengine.populate_room(run)
        if not run.enemies:
            # No more rooms — victory.
            await self._complete_run(run)
            return

        room_label = "BOSS ROOM" if run.in_boss_room else f"Room {run.room_index + 1}/{len(run.dungeon.rooms)}"
        listing = ", ".join(f"{e.name} (HP {e.hp})" for e in run.enemies)
        await _broadcast(self.bot, run, f"**{room_label}** — Enemies: {listing}")

        if run.in_boss_room:
            boss = run.enemies[0].obj.boss
            for line in boss.dialogue.get("on_spawn", []):
                await _broadcast(self.bot, run, f"_{line}_")
                break  # one spawn line per encounter

        await self._run_round(run)

    async def _run_round(self, run: dengine.DungeonRun):
        """One round: initiative roll, then each combatant acts in order."""
        order = dengine.roll_initiative(run)
        await _broadcast(
            self.bot, run,
            "Round initiative — "
            + ", ".join(f"{('You' if kind=='player' else c.name)} ({init})" for kind, c, init in order)
        )
        for kind, combatant, _ in order:
            if run.ended:
                return
            if kind == "player":
                if combatant.hp <= 0:
                    continue
                await self._prompt_player_turn(run, combatant)
                # The actual attack arrives via on_message listener; we await it.
                await self._await_player_action(run, combatant)
            else:
                if not combatant.is_alive:
                    continue
                result = dengine.enemy_action(combatant, run)
                await _broadcast(self.bot, run, result["text"])
                if not dengine.alive_party(run):
                    await self._fail_run(run)
                    return

        # End-of-round bookkeeping
        if dengine.room_cleared(run):
            await self._room_cleared(run)
        else:
            # Continue to next round.
            await self._run_round(run)

    async def _prompt_player_turn(self, run, member: dengine.PartyMember):
        listing = ", ".join(f"[{i}] {e.name} HP {e.hp}" for i, e in enumerate(dengine.alive_enemies(run)))
        await _dm(
            self.bot, member.user_id,
            f"**Your turn** — HP {member.hp}/{member.max_hp}.\n"
            f"Enemies: {listing}\n"
            f"`!<weapon_id> <attack_id> [target_index]` or `!<weapon_id> defend`."
        )

    async def _await_player_action(self, run: dengine.DungeonRun, member: dengine.PartyMember):
        """Wait up to 60s for this player to act. Auto-pass on timeout.

        Uses an asyncio.Event so the wait wakes immediately when the player
        acts, instead of polling once per second.
        """
        member._action_event = asyncio.Event()
        try:
            await asyncio.wait_for(member._action_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            if not run.ended and member.hp > 0:
                await _broadcast(self.bot, run, f"**{member.name}** hesitated and lost their turn.")

    async def _handle_player_attack(self, message, run, weapon_id, attack_id, target_index):
        member = next((p for p in run.party if p.user_id == message.author.id), None)
        if member is None or member.hp <= 0:
            return
        player = players.get_or_create(message.author.id, message.author.display_name)
        result, err = dengine.player_attack(player, member, run, weapon_id, attack_id, target_index)
        if err:
            await message.channel.send(err)
            return

        # Broadcast the action
        lines = [f"**{member.name}** uses **{result['weapon']} — {result['attack']}** on {result['target_name']}."]
        for i, s in enumerate(result["swings"], 1):
            prefix = f"  Swing {i}: " if len(result["swings"]) > 1 else "  "
            if not s["hit"]:
                lines.append(f"{prefix}d20={s['roll']} miss (AC {s['ac']}).")
            else:
                lines.append(f"{prefix}d20={s['roll']}{' CRIT!' if s['crit'] else ''} hit, dice {s['dice']} → **{s['damage']}** dmg.")
        lines.append(f"  → {result['target_name']}: HP {result['target_hp']}.")
        if result["target_dead"]:
            lines.append(f"  💀 {result['target_name']} falls.")
        await _broadcast(self.bot, run, "\n".join(lines))

        # Wake the round loop immediately instead of waiting for the next poll.
        ev = getattr(member, "_action_event", None)
        if ev is not None:
            ev.set()

    # ── Room/dungeon completion ──────────────────────────────────────────────

    async def _room_cleared(self, run: dengine.DungeonRun):
        boss_room = run.in_boss_room
        awarded = dengine.grant_room_lootboxes(run, boss_room=boss_room)

        # Materialize lootboxes into each player's inventory.
        for p in run.party:
            if not p.pending_lootboxes:
                continue
            player_obj = players.get_or_create(p.user_id, p.name)
            for rarity in p.pending_lootboxes:
                player_obj.inventory.append(lootboxes.lootbox_item_id(rarity))
            p.pending_lootboxes.clear()

        loot_summary = "\n".join(
            f"{p.name}: **{awarded[p.user_id].title()} Lootbox**" for p in run.party
        )
        embed = style.celebration(
            "Boss defeated" if boss_room else "Room cleared",
            footer_context=f"Dungeon: {run.dungeon.name}",
        )
        style.add_fields(embed, [("Lootboxes", loot_summary, False)])
        await _broadcast_embed(self.bot, run, embed)

        if boss_room:
            await self._complete_run(run)
        else:
            run.room_index += 1
            await self._enter_room(run)

    async def _complete_run(self, run: dengine.DungeonRun):
        diff_mult = dungeon_world.DIFFICULTY_MULTIPLIERS.get(run.difficulty, 1.0)
        base_xp = 200 + 80 * run.zone_difficulty
        xp_each = int(base_xp * diff_mult)
        combat_xp_each = max(2, run.zone_difficulty * 3)

        rows = []
        for p in run.party:
            player_obj = players.get_or_create(p.user_id, p.name)
            leveled = player_obj.gain_xp(xp_each)
            leveled_combat = stats_mod.gain_xp(player_obj, "combat", combat_xp_each)
            extras = ""
            if leveled:
                extras += f" → L{player_obj.level}"
            if leveled_combat:
                extras += f" → combat L{player_obj.combat_level}"
            rows.append(f"{p.name}: +{xp_each} XP, +{combat_xp_each} combat XP{extras}")

        # Persist all party members in parallel, off the event loop.
        await asyncio.gather(*(save_player_async(players.save, p.user_id) for p in run.party))

        embed = style.celebration(
            f"Dungeon complete: {run.dungeon.name}",
            description=f"Difficulty: {run.difficulty}",
            footer_context=f"Run {run.id}",
        )
        style.add_fields(embed, [("Rewards", "\n".join(rows), False)])
        await _broadcast_embed(self.bot, run, embed)
        dengine.end_run(run)

    async def _fail_run(self, run: dengine.DungeonRun):
        await _broadcast_embed(
            self.bot, run,
            style.error(
                "Party wiped.",
                "The dungeon swallows your failure. Revived in the Village.",
            ),
        )
        for p in run.party:
            player_obj = players.get_or_create(p.user_id, p.name)
            player_obj.health = player_obj.max_health
        await asyncio.gather(*(save_player_async(players.save, p.user_id) for p in run.party))
        dengine.end_run(run)

    # ── Rendering ────────────────────────────────────────────────────────────

    def _render_run_state(self, run: dengine.DungeonRun) -> str:
        lines = [
            f"**{run.dungeon.name}** [{run.difficulty}] — "
            + ("BOSS ROOM" if run.in_boss_room else f"Room {run.room_index + 1}/{len(run.dungeon.rooms)}")
        ]
        lines.append("Party:")
        for p in run.party:
            lines.append(f"  {p.name}: HP {p.hp}/{p.max_hp}, poise {p.poise}/{p.max_poise}")
        if run.enemies:
            lines.append("Enemies:")
            for i, e in enumerate(dengine.alive_enemies(run)):
                lines.append(f"  [{i}] {e.name} HP {e.hp}")
        return "\n".join(lines)


async def setup(bot):
    await bot.add_cog(Dungeon(bot))
