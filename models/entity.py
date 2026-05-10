import random
from dataclasses import dataclass, field


@dataclass
class Entity:
    name: str
    max_health: int
    damage: int
    health: int = field(init=False)

    def __post_init__(self):
        self.health = self.max_health

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int) -> int:
        actual = min(amount, self.health)
        self.health -= actual
        return actual

    def attack(self, target: "Entity") -> int:
        roll = random.randint(int(self.damage * 0.8), int(self.damage * 1.2))
        return target.take_damage(roll)
