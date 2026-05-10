"""PVP commands: challenge, wager, accept, attack, forfeit, spectate."""
import asyncio
import random
from dataclasses import dataclass, field

import discord
from discord.ext import commands

from ..services import players
from ..world import items, weapons, stats as stats_mod
from ..pvp import engine as pvp_engine
from .. import style
from ..util import get_or_fetch_user, save_player_async


# PvP win rewards. Beating a player gives a flat base plus a per-opponent-level
# bonus — facing a stronger rival is worth more.
PVP_WIN_BASE_XP = 75
PVP_WIN_XP_PER_OPPONENT_LEVEL = 30
PVP_WIN_BASE_COMBAT_XP = 3


# ── Pending challenges (pre-battle) ──────────────────────────────────────────

@dataclass
class Challenge:
    initiator_id: int
    initiator_name: str
    recipient_id: int
    recipient_name: str
    channel_id: int                          # guild channel where challenge was made
    public: bool = True
    wager_proposed_by: int | None = None     # whoever last named a number
    wager_amount: int = 0
    wager_locked: bool = False               # true once both agree


# user_id (recipient or initiator) -> Challenge
_challenges: dict[int, Challenge] = {}


def _get_my_challenge(user_id: int) -> Challenge | None:
    return _challenges.get(user_id)


def _drop_challenge(c: Challenge) -> None:
    _challenges.pop(c.initiator_id, None)
    _challenges.pop(c.recipient_id, None)


# ── Spectator subscriptions ──────────────────────────────────────────────────
# battle_id -> set[user_id]
_spectators: dict[str, set[int]] = {}


# ── Cog ──────────────────────────────────────────────────────────────────────

