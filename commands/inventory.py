from discord.ext import commands

from ..services import players
from ..world import items, zones, lootboxes
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
        if item.type not in ("weapon", "armor"):
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
        else:
            if player.equipped_armor:
                player.inventory.append(player.equipped_armor)
            player.equipped_armor = item_id
            await ctx.send(f"Equipped **{item.name}** ({item.defense} defense).")

    @commands.command(name="unequip")
    async def unequip(self, ctx, slot: str = None):
        if slot not in ("weapon", "armor"):
            await ctx.send("Usage: `!unequip weapon` or `!unequip armor`.")
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
        else:
            if not player.equipped_armor:
                await ctx.send("No armor equipped.")
                return
            item = items.get(player.equipped_armor)
            player.inventory.append(player.equipped_armor)
            player.equipped_armor = None
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

    @commands.command(name="open")
    @block_during_battle()
    async def open_lootbox(self, ctx, rarity: str = None):
        """Open a lootbox of the given rarity from inventory."""
        if rarity is None:
            await ctx.send(embed=style.error(
                "`!open` needs a rarity.",
                f"Usage: `!open <rarity>`. Rarities: {', '.join(lootboxes.RARITIES)}."
            ))
            return
        rarity = rarity.lower()
        if rarity not in lootboxes.RARITIES:
            await ctx.send(embed=style.error(
                f"Unknown rarity `{rarity}`.",
                f"Pick one of: {', '.join(lootboxes.RARITIES)}."
            ))
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        box_id = lootboxes.lootbox_item_id(rarity)
        if box_id not in player.inventory:
            await ctx.send(embed=style.error(
                f"No {rarity.title()} Lootbox in inventory.",
                "Earn one by clearing a dungeon room."
            ))
            return

        result = lootboxes.open_box(rarity)
        if result is None:
            await ctx.send(embed=style.error(f"No loot pool defined for `{rarity}`."))
            return

        player.inventory.remove(box_id)
        if result.gold:
            player.gold += result.gold
        for item_id, amount in result.items:
            for _ in range(amount):
                player.inventory.append(item_id)

        item_summary = ", ".join(
            f"{item_label(i)} x{a}" for i, a in result.items
        ) or "no items"
        embed = style.celebration(
            f"Opened {rarity.title()} Lootbox",
            footer_context=f"Opened by {ctx.author.display_name}",
        )
        style.add_fields(embed, [
            ("Gold", f"+{result.gold}g", True),
            ("Items", item_summary, False),
        ])
        await ctx.send(embed=embed)

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
        style.add_fields(embed, fields)
        await ctx.send(embed=embed)

    @commands.command(name="inv", aliases=["inventory", "bag"])
    async def inv(self, ctx):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        weapon = item_label(player.equipped_weapon) if player.equipped_weapon else "none"
        armor  = item_label(player.equipped_armor)  if player.equipped_armor  else "none"
        embed = style.lookup(f"{player.name}'s Inventory",
                             footer_context=f"Requested by {ctx.author.display_name}")
        style.add_fields(embed, [
            ("Weapon", weapon, True),
            ("Armor", armor, True),
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
        weapon = item_label(player.equipped_weapon) if player.equipped_weapon else "none"
        armor  = item_label(player.equipped_armor)  if player.equipped_armor  else "none"

        embed = style.lookup(f"{player.name} — L{player.level}",
                             description=f"Location: {where}",
                             footer_context=f"Requested by {ctx.author.display_name}")
        vitals = f"HP {player.health}/{player.max_health} • XP {player.xp}/{next_xp} • DMG {player.damage}"
        gear   = f"Weapon: {weapon} • Armor: {armor}"
        style.add_fields(embed, [
            ("Vitals",    vitals, False),
            ("Equipment", gear, False),
            ("Gold",      f"{player.gold}g", True),
            ("Inventory", inventory_str(player), False),
        ])
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Inventory())
