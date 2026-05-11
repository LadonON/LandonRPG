from dataclasses import dataclass, field
from .entity import Entity
from ..world import items, stats as stats_mod


@dataclass
class Player(Entity):
    level: int = 1
    xp: int = 0
    inventory: list[str] = field(default_factory=list)
    gold: int = 0
    equipped_weapon: str | None = None
    equipped_armor: str | None = None
    x: int = 0
    y: int = 0
    # Active growing plots — list of dicts serialised to JSON in the DB
    growing_plots: list = field(default_factory=list)
    # IDs of unlocks that have been claimed
    claimed_unlocks: list = field(default_factory=list)
    # Per-player weapon state: {weapon_id: {"level": int, "attacks": [...], "skill": skill_id|None}}
    weapon_instances: dict = field(default_factory=dict)
    # Equipped pickaxe slot (separate from weapon — pickaxes are gathering tools).
    equipped_pickaxe: str | None = None
    # Per-player pickaxe state: {pickaxe_id: {"level": int}}. Mirrors weapon_instances.
    pickaxe_instances: dict = field(default_factory=dict)
    # Equipped fishing rod slot. Required to use !fish. Static tool — no per-instance level.
    equipped_fishing_rod: str | None = None
    # Set to a battle id while in a PVP arena. Not persisted (battles are
    # in-memory only); cleared when the battle ends.
    pvp_battle_id: str | None = None
    # Quest state.
    active_quests: dict = field(default_factory=dict)        # {quest_id: {progress, started_at}}
    completed_quests: list = field(default_factory=list)     # [quest_id, ...]
    unlocked_zones: list = field(default_factory=list)       # zones unlocked via quest rewards

    def __post_init__(self):
        # Initialise health (Entity.__post_init__ would otherwise be skipped)
        super().__post_init__()
        # Skill stat storage is generated from world.stats.DEFINITIONS so a
        # new stat only needs an entry there, not edits here.
        for d in stats_mod.DEFINITIONS:
            if not hasattr(self, d.resolved_level_attr):
                setattr(self, d.resolved_level_attr, d.default_level)
            if not hasattr(self, d.resolved_xp_attr):
                setattr(self, d.resolved_xp_attr, d.default_xp)

    def attack(self, target: Entity) -> str:
        dealt = super().attack(target)
        return f"{self.name} strikes the {target.name} for {dealt} damage!"

    def take_damage(self, amount: int) -> int:
        if self.equipped_armor:
            armor = items.get(self.equipped_armor)
            if armor:
                amount = max(1, amount - armor.defense)
        return super().take_damage(amount)

    def xp_to_next_level(self) -> int:
        return int(100 * self.level ** 1.4)

    def gain_xp(self, amount: int) -> bool:
        self.xp += amount
        if self.xp >= self.xp_to_next_level():
            self.level_up()
            return True
        return False

    def level_up(self):
        self.level += 1
        self.max_health += 10
        self.damage += 2
        self.health = self.max_health
