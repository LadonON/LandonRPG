from collections import Counter
from discord.ext import commands

from ..services import players, shop
from ..world import items
from .. import style
from ._helpers import inventory_str, item_label, require_village


def _not_in_village_embed():
    return style.error(
        "No shop here.",
        "Warp to the village: `!warp village`."
    )


class Shop(commands.Cog):
    @commands.command(name="sell")
    async def sell(self, ctx, *args: str):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        if not args:
            catalog = ", ".join(f"{i.name} ({i.value}g)" for i in items.ITEMS.values() if i.value > 0)
            embed = style.info(
                "Sell command usage",
                "`!sell all` or `!sell <item_id> [item_id ...]`."
            )
            style.add_fields(embed, [("Shop Buys", catalog or "—", False)])
            await ctx.send(embed=embed)
            return

        if require_village(player) is None:
            await ctx.send(embed=_not_in_village_embed())
            return

        if len(args) == 1 and args[0].lower() == "all":
            sold = shop.sell_all(player)
            missing = []
        else:
            sold, missing = shop.sell_items(player, list(args))

        if not sold:
            await ctx.send(embed=style.warning(
                "Nothing sold.",
                f"Inventory: {inventory_str(player)}"
            ))
            return

        c = Counter(item_id for item_id, _ in sold)
        total = sum(g for _, g in sold)
        items_sold = ", ".join(f"{item_label(n)} x{q}" for n, q in c.items())
        embed = style.success(f"Sold for {total}g",
                              footer_context=f"Sold by {ctx.author.display_name}")
        fields = [
            ("Items", items_sold, False),
            ("Gold",  f"{player.gold}g", True),
        ]
        if missing:
            fields.append(("Couldn't Sell", ", ".join(missing), False))
        style.add_fields(embed, fields)
        await ctx.send(embed=embed)

    @commands.command(name="shop")
    async def shop_cmd(self, ctx):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        if require_village(player) is None:
            await ctx.send(embed=_not_in_village_embed())
            return

        lines = []
        for item_id in shop.SHOP_INVENTORY:
            it = items.get(item_id)
            lines.append(f"`{item_id}` — {it.name} ({shop.buy_price(item_id)}g)\n  {it.description}")
        embed = style.lookup("Village Shop",
                             description="`!buy <item_id>` to purchase.",
                             footer_context=f"Your gold: {player.gold}g")
        style.add_fields(embed, [("Stock", "\n\n".join(lines) or "—", False)])
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy_cmd(self, ctx, item_id: str = None):
        if item_id is None:
            await ctx.send(embed=style.error(
                "`!buy` needs an item.",
                "Usage: `!buy <item_id>`. See `!shop` for stock."
            ))
            return
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        if require_village(player) is None:
            await ctx.send(embed=_not_in_village_embed())
            return
        ok, msg = shop.buy(player, item_id)
        if not ok:
            await ctx.send(embed=style.error(msg))
            return
        embed = style.success(msg, footer_context=f"Buyer: {ctx.author.display_name}")
        style.add_fields(embed, [
            ("Gold", f"{player.gold}g", True),
            ("Inventory", inventory_str(player), False),
        ])
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Shop())
