from collections import Counter
from discord.ext import commands
from ..world import items, zones, seeds as seed_catalog, resources as resource_catalog
from ..world import dungeons as dungeon_world
from ..services import shop
from ..pvp import engine as pvp_engine
from ..pve import engine as pve_engine
from ..dungeon import engine as dungeon_engine
from .. import style


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


def _seed_label(seed_id: str) -> str:
    seed = seed_catalog.get(seed_id)
    return seed.seed_name if seed else seed_id


def _resource_label_with_chance(resource_id: str) -> str:
    r = resource_catalog.get(resource_id)
    if r is None:
        return resource_id
    return f"{r.name} ({r.drop_chance}%)"


def _monster_line(zone) -> str:
    if not zone.spawn_table:
        return "None — peaceful."
    return ", ".join(f"{s.monster_id} (L{s.level})" for s in zone.spawn_table)


def _foraging_line(zone) -> str:
    if not zone.forage_table:
        return "—"
    return ", ".join(f"{_seed_label(d.seed_id)} (w{d.weight})" for d in zone.forage_table)


def _mining_line(zone) -> str:
    if not zone.mining_resources:
        return "—"
    return ", ".join(_resource_label_with_chance(r) for r in zone.mining_resources)


def _fishing_line(zone) -> str:
    if not zone.fishing_pool:
        return "—"
    return ", ".join(
        f"{item_label(c.item_id)} (w{c.weight})" for c in zone.fishing_pool
    )


def _dungeon_line(zone) -> str:
    cfg = dungeon_world.get(zone.zone_id)
    if cfg is None:
        return "—"
    # Default Normal scaling preview: monster level ≈ zone.difficulty.
    monster_level = max(1, zone.difficulty)
    return (
        f"**{cfg.name}** — {len(cfg.rooms)} room(s), boss `{cfg.boss_id}`.\n"
        f"Base monster level ≈ {monster_level} (scales with difficulty)."
    )


def _gates_line(zone) -> str:
    bits = []
    if zone.min_combat_level > 1:
        bits.append(f"Combat L{zone.min_combat_level}")
    if zone.min_foraging_level > 1:
        bits.append(f"Foraging L{zone.min_foraging_level}")
    if zone.min_farming_level > 1:
        bits.append(f"Farming L{zone.min_farming_level}")
    return ", ".join(bits) if bits else "None"


def zone_summary(zone):
    """Build a rich Discord embed describing the zone's activities."""
    embed = style.lookup(
        zone.name,
        description=zone.description,
        footer_context=f"Zone: {zone.zone_id} • Difficulty {zone.difficulty}",
    )
    monsters = _monster_line(zone)
    foraging = _foraging_line(zone)
    mining   = _mining_line(zone)
    fishing  = _fishing_line(zone)
    dungeon  = _dungeon_line(zone)
    gates    = _gates_line(zone)

    # Combine the gathering trio into one field so the panel fits within
    # the 4-field-on-first-paint rule.
    gathering = (
        f"**Forage** — {foraging}\n"
        f"**Mine**   — {mining}\n"
        f"**Fish**   — {fishing}"
    )
    style.add_fields(embed, [
        ("Monsters",  monsters,  False),
        ("Gathering", gathering, False),
        ("Dungeon",   dungeon,   False),
        ("Access",    gates,     True),
    ])
    return embed
