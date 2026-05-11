from discord.ext import commands

from ..services import players
from ..world import items, zones, lootboxes, weapons as weapons_module, weapon_skills as ws_module
from .. import style
from ._helpers import inventory_str, item_label, require_village, block_during_battle


class Inventory(commands.Cog):
    @commands.command(name="equip")
    async def equip(self, ctx, item_id: str = None):
        if item_id is None:
            await ctx.send("Usage: `!equip <item_id>`.")
            return
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        item_id = item_id.lower()
        item = items.get(item_id)
        if item is None or item_id not in player.inventory:
            await ctx.send(f"You don't have `{item_id}`.")
            return
        if item.type not in ("weapon", "armor", "pickaxe", "fishing_rod"):
            await ctx.send(f"{item.name} isn't equippable.")
            return

        missing = items.missing_requirements(item, player)
        if missing:
            await ctx.send(f"**{item.name}** requires {', '.join(missing)}.")
            return

        player.inventory.remove(item_id)
        if item.type == "weapon":
            if player.equipped_weapon:
                old = items.get(player.equipped_weapon)
                player.damage -= old.damage_bonus
                player.inventory.append(player.equipped_weapon)
            player.equipped_weapon = item_id
            player.damage += item.damage_bonus
            await ctx.send(f"Equipped **{item.name}** (+{item.damage_bonus} damage). Damage now {player.damage}.")
        elif item.type == "armor":
            if player.equipped_armor:
                player.inventory.append(player.equipped_armor)
            player.equipped_armor = item_id
            await ctx.send(f"Equipped **{item.name}** ({item.defense} defense).")
        elif item.type == "pickaxe":
            if player.equipped_pickaxe:
                player.inventory.append(player.equipped_pickaxe)
            player.equipped_pickaxe = item_id
            await ctx.send(f"Equipped **{item.name}** (pickaxe).")
        else:  # fishing_rod
            if player.equipped_fishing_rod:
                player.inventory.append(player.equipped_fishing_rod)
            player.equipped_fishing_rod = item_id
            await ctx.send(f"Equipped **{item.name}** (fishing rod).")

    @commands.command(name="unequip")
    async def unequip(self, ctx, slot: str = None):
        valid_slots = ("weapon", "armor", "pickaxe", "fishing_rod")
        if slot not in valid_slots:
            await ctx.send("Usage: `!unequip weapon`, `armor`, `pickaxe`, or `fishing_rod`.")
            return
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        if slot == "weapon":
            if not player.equipped_weapon:
                await ctx.send("No weapon equipped.")
                return
            item = items.get(player.equipped_weapon)
            player.damage -= item.damage_bonus
            player.inventory.append(player.equipped_weapon)
            player.equipped_weapon = None
            await ctx.send(f"Unequipped **{item.name}**. Damage now {player.damage}.")
        elif slot == "armor":
            if not player.equipped_armor:
                await ctx.send("No armor equipped.")
                return
            item = items.get(player.equipped_armor)
            player.inventory.append(player.equipped_armor)
            player.equipped_armor = None
            await ctx.send(f"Unequipped **{item.name}**.")
        elif slot == "pickaxe":
            if not player.equipped_pickaxe:
                await ctx.send("No pickaxe equipped.")
                return
            item = items.get(player.equipped_pickaxe)
            player.inventory.append(player.equipped_pickaxe)
            player.equipped_pickaxe = None
            await ctx.send(f"Unequipped **{item.name}**.")
        else:  # fishing_rod
            if not player.equipped_fishing_rod:
                await ctx.send("No fishing rod equipped.")
                return
            item = items.get(player.equipped_fishing_rod)
            player.inventory.append(player.equipped_fishing_rod)
            player.equipped_fishing_rod = None
            await ctx.send(f"Unequipped **{item.name}**.")

    @commands.command(name="use")
    async def use(self, ctx, item_id: str = None):
        if item_id is None:
            await ctx.send("Usage: `!use <item_id>` (consumables only).")
            return
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        item_id = item_id.lower()
        item = items.get(item_id)
        if item is None or item_id not in player.inventory:
            await ctx.send(f"You don't have `{item_id}`.")
            return
        if item.type != "consumable":
            await ctx.send(f"{item.name} isn't a consumable.")
            return

        missing = items.missing_requirements(item, player)
        if missing:
            await ctx.send(f"**{item.name}** requires {', '.join(missing)}.")
            return

        player.inventory.remove(item_id)
        if item.heal:
            before = player.health
            player.health = min(player.max_health, player.health + item.heal)
            await ctx.send(f"Used {item.name}. Healed {player.health - before} HP. ({player.health}/{player.max_health})")

    @commands.command(name="inspect")
    async def inspect(self, ctx, item_id: str = None):
        if item_id is None:
            await ctx.send(embed=style.error(
                "`!inspect` needs an item.",
                "Usage: `!inspect <item_id>`."
            ))
            return
        item = items.get(item_id)
        if item is None:
            await ctx.send(embed=style.error(f"No item `{item_id}`."))
            return

        embed = style.lookup(item.name, description=item.description,
                             footer_context=f"Type: {item.type}")
        stat_bits = []
        if item.damage_bonus: stat_bits.append(f"+{item.damage_bonus} dmg")
        if item.defense:      stat_bits.append(f"{item.defense} def")
        if item.heal:         stat_bits.append(f"+{item.heal} HP")
        fields = [("Sell Value", f"{item.value}g", True)]
        if stat_bits:
            fields.append(("Stats", " • ".join(stat_bits), True))
        if item.requirements:
            reqs = ", ".join(f"{s.title()} L{l}" for s, l in item.requirements.items())
            fields.append(("Requires", reqs, False))

        # Weapon attacks
        if item.type == "weapon":
            weapon = weapons_module.get(item_id)
            if weapon and weapon.attacks:
                for atk in weapon.attacks:
                    thb = f"+{atk.to_hit_bonus}" if atk.to_hit_bonus >= 0 else str(atk.to_hit_bonus)
                    atk_line = f"`{atk.damage_die}+{atk.damage_bonus}` dmg • {thb} to hit • {atk.poise_break} poise break"
                    fields.append((f"Attack: {atk.name}", atk_line, False))

        # Weapon skill attack
        if item.type == "weapon_skill":
            skill = ws_module.get(item_id)
            if skill:
                atk = skill.attack
                thb = f"+{atk.to_hit_bonus}" if atk.to_hit_bonus >= 0 else str(atk.to_hit_bonus)
                atk_line = f"`{atk.damage_die}+{atk.damage_bonus}` dmg • {thb} to hit • {atk.poise_break} poise break"
                fields.append((f"Grants: {atk.name}", atk_line, False))

        style.add_fields(embed, fields)
        await ctx.send(embed=embed)

    @commands.command(name="inv", aliases=["inventory", "bag"])
    async def inv(self, ctx):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        weapon  = item_label(player.equipped_weapon)      if player.equipped_weapon      else "none"
        armor   = item_label(player.equipped_armor)       if player.equipped_armor       else "none"
        pickaxe = item_label(player.equipped_pickaxe)     if player.equipped_pickaxe     else "none"
        rod     = item_label(player.equipped_fishing_rod) if player.equipped_fishing_rod else "none"
        equipped = (
            f"Weapon: {weapon} • Armor: {armor}\n"
            f"Pickaxe: {pickaxe} • Rod: {rod}"
        )
        embed = style.lookup(f"{player.name}'s Inventory",
                             footer_context=f"Requested by {ctx.author.display_name}")
        style.add_fields(embed, [
            ("Equipped", equipped, False),
            ("Gold", f"{player.gold}g", True),
            ("Items", inventory_str(player), False),
        ])
        await ctx.send(embed=embed)

    @commands.command(name="rest")
    async def rest(self, ctx):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        if not require_village(player):
            await ctx.send(embed=style.error(
                "Resting requires the Village.",
                "Use `!warp village` to return."
            ))
            return
        if player.health == player.max_health:
            await ctx.send(embed=style.info(
                "Already at full health.",
                f"HP {player.health}/{player.max_health}."
            ))
            return
        healed = player.max_health - player.health
        player.health = player.max_health
        await ctx.send(embed=style.success(
            f"{player.name} rests at the inn.",
            f"Recovered {healed} HP. Now at {player.health}/{player.max_health}."
        ))

    @commands.command(name="me")
    async def me(self, ctx):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        zone = zones.world.get((player.x, player.y))
        where = f"{zone.name} ({player.x},{player.y})" if zone else f"({player.x},{player.y}) — unknown"
        next_xp = player.xp_to_next_level()
        weapon  = item_label(player.equipped_weapon)      if player.equipped_weapon      else "none"
        armor   = item_label(player.equipped_armor)       if player.equipped_armor       else "none"
        pickaxe = item_label(player.equipped_pickaxe)     if player.equipped_pickaxe     else "none"
        rod     = item_label(player.equipped_fishing_rod) if player.equipped_fishing_rod else "none"

        embed = style.lookup(f"{player.name} — L{player.level}",
                             description=f"Location: {where}",
                             footer_context=f"Requested by {ctx.author.display_name}")
        vitals = f"HP {player.health}/{player.max_health} • XP {player.xp}/{next_xp} • DMG {player.damage}"
        gear   = (
            f"Weapon: {weapon} • Armor: {armor}\n"
            f"Pickaxe: {pickaxe} • Rod: {rod}"
        )
        style.add_fields(embed, [
            ("Vitals",    vitals, False),
            ("Equipment", gear, False),
            ("Gold",      f"{player.gold}g", True),
            ("Inventory", inventory_str(player), False),
        ])
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Inventory())
