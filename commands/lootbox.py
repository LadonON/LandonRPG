"""Lootbox command group.

  !lootbox                  — list unopened lootboxes you own
  !lootbox open <rarity>    — open one of that rarity
  !lootbox inspect <rarity> — preview the loot pool weights
"""
from collections import Counter

from discord.ext import commands

from ..services import players
from ..world import lootboxes, items
from .. import style
from ._helpers import block_during_battle, item_label


class Lootbox(commands.Cog):

    @commands.group(name="lootbox", invoke_without_command=True)
    @block_during_battle()
    async def lootbox(self, ctx):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        counts = Counter(i for i in player.inventory if i.startswith("lootbox_"))
        if not counts:
            await ctx.send(embed=style.info(
                "No lootboxes in inventory.",
                "Clear dungeon rooms or finish quests to earn them."
            ))
            return

        rows = []
        for rarity in lootboxes.RARITIES:
            box_id = lootboxes.lootbox_item_id(rarity)
            n = counts.get(box_id, 0)
            if n:
                rows.append(f"**{rarity.title()}** — `{n}` (open: `!lootbox open {rarity}`)")
        embed = style.lookup(
            "Your Lootboxes",
            description=f"Total: {sum(counts.values())}",
            footer_context=f"Requested by {ctx.author.display_name}",
        )
        style.add_fields(embed, [("Owned", "\n".join(rows), False)])
        await ctx.send(embed=embed)

    @lootbox.command(name="open")
    @block_during_battle()
    async def lootbox_open(self, ctx, rarity: str = None):
        if rarity is None:
            await ctx.send(embed=style.error(
                "`!lootbox open` needs a rarity.",
                f"Usage: `!lootbox open <rarity>`. Rarities: {', '.join(lootboxes.RARITIES)}."
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
                "Earn one by clearing a dungeon room or finishing a quest."
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

    @lootbox.command(name="inspect")
    async def lootbox_inspect(self, ctx, rarity: str = None):
        if rarity is None:
            await ctx.send(embed=style.error(
                "`!lootbox inspect` needs a rarity.",
                f"Usage: `!lootbox inspect <rarity>`. Rarities: {', '.join(lootboxes.RARITIES)}."
            ))
            return
        rarity = rarity.lower()
        pool = lootboxes.POOLS.get(rarity)
        if pool is None:
            await ctx.send(embed=style.error(f"Unknown rarity `{rarity}`."))
            return

        total_w = sum(e["weight"] for e in pool.weighted_items) or 1
        rows = []
        for entry in pool.weighted_items:
            pct = entry["weight"] * 100 / total_w
            label = item_label(entry["item"])
            amt = entry["amount"]
            rows.append(f"`{entry['item']}` ({label}) x{amt[0]}-{amt[1]} — {pct:.1f}%")

        embed = style.lookup(
            f"{rarity.title()} Lootbox pool",
            description=f"{pool.pulls} pulls per box • {pool.gold_range[0]}-{pool.gold_range[1]}g",
            footer_context="Pool percentages are fixed.",
        )
        style.add_fields(embed, [("Loot", "\n".join(rows), False)])
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Lootbox())
