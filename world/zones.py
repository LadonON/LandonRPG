from ..models.zone import Zone, MonsterSpawn, ForageDrop

# Persistent world: (x, y) -> Zone.
world: dict[tuple[int, int], Zone] = {
    (0, 0): Zone(
        zone_id="village", name="Village",
        description="A small cozy haven",
        difficulty=0,
        spawn_table=[],
        forage_table=[],           # no foraging in the village
    ),
    (0, 1): Zone(
        zone_id="forest", name="Forest",
        description="Large trees surround you",
        difficulty=1,
        spawn_table=[MonsterSpawn("orc", level=1), MonsterSpawn("skeleton", level=1)],
        forage_table=[
            ForageDrop("corn_seed",      weight=4),
            ForageDrop("wheat_seed",     weight=4),
            ForageDrop("blueberry_seed", weight=2),
            ForageDrop("herb_seed",      weight=1),
        ],
    ),
    (1, 0): Zone(
        zone_id="cave", name="Damp Cave",
        description="Dripping water echoes in the dark.",
        difficulty=5,
        spawn_table=[MonsterSpawn("orc", level=15), MonsterSpawn("skeleton", level=10)],
        min_combat_level=3,
        forage_table=[
            ForageDrop("herb_seed",        weight=3),
            ForageDrop("moonflower_seed",  weight=1),
            ForageDrop("glowmushroom_seed", weight=1),
        ],
    ),
    (0, 2): Zone(
        zone_id="meadow", name="Sunlit Meadow",
        description="Tall grass sways under a warm sun, dotted with bright flowers.",
        difficulty=2,
        spawn_table=[MonsterSpawn("orc", level=2)],
        min_foraging_level=2,
        forage_table=[
            ForageDrop("sunpetal_seed",  weight=4),
            ForageDrop("blueberry_seed", weight=3),
            ForageDrop("herb_seed",      weight=2),
            ForageDrop("pumpkin_seed",   weight=1),
        ],
    ),
    (1, 1): Zone(
        zone_id="swamp", name="Murk Swamp",
        description="Thick mist clings to crooked trees and bubbling pools.",
        difficulty=6,
        spawn_table=[MonsterSpawn("skeleton", level=12), MonsterSpawn("orc", level=8)],
        min_combat_level=5,
        min_foraging_level=4,
        forage_table=[
            ForageDrop("herb_seed",         weight=3),
            ForageDrop("glowmushroom_seed", weight=2),
            ForageDrop("pumpkin_seed",      weight=2),
            ForageDrop("moonflower_seed",   weight=1),
        ],
    ),
}


def find_by_name(name: str) -> tuple[int, int] | None:
    """Locate a zone by case-insensitive name or zone_id. Returns (x,y) or None."""
    needle = name.lower()
    for coords, z in world.items():
        if z.name.lower() == needle or z.zone_id.lower() == needle:
            return coords
    return None
