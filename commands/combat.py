"""PvE combat — turn-based monster arenas mirroring the PVP arena.

`!attack [<monster>]` opens a battle. While in the arena, the player issues
`!<weapon_id> <attack_id>` (the same syntax used in PVP) to act on their turn.
Monster takes its turn automatically after each player action. Poise-stagger
rules apply: breaking the enemy's poise grants an extra turn.
"""
import random
from collections import Counter

from discord.ext import commands

from ..services import players
from ..world import zones, monsters, items, weapons, stats as stats_mod
from ..pvp import engine as pvpe
from ..pve import engine as pvee
from ..quests import engine as quests_engine
from .. import style


# PvE arena rewards. The new turn-based arena is slower and more involved
# than the old chain-attack flow, so per-fight rewards are scaled up.
PVE_XP_MULTIPLIER = 3
PVE_COMBAT_XP_PER_LEVEL = 2


class Combat(commands.Cog):
    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("Pong!")

    # ── !attack [<monster>] ─────────────────────────────────────────────────

    @commands.command(name="attack", aliases=["fight"])
    async def attack(self, ctx, monster_id: str = None):
        # Already in some battle?
        if pvpe.in_battle(ctx.author.id):
            await ctx.send("You're in a PVP arena. Resolve that first.")
            return
        if pvee.in_battle(ctx.author.id):
            await ctx.send(
                "You're already fighting a monster. Use `!pve arena` for status, "
                "`!<weapon_id> <attack_id>` to attack, or `!pve arena flee`."
            )
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        # Stash user_id on player so the engine's PlayerSide can record it
        player.user_id = ctx.author.id

        zone = zones.world.get((player.x, player.y))
        if zone is None:
            await ctx.send("You're not in a zone. Use `!warp <zone name>`.")
            return
        if not zone.spawn_table:
            await ctx.send(f"There are no monsters to fight in **{zone.name}**.")
            return

        pool = zone.spawn_table
        if monster_id:
            requested = monster_id.lower().rstrip("s")
            pool = [s for s in zone.spawn_table if s.monster_id == requested]
            if not pool:
                available = ", ".join(s.monster_id for s in zone.spawn_table)
                await ctx.send(f"No `{requested}` in **{zone.name}**. Try: {available}.")
                return

        spawn_entry = random.choice(pool)
        monster = monsters.spawn(spawn_entry.monster_id, spawn_entry.level)
        if monster is None:
            await ctx.send(f"Could not spawn `{spawn_entry.monster_id}`.")
            return

        battle = pvee.start_battle(player, monster)

        weapon_line = "(no weapon equipped)"
        if player.equipped_weapon:
            w = weapons.get(player.equipped_weapon)
            if w:
                lvl = pvpe.instance_level(player, player.equipped_weapon)
                attacks = ", ".join(a.id for a in pvpe.available_attacks(player, player.equipped_weapon))
                weapon_line = f"{w.name} L{lvl} [{w.weapon_class}] — attacks: {attacks}"

        embed = style.info(
            f"Encounter: {monster.name}",
            description="`!<weapon_id> <attack_id>` to attack • `!<weapon_id> defend` to brace • `!pve arena flee` to retreat.",
            footer_context=f"Fighter: {ctx.author.display_name}",
        )
        style.add_fields(embed, [
            ("Enemy",
             f"HP {monster.health}/{monster.max_health} • def {monster.defense} • "
             f"poise {monster.poise}/{monster.max_poise}",
             False),
            ("You",
             f"HP {player.health}/{player.max_health} • def {pvpe.player_defense(player)} • "
             f"poise {battle.player.poise}/{battle.player.max_poise}",
             False),
            ("Weapon", weapon_line, False),
        ])
        await ctx.send(embed=embed)

    # ── !pve arena <subcommand> ─────────────────────────────────────────────

    @commands.group(name="pve", invoke_without_command=True)
    async def pve(self, ctx):
        await ctx.send(
            "Usage:\n"
            "`!pve arena` — show current encounter\n"
            "`!<weapon_id> defend` — brace on your turn; next monster hit does 50% damage\n"
            "`!pve arena flee` — retreat from the encounter (no XP/loot)"
        )

    @pve.group(name="arena", invoke_without_command=True)
    async def pve_arena(self, ctx):
        battle = pvee.get_battle(ctx.author.id)
        if battle is None:
            await ctx.send("You're not in a PvE encounter. Use `!attack` to start one.")
            return
        m = battle.enemy.monster
        await ctx.send(
            f"**{m.name}** — HP {m.health}/{m.max_health}, def {m.defense}, "
            f"poise {m.poise}/{m.max_poise}.\n"
            f"You — HP {battle.player.hp}/{battle.player.max_hp}, "
            f"poise {battle.player.poise}/{battle.player.max_poise}, turn: {battle.turn}"
        )

    @pve_arena.command(name="flee")
    async def pve_arena_flee(self, ctx):
        battle = pvee.get_battle(ctx.author.id)
        if battle is None:
            await ctx.send("You're not in a PvE encounter.")
            return
        pvee.end_battle(battle)
        await ctx.send(f"**{battle.player.name}** flees the encounter. No XP, no loot.")

    # ── Listener: !<weapon_id> <attack_id> in PvE ───────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content.startswith("!"):
            return
        # If they're in PVP, the PVP listener handles it.
        if pvpe.in_battle(message.author.id):
            return
        if not pvee.in_battle(message.author.id):
            return
        parts = message.content[1:].split()
        if len(parts) < 2:
            return
        weapon_id = parts[0].lower()
        if weapon_id not in weapons.WEAPONS:
            return
        action_id = parts[1].lower()
        if action_id == "defend":
            await self._do_player_defend(message, weapon_id)
        else:
            await self._do_player_attack(message, weapon_id, action_id)

    async def _do_player_defend(self, message, weapon_id: str):
        battle = pvee.get_battle(message.author.id)
        if battle is None:
            return
        if battle.turn != "player":
            await message.channel.send("It's not your turn.")
            return
        player = players.get_or_create(message.author.id, message.author.display_name)
        if player.equipped_weapon != weapon_id:
            weapon = weapons.get(weapon_id)
            wname = weapon.name if weapon else weapon_id
            await message.channel.send(f"You aren't wielding **{wname}**. Equip it first.")
            return
        battle.player.is_defending = True
        weapon = weapons.get(weapon_id)
        await message.channel.send(
            f"**{battle.player.name}** raises **{weapon.name}** to brace. "
            f"Next monster hit does 50% damage."
        )
        await self._monster_turn(message, battle)

    async def _do_player_attack(self, message, weapon_id: str, attack_id: str):
        battle = pvee.get_battle(message.author.id)
        if battle is None:
            return
        if battle.turn != "player":
            await message.channel.send("It's not your turn.")
            return

        player = players.get_or_create(message.author.id, message.author.display_name)
        result, err = pvee.resolve_player_attack(player, battle.enemy, weapon_id, attack_id)
        if err:
            await message.channel.send(err)
            return

        battle.enemy.is_defending = False
        await message.channel.send(pvee.format_result(result))

        # Monster KO?
        if battle.enemy.hp <= 0:
            await self._victory(message, battle)
            return

        # Poise break grants another player turn.
        if result.poise_broken:
            return

        battle.turn = "monster"
        await self._monster_turn(message, battle)

    # ── Monster turn ─────────────────────────────────────────────────────────

    async def _monster_turn(self, ctx_or_msg, battle):
        send = ctx_or_msg.channel.send if hasattr(ctx_or_msg, "channel") else ctx_or_msg.send
        player = players.get_or_create(battle.player.user_id, battle.player.name)
        result = pvee.resolve_monster_attack(battle.enemy, battle.player, player)
        battle.player.is_defending = False
        await send(pvee.format_result(result))

        if battle.player.hp <= 0:
            await self._defeat(send, battle, player)
            return

        # Monster broke player's poise — monster gets another turn.
        if result.poise_broken:
            await self._monster_turn(ctx_or_msg, battle)
            return

        battle.turn = "player"

    # ── Resolution ───────────────────────────────────────────────────────────

    async def _victory(self, message, battle):
        player = players.get_or_create(battle.player.user_id, battle.player.name)
        monster = battle.enemy.monster

        # Quest hook: count this kill against any matching kill_monster quests.
        if monster.monster_id:
            quests_engine.on_monster_killed(player, monster.monster_id)

        # Bigger XP for the slower turn-based fight; combat-skill XP scales
        # with monster level instead of being a flat +1 per kill.
        xp_gained = monster.xp_reward * PVE_XP_MULTIPLIER
        combat_xp_gained = max(1, getattr(monster, "level", 1) * PVE_COMBAT_XP_PER_LEVEL)
        leveled_player = player.gain_xp(xp_gained)
        leveled_combat = stats_mod.gain_xp(player, "combat", combat_xp_gained)

        drops = 1 + getattr(monster, "level", 1) // 5 + player.combat_level // 3
        loot_dropped: list[str] = []
        for _ in range(drops):
            if monster.loot:
                loot_dropped.append(random.choice(monster.loot))
                player.inventory.append(loot_dropped[-1])

        pvee.end_battle(battle)

        loot_line = ""
        if loot_dropped:
            c = Counter(loot_dropped)
            loot_line = "\nLoot: " + ", ".join(f"{n} x{q}" for n, q in c.items())

        embed = style.celebration(
            f"{player.name} defeats {monster.name}",
            footer_context=f"Combatant: {player.name}",
        )
        fields = [
            ("HP",        f"{player.health}/{player.max_health}", True),
            ("XP",        f"+{xp_gained}", True),
            ("Combat XP", f"+{combat_xp_gained}", True),
        ]
        if loot_dropped:
            c = Counter(loot_dropped)
            fields.append(("Loot", ", ".join(f"{n} x{q}" for n, q in c.items()), False))
        notes = []
        if leveled_player:
            notes.append(f"Player leveled up to {player.level}.")
        if leveled_combat:
            notes.append(f"Combat skill reached L{player.combat_level}.")
        if notes:
            fields.append(("Milestones", " ".join(notes), False))
        style.add_fields(embed, fields)
        await message.channel.send(embed=embed)

    async def _defeat(self, send, battle, player):
        gold_lost = max(1, player.gold // 10)
        gold_lost = min(gold_lost, player.gold)
        player.gold -= gold_lost
        dropped = None
        if player.inventory:
            dropped = random.choice(player.inventory)
            player.inventory.remove(dropped)
        player.health = player.max_health
        pvee.end_battle(battle)

        penalty_bits = [f"Lost {gold_lost}g"]
        if dropped:
            penalty_bits.append(f"Dropped {dropped}")
        embed = style.error(
            f"{player.name} slain by {battle.enemy.name}.",
            "Revived in the Village.",
        )
        style.add_fields(embed, [
            ("Penalty", " • ".join(penalty_bits), False),
            ("HP",      f"{player.health}/{player.max_health}", True),
        ])
        await send(embed=embed)


async def setup(bot):
    await bot.add_cog(Combat())
