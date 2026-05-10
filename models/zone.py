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
class Zone:
    zone_id: str
    name: str
    description: str
    difficulty: int = 1
    spawn_table: list[MonsterSpawn] = field(default_factory=list)
    min_combat_level: int = 1
    min_foraging_level: int = 1
    min_farming_level: int = 1
    forage_table: list[ForageDrop] = field(default_factory=list)
