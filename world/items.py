from dataclasses import dataclass, field


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    description: str
    type: str            # "junk" | "weapon" | "armor" | "consumable"
    value: int = 0       # shop sell price
    damage_bonus: int = 0
    defense: int = 0
    heal: int = 0
    # Stat requirements to equip/use, e.g. {"combat": 3, "foraging": 2}.
    # Stat names match keys in world.stats.STATS.
    requirements: dict = field(default_factory=dict)


def missing_requirements(item: "Item", player) -> list[str]:
    """Return human-readable strings for any unmet requirements.

    Supported keys in `requirements`:
      - "level": player overall level
      - "<stat_name>": minimum stat level (e.g. "combat", "farming", "foraging")
    """
    from . import stats as stats_mod
    missing = []
    for key, req_lvl in (item.requirements or {}).items():
        if key == "level":
            cur = getattr(player, "level", 1)
            if cur < req_lvl:
                missing.append(f"Player Level {req_lvl} (you are L{cur})")
            continue
        cfg = stats_mod.get(key)
        if cfg is None:
            continue
        cur = getattr(player, cfg.level_attr, 1)
        if cur < req_lvl:
            missing.append(f"{key.title()} L{req_lvl} (you are L{cur})")
    return missing


ITEMS: dict[str, Item] = {
    # ── Junk (loot drops, sold for gold) ──
    "bone":  Item("bone",  "Bone",         "A sun-bleached fragment.",       "junk", value=2),
    "skull": Item("skull", "Skull",        "Empty eye sockets stare back.",  "junk", value=5),
    "tooth": Item("tooth", "Orc Tooth",    "Yellowed and chipped.",          "junk", value=8),
    "club_fragment": Item("club_fragment", "Club Fragment", "Splintered orc weapon.", "junk", value=3),
    # T1 new drops
    "wolf_pelt":    Item("wolf_pelt",    "Wolf Pelt",    "Thick grey fur.",                          "junk", value=6),
    "spider_silk":  Item("spider_silk",  "Spider Silk",  "Tough and sticky strands.",                "junk", value=7),
    "fang":         Item("fang",         "Fang",         "A curved fang.",                           "junk", value=5),
    # T2 new drops
    "drake_scale":   Item("drake_scale",   "Drake Scale",   "Iridescent scale from a drake.",        "junk", value=12),
    "honey_essence": Item("honey_essence", "Honey Essence", "Crystallized nectar from a drake hive.","junk", value=10),
    "glow_dust":     Item("glow_dust",     "Glow Dust",     "Faintly glowing powder.",               "junk", value=8),
    # T3 new drops
    "rusted_blade":     Item("rusted_blade",     "Rusted Blade",     "A corroded blade fragment.",           "junk", value=4),
    "bat_wing":         Item("bat_wing",         "Bat Wing",         "Leathery grey membrane.",              "junk", value=5),
    "pickaxe_fragment": Item("pickaxe_fragment", "Pickaxe Fragment", "A broken pickaxe head.",               "junk", value=6),
    # T4 new drops
    "swamp_essence": Item("swamp_essence", "Swamp Essence", "Thick dark liquid from swamp creatures.", "junk", value=10),
    "serpent_scale": Item("serpent_scale", "Serpent Scale", "Slippery iridescent scale.",              "junk", value=12),
    "venom_sac":     Item("venom_sac",     "Venom Sac",     "A sac full of potent venom.",            "junk", value=15),
    "soul_fragment": Item("soul_fragment", "Soul Fragment", "A flickering mote of trapped soul.",      "junk", value=20),
    "gator_hide":    Item("gator_hide",    "Gator Hide",    "Rough and waterproof skin.",              "junk", value=14),
    # T5 new drops
    "imp_horn":       Item("imp_horn",       "Imp Horn",       "A small twisted horn.",               "junk", value=18),
    "ash_dust":       Item("ash_dust",       "Ash Dust",       "Grey powder from creatures of flame.","junk", value=12),
    "molten_core":    Item("molten_core",    "Molten Core",    "A glowing chunk from a golem.",       "junk", value=30),
    "salamander_hide":Item("salamander_hide","Salamander Hide","Heat-resistant scaled hide.",         "junk", value=25),
    "fire_gland":     Item("fire_gland",     "Fire Gland",     "A fire-producing organ.",             "junk", value=22),
    "cinder_brand":   Item("cinder_brand",   "Cinder Brand",   "A smoldering brand from a pyre orc.","junk", value=16),
    # T6 new drops
    "frost_pelt":    Item("frost_pelt",    "Frost Pelt",    "Thick fur that resists ice.",            "junk", value=28),
    "revenant_dust": Item("revenant_dust", "Revenant Dust", "What a revenant leaves behind.",         "junk", value=22),
    "yeti_fur":      Item("yeti_fur",      "Yeti Fur",      "Massive clumps of dense white fur.",    "junk", value=30),
    "frost_bone":    Item("frost_bone",    "Frost Bone",    "Bone bleached white by permafrost.",     "junk", value=20),
    "hex_charm":     Item("hex_charm",     "Hex Charm",     "A cursed trinket from a snow witch.",    "junk", value=35),
    # T7 new drops
    "drowner_pearl": Item("drowner_pearl", "Drowner Pearl", "A dark pearl from a reef drowner.",      "junk", value=40),
    "siren_voice":   Item("siren_voice",   "Siren Voice",   "A crystallized siren call.",             "junk", value=45),
    "scale":         Item("scale",         "Scale",         "Generic fish-like scale.",               "junk", value=15),
    "shark_fang":    Item("shark_fang",    "Shark Fang",    "A serrated shark tooth.",                "junk", value=38),
    "shark_hide":    Item("shark_hide",    "Shark Hide",    "Rough abrasive hide.",                   "junk", value=35),
    "kraken_tendril":Item("kraken_tendril","Kraken Tendril","A severed tentacle.",                    "junk", value=50),
    # T8 new drops
    "knight_sigil":    Item("knight_sigil",    "Knight Sigil",    "A hollow knight's tarnished sigil.",   "junk", value=55),
    "lich_phylactery": Item("lich_phylactery", "Lich Phylactery", "The lich's source of power.",          "junk", value=70),
    "dark_tome":       Item("dark_tome",       "Dark Tome",       "Writings in an unknown tongue.",        "junk", value=60),
    # T9 new drops
    "sentinel_core": Item("sentinel_core", "Sentinel Core", "The power source of a storm sentinel.",  "junk", value=80),
    "lightning_rod":  Item("lightning_rod", "Lightning Rod",  "Sparking metal rod.",                  "junk", value=70),
    "arc_capacitor":  Item("arc_capacitor", "Arc Capacitor",  "Stores enormous electrical charge.",   "junk", value=90),
    "giant_femur":    Item("giant_femur",   "Giant Femur",    "Femur from a storm giant.",            "junk", value=75),
    # T10 new drops
    "warden_plate":  Item("warden_plate",  "Warden Plate",  "Celestial alloy armor plate.",           "junk", value=120),
    "herald_eye":    Item("herald_eye",    "Herald Eye",    "An unblinking eye from a void herald.",  "junk", value=110),
    "wraith_dust":   Item("wraith_dust",   "Wraith Dust",   "The remains of a forgewraith.",          "junk", value=100),
    "voidstone":     Item("voidstone",     "Voidstone",     "Stone from the between-worlds.",         "junk", value=150),
    "sunstone":      Item("sunstone",      "Sunstone",      "Stone suffused with solar energy.",      "junk", value=160),
    "moonstone":     Item("moonstone",     "Moonstone",     "Stone that glows with pale moonlight.",  "junk", value=155),
    # ── Boss-drop unique items ──────────────────────────────────────────────
    "hollow_charm":    Item("hollow_charm",    "Hollow Charm",    "A charm imbued with forest magic.",         "junk", value=50),
    "royal_jelly":     Item("royal_jelly",     "Royal Jelly",     "Golden jelly from the hive queen.",         "junk", value=80),
    "troll_heart":     Item("troll_heart",     "Troll Heart",     "The still-beating heart of a troll.",       "junk", value=120),
    "bogfather_heart": Item("bogfather_heart", "Bogfather Heart", "Dark organ pulsing with bog magic.",         "junk", value=200),
    "sundering_core":  Item("sundering_core",  "Sundering Core",  "A shard of volcanic destruction.",          "junk", value=300),
    "frostfang":       Item("frostfang",       "Frostfang",       "A fang sharp enough to freeze.",            "junk", value=400),
    "krakora_eye":     Item("krakora_eye",     "Krakora's Eye",   "A vast compound eye from Krakora.",         "junk", value=500),
    "crown_shard":     Item("crown_shard",     "Crown Shard",     "A fragment of the Hollowed King's crown.",  "junk", value=700),
    "storm_crown":     Item("storm_crown",     "Storm Crown",     "Volthrax's storm-wreathed crown.",          "junk", value=1000),
    "forgegod_essence":Item("forgegod_essence","Forgegod Essence","Pure divine forge energy.",                 "junk", value=2000),
    # ── Crucible of Reckoning ───────────────────────────────────────────────
    "crucible_triumph_token": Item("crucible_triumph_token","Crucible Triumph Token","Proof of defeating the Sun Eater.","junk",value=5000),
    # ── Sun Eater exclusives ────────────────────────────────────────────────
    "sunburst_core":         Item("sunburst_core",         "Sunburst Core",         "A pulsing remnant of stellar energy.",                "junk",      value=3000),
    "photon_shard":          Item("photon_shard",          "Photon Shard",          "Light made solid.",                                   "junk",      value=2000),
    "stellar_essence":       Item("stellar_essence",       "Stellar Essence",       "A distilled star fragment.",                          "junk",      value=2000),
    "corona_circlet":        Item("corona_circlet",        "Corona Circlet",        "A golden halo that hovers above the head.",           "junk",      value=4000),
    "incandescent_vial":     Item("incandescent_vial",     "Incandescent Vial",     "Restores all party members to full HP instantly.",    "consumable",value=1500, heal=9999),
    "blinding_powder":       Item("blinding_powder",       "Blinding Powder",       "Causes temporary blindness in enemies.",              "junk",      value=800),
    "sun_eater_trophy_head": Item("sun_eater_trophy_head", "Sun Eater Trophy Head", "Legendary bragging rights.",                         "junk",      value=10000),
    "eternal_flame":         Item("eternal_flame",         "Eternal Flame",         "A flame that never extinguishes.",                    "junk",      value=2500),
    "radiant_blessing":      Item("radiant_blessing",      "Radiant Blessing",      "A blessing from the sun itself.",                     "junk",      value=3500),
    "eclipse_stone":         Item("eclipse_stone",         "Eclipse Stone",         "Shadow within light.",                               "junk",      value=1800),
    # ── Lootbox exclusives ──────────────────────────────────────────────────
    "prismatic_shard":  Item("prismatic_shard",  "Prismatic Shard",  "A shard that refracts all colors.",                "junk", value=200),
    "echo_core":        Item("echo_core",        "Echo Core",        "Holds the echo of a defeated boss.",               "junk", value=600),
    "void_essence":     Item("void_essence",     "Void Essence",     "Essence of the between-worlds.",                   "junk", value=1200),
    "celestial_ember":  Item("celestial_ember",  "Celestial Ember",  "A dying piece of a star.",                         "junk", value=2000),
    "corrupted_pearl":  Item("corrupted_pearl",  "Corrupted Pearl",  "A pearl with shadowed depths.",                    "junk", value=500),
    "eon_crystal":      Item("eon_crystal",       "Eon Crystal",     "Ancient crystal predating history.",               "junk", value=1000),
    "leviathan_scale":  Item("leviathan_scale",  "Leviathan Scale",  "Scale from a legendary sea creature.",             "junk", value=700),
    "forge_catalyst":   Item("forge_catalyst",   "Forge Catalyst",   "+50% material efficiency on next craft.",          "consumable", value=300),
    "soulweaver_thread":Item("soulweaver_thread","Soulweaver Thread","Binds essence to steel.",                          "junk", value=400),
    "elder_bone":       Item("elder_bone",       "Elder Bone",       "Bone of an ancient creature.",                     "junk", value=150),
    "starfall_dust":    Item("starfall_dust",    "Starfall Dust",    "Powder from meteorites.",                          "junk", value=1100),
    "hollowed_talisman":Item("hollowed_talisman","Hollowed Talisman","The Hollowed King's amulet. Whispers cryptically.","junk", value=800),
    "tempest_feather":  Item("tempest_feather",  "Tempest Feather",  "From a storm eagle. Light as air.",                "junk", value=350),
    "sunken_locket":    Item("sunken_locket",    "Sunken Locket",    "A locket from drowned sailors.",                   "junk", value=100),
    "malice_stone":     Item("malice_stone",     "Malice Stone",     "Pure hatred crystallized.",                        "junk", value=650),
    "moonveil_silk":    Item("moonveil_silk",    "Moonveil Silk",    "Silk that shimmers like moonlight.",               "junk", value=450),
    "ashen_crown":      Item("ashen_crown",      "Ashen Crown",      "A crown of volcanic ash. Mining keepsake.",        "junk", value=180),
    "abyssal_fang":     Item("abyssal_fang",     "Abyssal Fang",     "A fang from the deep.",                           "junk", value=750),
    "godly_fragment":   Item("godly_fragment",   "Godly Fragment",   "A shard of divine essence.",                      "junk", value=2500),
    "chronicle_ink":    Item("chronicle_ink",    "Chronicle Ink",    "Ink used to unlock hidden lore entries.",          "junk", value=250),
    # ── Fish ────────────────────────────────────────────────────────────────
    "river_minnow":  Item("river_minnow",  "River Minnow",  "A tiny silver fish.",                     "food", value=3,  heal=2),
    "bluegill":      Item("bluegill",      "Bluegill",      "A flat-sided freshwater fish.",            "food", value=5,  heal=4),
    "forest_perch":  Item("forest_perch",  "Forest Perch",  "Patterned like bark.",                    "food", value=10, heal=8),
    "sunfish":       Item("sunfish",       "Sunfish",       "Bright gold scales.",                     "food", value=8,  heal=6),
    "golden_carp":   Item("golden_carp",   "Golden Carp",   "Shimmering gold scales.",                 "food", value=15, heal=12),
    "meadow_eel":    Item("meadow_eel",    "Meadow Eel",    "A long green eel from meadow streams.",   "food", value=20, heal=15),
    "blind_eel":     Item("blind_eel",     "Blind Eel",     "Eyeless cave-dwelling eel.",              "food", value=10, heal=8),
    "glow_shrimp":   Item("glow_shrimp",   "Glow Shrimp",   "Bioluminescent cave shrimp.",             "food", value=15, heal=10),
    "cave_grouper":  Item("cave_grouper",  "Cave Grouper",  "A pale fish from underground rivers.",    "food", value=25, heal=18),
    "mudpike":       Item("mudpike",       "Mudpike",       "A muddy pike from the swamp.",            "food", value=20, heal=14),
    "bog_leech":     Item("bog_leech",     "Bog Leech",     "Slimy and unappetizing.",                 "food", value=5,  heal=3),
    "glowfin":       Item("glowfin",       "Glowfin",       "Luminescent fin fish.",                   "food", value=30, heal=20),
    "swamp_pike":    Item("swamp_pike",    "Swamp Pike",    "A massive pike from the deepest bog.",    "food", value=40, heal=28),
    "magmacarp":     Item("magmacarp",     "Magmacarp",     "Swims in lava pools. Scales are hot.",    "food", value=35, heal=25),
    "ashfin":        Item("ashfin",        "Ashfin",        "Grey fish from volcanic ash rivers.",     "food", value=55, heal=38),
    "lavakraken_spawn":Item("lavakraken_spawn","Lava Kraken Spawn","A hatchling from lava depths.",    "food", value=80, heal=55),
    "ice_salmon":    Item("ice_salmon",    "Ice Salmon",    "Salmon with iridescent blue scales.",     "food", value=50, heal=35),
    "glacier_trout": Item("glacier_trout", "Glacier Trout", "Trout from glacial meltwater.",           "food", value=70, heal=48),
    "frozen_pike":   Item("frozen_pike",   "Frozen Pike",   "A pike encased in a thin layer of ice.", "food", value=90, heal=60),
    "deepsquid":     Item("deepsquid",     "Deepsquid",     "Multi-armed and enormous.",               "food", value=80, heal=55),
    "anglerfish":    Item("anglerfish",    "Anglerfish",    "Lured in by its own light.",              "food", value=100,heal=70),
    "kraken_spawn":  Item("kraken_spawn",  "Kraken Spawn",  "A tiny kraken. Still dangerous.",         "food", value=120,heal=80),
    "sunken_relic":  Item("sunken_relic",  "Sunken Relic",  "Not a fish, but fished up anyway.",      "junk", value=200),
    "bonefish":      Item("bonefish",      "Bonefish",      "Skeleton of a fish animated by curse.",   "food", value=100,heal=68),
    "cursed_catch":  Item("cursed_catch",  "Cursed Catch",  "Something that should not be eaten.",     "food", value=80, heal=50),
    "spectralfin":   Item("spectralfin",   "Spectralfin",   "Translucent spectral fish.",              "food", value=150,heal=100),
    "voltcatfish":   Item("voltcatfish",   "Voltcatfish",   "Shocks anything that touches it.",        "food", value=200,heal=130),
    "starwhale":     Item("starwhale",     "Starwhale",     "A whale made of stars. One exists.",      "food", value=1000,heal=500),

    # Weapons are loaded from json/weapons/*.json by world/weapons.py at import.

    # ── Armor ──
    "leather_armor": Item("leather_armor", "Leather Armor", "Light protection.",                "armor", value=25,  defense=2),
    "iron_armor":    Item("iron_armor",    "Iron Armor",    "Heavy plates.",                    "armor", value=90,  defense=5, requirements={"combat": 4}),
    "dragonscale":   Item("dragonscale",   "Dragonscale Armor", "Iridescent scales, nearly impenetrable.", "armor", value=600, defense=12, requirements={"combat": 9}),

    # ── Consumables ──
    "small_potion": Item("small_potion", "Small Potion", "Restores 25 HP.",  "consumable", value=5,  heal=25),
    "large_potion": Item("large_potion", "Large Potion", "Restores 75 HP.",  "consumable", value=15, heal=75),

    # ── Fishing rods ──
    # Tools required to use !fish. Like pickaxes, they cannot be used in
    # combat. Tier gates rare fish via min_fishing_level on the catch.
    "wood_fishing_rod":  Item("wood_fishing_rod",  "Wood Fishing Rod",  "A simple line and stick. Catches the basics.", "fishing_rod", value=15),
    "iron_fishing_rod":  Item("iron_fishing_rod",  "Iron Fishing Rod",  "A weighted rod that lets you reach deeper pools.", "fishing_rod", value=80, requirements={"fishing": 4}),

    # Seeds and crops are registered dynamically by world/seeds.py at startup.
}


def get(item_id: str) -> Item | None:
    return ITEMS.get(item_id.lower())
