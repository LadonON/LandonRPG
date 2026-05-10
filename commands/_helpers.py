from collections import Counter
from discord.ext import commands
from ..world import items, zones
from ..services import shop
from ..pvp import engine as pvp_engine
from ..pve import engine as pve_engine
from ..dungeon import engine as dungeon_engine


def block_during_battle():
    """Decorator: command fails with a friendly message if the invoker is in
    any battle (PVP arena, PvE encounter, or dungeon run)."""
    async def predicate(ctx):
        if pvp_engine.in_battle(ctx.author.id):
            await ctx.send(
                "You can't use that command during a PVP battle. "
                "Use `!pvp arena forfeit` to surrender."
            )
            return False
        if pve_engine.in_battle(ctx.author.id):
            await ctx.send(
                "You can't use that command during a PvE encounter. "
                "Use `!pve arena flee` to retreat."
            )
            return False
        if dungeon_engine.in_dungeon(ctx.author.id):
            await ctx.send(
                "You can't use that command during a dungeon run. "
                "Use `!dungeon abandon` to leave."
            )
            return False
        return True
    return commands.check(predicate)


# Backwards-compatible alias used by existing commands.
block_during_pvp = block_during_battle


def item_label(item_id: str) -> str:
    item = items.get(item_id)
    return item.name if item else item_id


def inventory_str(player) -> str:
    if not player.inventory:
        return "empty"
    return ", ".join(f"{item_label(n)} x{q}" for n, q in Counter(player.inventory).items())


def require_village(player):
    zone = zones.world.get((player.x, player.y))
    if zone is None or zone.zone_id != shop.SHOP_ZONE:
        return None
    return zone


def zone_summary(zone) -> str:
    if not zone.spawn_table:
        mob_line = "Monsters: none — peaceful."
    else:
        mob_line = "Monsters: " + ", ".join(f"{s.monster_id} (L{s.level})" for s in zone.spawn_table)
    return f"**{zone.name}** — {zone.description}\n{mob_line}"
