from dataclasses import dataclass, field
from .entity import Entity


@dataclass
class Monster(Entity):
    attack_msg: str = "attacks"
    xp_reward: int = 10
    loot: list[str] = field(default_factory=list)
    # PvE-arena combat profile (used for d20 rolls, mirrors weapon attacks).
    damage_die: str = "1d6"
    to_hit_bonus: int = 0
    defense: int = 0
    max_poise: int = 8
    poise: int = 8
    poise_break: int = 1
    level: int = 1
    # The base monster_id from JSON (stable identifier; persists across spawn levels).
    monster_id: str = ""

    def attack(self, target: Entity) -> str:
        dealt = super().attack(target)
        return f"The {self.name} {self.attack_msg} for {dealt} damage!"
