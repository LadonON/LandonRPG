from dataclasses import dataclass, field


@dataclass
class MonsterSpawn:
    """One entry in a zone's spawn table: which monster, at what level."""
    monster_id: str
    level: int = 1


@dataclass
class ForageDrop:
    """One entry in a zone's forage table: which seed, with what relative weight."""
    seed_id: str
    weight: int = 1


@dataclass
class FishingCatch:
    """One entry in a zone's fishing pool: an item id with a relative weight."""
    item_id: str
    weight: int = 1


@dataclass
class Zone:
    zone_id: str
    name: str
    description: str
    difficulty: int = 1
    spawn_table: list[MonsterSpawn] = field(default_factory=list)
    min_combat_level: int = 1
    min_foraging_level: int = 1
    min_farming_level: int = 1
    min_mining_level: int = 1
    min_fishing_level: int = 1
    forage_table: list[ForageDrop] = field(default_factory=list)
    # Resource ids minable here. Per-resource drop chance lives in the
    # resource's own JSON (json/resources/<id>.json).
    mining_resources: tuple = ()
    # Weighted loot pool for fishing in this zone. Empty = fishing disabled.
    fishing_pool: list[FishingCatch] = field(default_factory=list)
