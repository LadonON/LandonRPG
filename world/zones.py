from ..models.zone import Zone, MonsterSpawn, ForageDrop, FishingCatch

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
        zone_id="forest", name="Whispering Forest",
        description="Sun-dappled woodland on the edge of civilization.",
        difficulty=1,
        spawn_table=[
            MonsterSpawn("young_orc", level=1), MonsterSpawn("forest_wolf", level=1),
            MonsterSpawn("forest_skeleton", level=1), MonsterSpawn("giant_spider", level=1),
        ],
        forage_table=[
            ForageDrop("blueberry_seed", weight=3),
            ForageDrop("herb_seed",      weight=3),
            ForageDrop("sunpetal_seed",  weight=2),
        ],
        fishing_pool=[
            FishingCatch("river_minnow", weight=6),
            FishingCatch("bluegill",     weight=3),
            FishingCatch("forest_perch", weight=1),
        ],
    ),
    (1, 0): Zone(
        zone_id="cave", name="Damp Cave",
        description="Wet limestone tunnels. The first mining zone.",
        difficulty=5,
        spawn_table=[
            MonsterSpawn("cave_orc", level=1), MonsterSpawn("cave_skeleton", level=1),
            MonsterSpawn("bat_swarm", level=1), MonsterSpawn("kobold_miner", level=1),
        ],
        min_combat_level=3,
        forage_table=[
            ForageDrop("herb_seed",         weight=3),
            ForageDrop("moonflower_seed",   weight=1),
            ForageDrop("glowmushroom_seed", weight=1),
        ],
        mining_resources=("stone", "copper_ore", "tin_ore", "iron_ore",
                          "flint", "chalk", "quartz", "clay",
                          "pyrite", "magnetite", "graphite", "amber",
                          "malachite", "azurite", "jade", "hematite"),
        fishing_pool=[
            FishingCatch("blind_eel",    weight=6),
            FishingCatch("glow_shrimp",  weight=3),
            FishingCatch("cave_grouper", weight=1),
        ],
    ),
    (0, 2): Zone(
        zone_id="meadow", name="Sunlit Meadow",
        description="Open grassland and wildflower fields.",
        difficulty=2,
        spawn_table=[
            MonsterSpawn("meadow_orc", level=1), MonsterSpawn("honey_drake", level=1),
            MonsterSpawn("pollen_wisp", level=1),
        ],
        min_foraging_level=2,
        forage_table=[
            ForageDrop("sunpetal_seed", weight=4),
            ForageDrop("pumpkin_seed",  weight=3),
            ForageDrop("corn_seed",     weight=2),
            ForageDrop("carrot_seed",   weight=2),
        ],
        fishing_pool=[
            FishingCatch("sunfish",     weight=5),
            FishingCatch("golden_carp", weight=3),
            FishingCatch("meadow_eel",  weight=2),
        ],
    ),
    (1, 1): Zone(
        zone_id="swamp", name="Murk Swamp",
        description="Bog, rot, and old magic. All four gathering loops are present.",
        difficulty=6,
        spawn_table=[
            MonsterSpawn("swamp_skeleton", level=1), MonsterSpawn("bog_orc", level=1),
            MonsterSpawn("mire_serpent", level=1), MonsterSpawn("will_o_wisp", level=1),
            MonsterSpawn("gator_brute", level=1),
        ],
        min_combat_level=5,
        min_foraging_level=4,
        forage_table=[
            ForageDrop("mandrake_seed",     weight=3),
            ForageDrop("moonflower_seed",   weight=2),
            ForageDrop("glowmushroom_seed", weight=2),
            ForageDrop("foxglove_seed",     weight=1),
        ],
        mining_resources=("stone", "iron_ore", "coal", "gold_ore", "mythril_chunk",
                          "moonsilver", "bloodstone", "petrified_wood", "galena"),
        fishing_pool=[
            FishingCatch("mudpike",    weight=4),
            FishingCatch("bog_leech",  weight=3),
            FishingCatch("glowfin",    weight=2),
            FishingCatch("swamp_pike", weight=1),
        ],
    ),
    # ── Tier 5 ──────────────────────────────────────────────────────────────
    (2, 1): Zone(
        zone_id="ashfall", name="Ashfall Plateau",
        description="Scorched volcanic flats, slow-flowing lava channels, basalt columns.",
        difficulty=10,
        spawn_table=[
            MonsterSpawn("cinder_imp", level=1), MonsterSpawn("ash_walker", level=1),
            MonsterSpawn("molten_golem", level=1), MonsterSpawn("salamander_lord", level=1),
            MonsterSpawn("pyre_orc", level=1),
        ],
        min_combat_level=10,
        min_mining_level=6,
        forage_table=[
            ForageDrop("ashpetal_seed",  weight=3),
            ForageDrop("dragonweed_seed", weight=2),
        ],
        mining_resources=("obsidian", "volcanic_shard", "sulfur_chunk", "cobalt_ore",
                          "cinnabar", "basalt_shard", "pumice", "magnesium_ore"),
        fishing_pool=[
            FishingCatch("magmacarp", weight=7),
            FishingCatch("ashfin",    weight=3),
        ],
    ),
    # ── Tier 6 ──────────────────────────────────────────────────────────────
    (2, 2): Zone(
        zone_id="frostbound", name="Frostbound Peaks",
        description="Glaciated mountain spine. Wind, ice caves, snow-buried ruins.",
        difficulty=14,
        spawn_table=[
            MonsterSpawn("frost_wolf", level=1), MonsterSpawn("ice_revenant", level=1),
            MonsterSpawn("yeti_brute", level=1), MonsterSpawn("snow_witch", level=1),
            MonsterSpawn("glacial_drake", level=1),
        ],
        min_combat_level=14,
        min_foraging_level=10,
        forage_table=[
            ForageDrop("frostberry_seed", weight=3),
            ForageDrop("icebloom_seed",   weight=2),
            ForageDrop("mooncress_seed",  weight=2),
            ForageDrop("silverleaf_seed", weight=1),
        ],
        mining_resources=("frostsilver", "iceshard", "glacial_crystal", "silver_ore",
                          "tundra_iron", "permafrost_shard", "aurora_dust", "white_sapphire"),
        fishing_pool=[
            FishingCatch("ice_salmon",    weight=5),
            FishingCatch("glacier_trout", weight=4),
            FishingCatch("frozen_pike",   weight=1),
        ],
    ),
    # ── Tier 7 ──────────────────────────────────────────────────────────────
    (3, 1): Zone(
        zone_id="tidewreck", name="Tidewreck Reef",
        description="Half-submerged shipwrecks, coral spires, abyss trenches.",
        difficulty=18,
        spawn_table=[
            MonsterSpawn("reef_drowner", level=1), MonsterSpawn("siren_thrall", level=1),
            MonsterSpawn("tide_skeleton", level=1), MonsterSpawn("shark_brood", level=1),
            MonsterSpawn("kraken_hatchling", level=1),
        ],
        min_combat_level=18,
        min_fishing_level=10,
        forage_table=[
            ForageDrop("kelp_seed",  weight=3),
            ForageDrop("coral_seed", weight=1),
        ],
        mining_resources=("pearl_coral", "seabed_quartz", "abyssal_stone", "salt_crystal",
                          "black_pearl", "sea_glass", "deep_iron", "phosphorite"),
        fishing_pool=[
            FishingCatch("deepsquid",  weight=4),
            FishingCatch("anglerfish", weight=3),
            FishingCatch("kraken_spawn", weight=2),
            FishingCatch("sunken_relic", weight=1),
        ],
    ),
    # ── Tier 8 ──────────────────────────────────────────────────────────────
    (3, 2): Zone(
        zone_id="hollow", name="Hollow Marches",
        description="Cursed plains and bone forests. Where dead kings dream.",
        difficulty=22,
        spawn_table=[
            MonsterSpawn("hollow_knight", level=1), MonsterSpawn("wraith", level=1),
            MonsterSpawn("bone_collector", level=1), MonsterSpawn("grave_orc", level=1),
            MonsterSpawn("lich_acolyte", level=1),
        ],
        min_combat_level=22,
        min_foraging_level=16,
        forage_table=[
            ForageDrop("bonebloom_seed",  weight=3),
            ForageDrop("soulroot_seed",   weight=2),
            ForageDrop("shadowmoss_seed", weight=2),
            ForageDrop("nightshade_seed", weight=1),
        ],
        mining_resources=("soulstone", "bonemarble", "shadowsteel", "cursed_iron",
                          "void_crystal", "grave_iron", "necrotic_shard", "hex_stone"),
        fishing_pool=[
            FishingCatch("bonefish",     weight=6),
            FishingCatch("cursed_catch", weight=3),
            FishingCatch("spectralfin",  weight=1),
        ],
    ),
    # ── Tier 9 ──────────────────────────────────────────────────────────────
    (4, 2): Zone(
        zone_id="stormvault", name="Stormvault Citadel",
        description="Sky-fortress wrapped in perpetual storm. Tesla-coil corridors.",
        difficulty=28,
        spawn_table=[
            MonsterSpawn("storm_sentinel", level=1), MonsterSpawn("thunderkin", level=1),
            MonsterSpawn("arc_construct", level=1), MonsterSpawn("storm_giant", level=1),
        ],
        min_combat_level=28,
        min_mining_level=22,
        forage_table=[
            ForageDrop("stormvine_seed",  weight=3),
            ForageDrop("voltflower_seed", weight=2),
        ],
        mining_resources=("stormsteel", "voltite", "skyiron", "adamantite",
                          "thunder_crystal", "storm_glass", "charged_iron", "plasma_core"),
        fishing_pool=[
            FishingCatch("voltcatfish", weight=10),
        ],
    ),
    # ── Tier 10 ─────────────────────────────────────────────────────────────
    (4, 3): Zone(
        zone_id="skyforge", name="Skyforge Crucible",
        description="A forge between worlds. Where gods anneal reality.",
        difficulty=36,
        spawn_table=[
            MonsterSpawn("crucible_warden", level=1), MonsterSpawn("star_revenant", level=1),
            MonsterSpawn("void_herald", level=1), MonsterSpawn("forgewraith", level=1),
        ],
        min_combat_level=36,
        forage_table=[
            ForageDrop("starbloom_seed",      weight=3),
            ForageDrop("godsblood_seed",      weight=2),
            ForageDrop("celestial_lily_seed", weight=1),
        ],
        mining_resources=("celestium", "stardust", "voidstone", "sunstone", "moonstone", "aether_crystal",
                          "void_iron", "nebula_dust", "cosmic_shard", "primordial_ore"),
        fishing_pool=[
            FishingCatch("starwhale", weight=10),
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