class PVP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── Helpers ──────────────────────────────────────────────────────────────

    async def _dm(self, user_id: int, text: str) -> None:
        try:
            user = await get_or_fetch_user(self.bot, user_id)
            await user.send(text)
        except Exception:
            pass

    async def _dm_embed(self, user_id: int, embed) -> None:
        try:
            user = await get_or_fetch_user(self.bot, user_id)
            await user.send(embed=embed)
        except Exception:
            pass

    async def _broadcast(self, battle: pvp_engine.Battle, text: str) -> None:
        for uid in (battle.a.user_id, battle.b.user_id):
            await self._dm(uid, text)
        for uid in _spectators.get(battle.id, set()):
            await self._dm(uid, f"[spectating {battle.id}] {text}")

    async def _broadcast_embed(self, battle: pvp_engine.Battle, embed) -> None:
        for uid in (battle.a.user_id, battle.b.user_id):
            await self._dm_embed(uid, embed)
        for uid in _spectators.get(battle.id, set()):
            await self._dm_embed(uid, embed)

    # ── !pvp <player> ────────────────────────────────────────────────────────

    @commands.group(name="pvp", invoke_without_command=True)
    async def pvp(self, ctx, *, target_name: str = None):
        if target_name is None:
            await ctx.send(
                "Usage:\n"
                "`!pvp <player>` — challenge a player to a duel\n"
                "`!pvp accept` / `!pvp decline` — respond to a challenge\n"
                "`!pvp wager <amount>` — propose/match a gold wager\n"
                "`!pvp public` / `!pvp private` — visibility before battle\n"
                "`!pvp spectate <battle_id>` — watch a public battle\n"
                "`!pvp arena forfeit` — surrender mid-battle"
            )
            return

        if ctx.guild is None:
            await ctx.send("Send `!pvp <player>` from a server channel.")
            return

        if pvp_engine.in_battle(ctx.author.id):
            await ctx.send("You're already in a battle. Use `!pvp arena forfeit` to surrender.")
            return
        if ctx.author.id in _challenges:
            await ctx.send("You already have a pending challenge.")
            return

        target = discord.utils.find(
            lambda m: (
                m.display_name.lower() == target_name.lower()
                or m.name.lower() == target_name.lower()
            ),
            ctx.guild.members,
        )
        if target is None:
            await ctx.send(f"No player named `{target_name}` in this server.")
            return
        if target.id == ctx.author.id:
            await ctx.send("You cannot challenge yourself.")
            return
        if target.bot:
            await ctx.send("You cannot challenge a bot.")
            return
        if target.id in _challenges or pvp_engine.in_battle(target.id):
            await ctx.send(f"**{target.display_name}** is already busy.")
            return

        c = Challenge(
            initiator_id=ctx.author.id,
            initiator_name=ctx.author.display_name,
            recipient_id=target.id,
            recipient_name=target.display_name,
            channel_id=ctx.channel.id,
        )
        _challenges[c.initiator_id] = c
        _challenges[c.recipient_id] = c

        try:
            await ctx.author.send(
                f"PVP challenge sent to **{target.display_name}**.\n"
                f"Waiting for player to accept PVP request.\n"
                f"Use `!pvp wager <amount>` to propose a gold wager, "
                f"`!pvp private` to make the battle non-spectatable."
            )
            await target.send(
                f"**{ctx.author.display_name}** has challenged you to PVP!\n"
                f"`!pvp accept` to enter the arena, `!pvp decline` to refuse, "
                f"`!pvp wager <amount>` to counter-propose a wager."
            )
            await ctx.send(f"PVP challenge sent to **{target.display_name}**. Check your DMs.")
        except Exception:
            _drop_challenge(c)
            await ctx.send("Could not DM both players. Make sure DMs are enabled.")

    # ── !pvp accept ──────────────────────────────────────────────────────────

    @pvp.command(name="accept")
    async def pvp_accept(self, ctx):
        c = _get_my_challenge(ctx.author.id)
        if c is None or ctx.author.id != c.recipient_id:
            await ctx.send("You have no pending challenge to accept.")
            return

        # Validate wager gold for both sides
        a = players.get_or_create(c.initiator_id, c.initiator_name)
        b = players.get_or_create(c.recipient_id, c.recipient_name)
        if c.wager_locked and c.wager_amount > 0:
            if a.gold < c.wager_amount or b.gold < c.wager_amount:
                await ctx.send(
                    f"Wager check failed — both players need {c.wager_amount}g. Lower the wager and retry."
                )
                return
            a.gold -= c.wager_amount
            b.gold -= c.wager_amount

        # Spin up battle
        battle = pvp_engine.Battle(
            id=pvp_engine.new_battle_id(),
            a=pvp_engine.Combatant(
                user_id=c.initiator_id,
                name=c.initiator_name,
                hp=a.max_health,
                max_hp=a.max_health,
            ),
            b=pvp_engine.Combatant(
                user_id=c.recipient_id,
                name=c.recipient_name,
                hp=b.max_health,
                max_hp=b.max_health,
            ),
            wager=c.wager_amount if c.wager_locked else 0,
            public=c.public,
        )
        pvp_engine.BATTLES[battle.id] = battle
        pvp_engine.PLAYER_BATTLE[battle.a.user_id] = battle.id
        pvp_engine.PLAYER_BATTLE[battle.b.user_id] = battle.id
        a.pvp_battle_id = battle.id
        b.pvp_battle_id = battle.id

        # Initiative: random
        first_id = random.choice([battle.a.user_id, battle.b.user_id])
        battle.turn_user_id = first_id

        _drop_challenge(c)

        if battle.public:
            try:
                channel = self.bot.get_channel(c.channel_id) or await self.bot.fetch_channel(c.channel_id)
                await channel.send(embed=style.info(
                    f"PVP Arena: {battle.a.name} vs {battle.b.name}",
                    f"Battle id: `{battle.id}`. Spectate with `!pvp spectate {battle.id}`.",
                ))
            except Exception:
                pass

        opener = self._render_battle_state(battle, a, b)
        first_name = battle.a.name if first_id == battle.a.user_id else battle.b.name
        embed = style.info(
            f"Arena opened ({battle.id})",
            description=f"**{first_name}** acts first.",
            footer_context="`!<weapon> <attack>` • `!<weapon> defend` • `!pvp arena forfeit`",
        )
        style.add_fields(embed, [("Combatants", opener, False)])
        await self._broadcast_embed(battle, embed)

    # ── !pvp decline ─────────────────────────────────────────────────────────

    @pvp.command(name="cancel")
    async def pvp_cancel(self, ctx):
        c = _get_my_challenge(ctx.author.id)
        if c is None or ctx.author.id != c.initiator_id:
            await ctx.send("You don't have a pending challenge to cancel.")
            return
        _drop_challenge(c)
        await self._dm(c.initiator_id, "PVP challenge cancelled.")
        await self._dm(
            c.recipient_id,
            f"**{c.initiator_name}** cancelled their PVP challenge."
        )

    @pvp.command(name="decline")
    async def pvp_decline(self, ctx):
        c = _get_my_challenge(ctx.author.id)
        if c is None:
            await ctx.send("You have no pending challenge.")
            return
        _drop_challenge(c)
        await self._dm(c.initiator_id, f"**{c.recipient_name}** declined the PVP challenge.")
        await self._dm(c.recipient_id, f"You declined **{c.initiator_name}**'s challenge.")

    # ── !pvp wager ───────────────────────────────────────────────────────────

    @pvp.command(name="wager")
    async def pvp_wager(self, ctx, amount: int = None):
        c = _get_my_challenge(ctx.author.id)
        if c is None:
            await ctx.send("No active challenge to wager on.")
            return
        if amount is None or amount < 0:
            await ctx.send("Usage: `!pvp wager <amount>` (gold). 0 to clear.")
            return

        if c.wager_proposed_by is None or c.wager_proposed_by == ctx.author.id:
            # First proposal, or same person updating their proposal
            c.wager_amount = amount
            c.wager_proposed_by = ctx.author.id
            c.wager_locked = False
            other_id = c.recipient_id if ctx.author.id == c.initiator_id else c.initiator_id
            await ctx.send(f"Wager proposed: **{amount}g**. Waiting for opponent to match.")
            await self._dm(
                other_id,
                f"Opponent proposed a **{amount}g** wager. Run `!pvp wager {amount}` to accept "
                f"or `!pvp wager <other>` to counter."
            )
        else:
            # Other side responding
            if amount == c.wager_amount:
                c.wager_locked = True
                await ctx.send(f"Wager locked at **{amount}g** per side.")
                await self._dm(c.wager_proposed_by, f"Opponent matched the **{amount}g** wager. Locked in.")
            else:
                c.wager_amount = amount
                c.wager_proposed_by = ctx.author.id
                c.wager_locked = False
                other_id = c.recipient_id if ctx.author.id == c.initiator_id else c.initiator_id
                await ctx.send(f"Counter-proposed **{amount}g**. Waiting for opponent to match.")
                await self._dm(other_id, f"Opponent counter-proposed **{amount}g**. Run `!pvp wager {amount}` to accept.")

    # ── !pvp public / private ───────────────────────────────────────────────

    @pvp.command(name="public")
    async def pvp_public(self, ctx):
        c = _get_my_challenge(ctx.author.id)
        if c is None:
            await ctx.send("No active challenge.")
            return
        c.public = True
        await ctx.send("Battle visibility: **public** (spectators allowed).")

    @pvp.command(name="private")
    async def pvp_private(self, ctx):
        c = _get_my_challenge(ctx.author.id)
        if c is None:
            await ctx.send("No active challenge.")
            return
        c.public = False
        await ctx.send("Battle visibility: **private** (no spectators).")

    # ── !pvp spectate <id> ───────────────────────────────────────────────────

    @pvp.command(name="spectate")
    async def pvp_spectate(self, ctx, battle_id: str = None):
        if battle_id is None:
            public_battles = [b for b in pvp_engine.BATTLES.values() if b.public]
            if not public_battles:
                await ctx.send("No public battles right now.")
                return
            listing = ", ".join(f"`{b.id}` ({b.a.name} vs {b.b.name})" for b in public_battles)
            await ctx.send(f"Public battles: {listing}\nUse `!pvp spectate <id>`.")
            return

        battle = pvp_engine.BATTLES.get(battle_id)
        if battle is None or not battle.public:
            await ctx.send("No public battle with that id.")
            return
        _spectators.setdefault(battle.id, set()).add(ctx.author.id)
        await ctx.send(f"Now spectating **{battle.a.name} vs {battle.b.name}**. Updates will arrive in DMs.")

    # ── !pvp arena <subcommand> ──────────────────────────────────────────────

    @pvp.group(name="arena", invoke_without_command=True)
    async def pvp_arena(self, ctx):
        battle = pvp_engine.get_battle(ctx.author.id)
        if battle is None:
            await ctx.send("You're not in a PVP arena.")
            return
        a = players.get_or_create(battle.a.user_id, battle.a.name)
        b = players.get_or_create(battle.b.user_id, battle.b.name)
        await ctx.send(self._render_battle_state(battle, a, b))

    @pvp_arena.command(name="forfeit")
    async def pvp_arena_forfeit(self, ctx):
        await self._forfeit(ctx.author.id)

    # Top-level alias: !pvp forfeit
    @pvp.command(name="forfeit")
    async def pvp_forfeit(self, ctx):
        await self._forfeit(ctx.author.id)

    # ── Listener: catch !<weapon_id> <attack_id|defend> ──────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content.startswith("!"):
            return
        if not pvp_engine.in_battle(message.author.id):
            return
        parts = message.content[1:].split()
        if len(parts) < 2:
            return
        weapon_id = parts[0].lower()
        if weapon_id not in weapons.WEAPONS:
            return
        action_id = parts[1].lower()
        if action_id == "defend":
            await self._do_defend(message.author.id, message.channel, weapon_id)
        else:
            await self._do_attack(message.author.id, message.channel, weapon_id, action_id)

    async def _do_defend(self, user_id: int, channel, weapon_id: str) -> None:
        battle = pvp_engine.get_battle(user_id)
        if battle is None:
            return
        if battle.turn_user_id != user_id:
            await channel.send("It's not your turn.")
            return
        # Must be wielding the weapon to defend with it (consistent with attacks).
        me = battle.self_of(user_id)
        attacker_player = players.get_or_create(me.user_id, me.name)
        if attacker_player.equipped_weapon != weapon_id:
            weapon = weapons.get(weapon_id)
            wname = weapon.name if weapon else weapon_id
            await channel.send(f"You aren't wielding **{wname}**. Equip it first.")
            return
        me.is_defending = True
        battle.turn_user_id = battle.opponent_of(user_id).user_id
        weapon = weapons.get(weapon_id)
        await self._broadcast(
            battle,
            f"**{me.name}** raises **{weapon.name}** to brace — next attack does 50% damage."
        )
        await self._announce_turn(battle)

    # ── Battle actions ───────────────────────────────────────────────────────

    async def _do_attack(self, user_id: int, channel, weapon_id: str, attack_id: str) -> None:
        battle = pvp_engine.get_battle(user_id)
        if battle is None:
            return
        if battle.turn_user_id != user_id:
            await channel.send("It's not your turn.")
            return

        attacker_combat = battle.self_of(user_id)
        defender_combat = battle.opponent_of(user_id)
        attacker = players.get_or_create(attacker_combat.user_id, attacker_combat.name)
        defender = players.get_or_create(defender_combat.user_id, defender_combat.name)

        result, err = pvp_engine.resolve_attack(
            attacker, defender, defender_combat, weapon_id, attack_id
        )
        if err:
            await channel.send(err)
            return

        defender_combat.is_defending = False  # consumed
        text = pvp_engine.format_attack_result(attacker_combat.name, defender_combat.name, result)
        await self._broadcast(battle, text)

        if defender_combat.hp <= 0:
            await self._end_battle(battle, winner_id=attacker_combat.user_id, reason="ko")
            return

        # Poise break grants the attacker another turn instead of passing.
        if result.poise_broken:
            await self._announce_turn(battle)
            return

        battle.turn_user_id = defender_combat.user_id
        await self._announce_turn(battle)

    async def _announce_turn(self, battle: pvp_engine.Battle) -> None:
        whose = battle.a if battle.turn_user_id == battle.a.user_id else battle.b
        await self._dm(
            whose.user_id,
            f"Your turn — HP {whose.hp}/{whose.max_hp}, poise {whose.poise}/{whose.max_poise}.\n"
            f"Use `!<weapon_id> <attack_id>`, `!<weapon_id> defend`, or `!pvp arena forfeit`."
        )

    async def _forfeit(self, user_id: int) -> None:
        battle = pvp_engine.get_battle(user_id)
        if battle is None:
            await self._dm(user_id, "You're not in a PVP arena.")
            return
        winner = battle.opponent_of(user_id).user_id
        await self._end_battle(battle, winner_id=winner, reason="forfeit")

    async def _end_battle(self, battle: pvp_engine.Battle, winner_id: int, reason: str) -> None:
        winner_combat = battle.self_of(winner_id)
        loser_combat = battle.opponent_of(winner_id)
        winner_player = players.get_or_create(winner_combat.user_id, winner_combat.name)
        loser_player = players.get_or_create(loser_combat.user_id, loser_combat.name)

        payout = battle.wager * 2
        if payout:
            winner_player.gold += payout

        # XP reward for the winner — scaled by the loser's level / combat level.
        opponent_level = max(getattr(loser_player, "combat_level", 1), 1)
        xp_gained = PVP_WIN_BASE_XP + PVP_WIN_XP_PER_OPPONENT_LEVEL * opponent_level
        combat_xp_gained = PVP_WIN_BASE_COMBAT_XP + opponent_level
        leveled_player = winner_player.gain_xp(xp_gained)
        leveled_combat = stats_mod.gain_xp(winner_player, "combat", combat_xp_gained)

        loser_player.pvp_battle_id = None
        winner_player.pvp_battle_id = None

        verb = "forfeits" if reason == "forfeit" else "is defeated"
        embed = style.celebration(
            f"{winner_combat.name} wins",
            description=f"{loser_combat.name} {verb}.",
            footer_context=f"Battle {battle.id}",
        )
        fields = [
            ("XP",        f"+{xp_gained}", True),
            ("Combat XP", f"+{combat_xp_gained}", True),
        ]
        if payout:
            fields.append(("Pot", f"{payout}g", True))
        notes = []
        if leveled_player:
            notes.append(f"{winner_combat.name} leveled up to {winner_player.level}.")
        if leveled_combat:
            notes.append(f"Combat skill reached L{winner_player.combat_level}.")
        if notes:
            fields.append(("Milestones", " ".join(notes), False))
        style.add_fields(embed, fields)
        await self._broadcast_embed(battle, embed)

        _spectators.pop(battle.id, None)
        pvp_engine.end_battle(battle)

        # Persist both winner + loser in parallel, off the event loop.
        await asyncio.gather(
            save_player_async(players.save, winner_combat.user_id),
            save_player_async(players.save, loser_combat.user_id),
        )

    # ── Rendering ────────────────────────────────────────────────────────────

    def _render_battle_state(self, battle, a_player, b_player) -> str:
        def line(combat, player):
            weapon_id = player.equipped_weapon
            wstr = "(no weapon)"
            if weapon_id:
                w = weapons.get(weapon_id)
                if w:
                    lvl = pvp_engine.instance_level(player, weapon_id)
                    atk_list = ", ".join(a.id for a in w.attacks)
                    wstr = f"{w.name} L{lvl} [{w.weapon_class}] — attacks: {atk_list}"
            return (
                f"**{combat.name}** — HP {combat.hp}/{combat.max_hp}, "
                f"poise {combat.poise}/{combat.max_poise}, defense {pvp_engine.player_defense(player)}\n"
                f"  weapon: {wstr}"
            )
        return f"{line(battle.a, a_player)}\n{line(battle.b, b_player)}"


async def setup(bot):
    await bot.add_cog(PVP(bot))
