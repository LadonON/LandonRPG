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

    # Weapons are loaded from json/weapons/*.json by world/weapons.py at import.

    # ── Armor ──
    "leather_armor": Item("leather_armor", "Leather Armor", "Light protection.",                "armor", value=25,  defense=2),
    "iron_armor":    Item("iron_armor",    "Iron Armor",    "Heavy plates.",                    "armor", value=90,  defense=5, requirements={"combat": 4}),
    "dragonscale":   Item("dragonscale",   "Dragonscale Armor", "Iridescent scales, nearly impenetrable.", "armor", value=600, defense=12, requirements={"combat": 9}),

    # ── Consumables ──
    "small_potion": Item("small_potion", "Small Potion", "Restores 25 HP.",  "consumable", value=5,  heal=25),
    "large_potion": Item("large_potion", "Large Potion", "Restores 75 HP.",  "consumable", value=15, heal=75),

    # Seeds and crops are registered dynamically by world/seeds.py at startup.
}


def get(item_id: str) -> Item | None:
    return ITEMS.get(item_id.lower())
