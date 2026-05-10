"""Weapon configuration loaded from json/weapons/*.json.

Each weapon registers itself into items.ITEMS (so non-PVP code that just
treats weapons as items keeps working) AND into WEAPONS for PVP/upgrade
code that needs class, attacks, and upgrade recipe.
"""
import json
import os
from dataclasses import dataclass, field

from . import items as items_module

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "weapons")

WEAPON_CLASSES = ("light", "heavy", "finesse", "two_handed", "ranged")


@dataclass(frozen=True)
class Attack:
    id: str
    name: str
    damage_die: str        # e.g. "1d8", "2d10"
    damage_bonus: int = 0
    poise_break: int = 0
    to_hit_bonus: int = 0


@dataclass(frozen=True)
class UpgradeRecipe:
    max_level: int = 100
    per_level_materials: tuple = ()   # tuple of (item_id, amount)
    attack_per_level: float = 0.5
    poise_per_level: float = 0.3


@dataclass(frozen=True)
class Weapon:
    id: str
    name: str
    description: str
    weapon_class: str
    value: int
    damage_bonus: int
    requirements: dict
    attacks: tuple             # tuple[Attack, ...]
    upgrade: UpgradeRecipe

    def attack_by_id(self, attack_id: str) -> Attack | None:
        attack_id = attack_id.lower()
        for a in self.attacks:
            if a.id.lower() == attack_id:
                return a
        return None


WEAPONS: dict[str, Weapon] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)

        wid = data["id"]
        wclass = data.get("weapon_class", "light")
        if wclass not in WEAPON_CLASSES:
            raise ValueError(
                f"weapon {wid}: invalid weapon_class {wclass!r} "
                f"(allowed: {WEAPON_CLASSES})"
            )

        attacks = tuple(
            Attack(
                id=a["id"],
                name=a["name"],
                damage_die=a["damage_die"],
                damage_bonus=a.get("damage_bonus", 0),
                poise_break=a.get("poise_break", 0),
                to_hit_bonus=a.get("to_hit_bonus", 0),
            )
            for a in data.get("attacks", [])
        )

        up = data.get("upgrade", {})
        upgrade = UpgradeRecipe(
            max_level=up.get("max_level", 100),
            per_level_materials=tuple(
                (m["item"], m["amount"]) for m in up.get("per_level_materials", [])
            ),
            attack_per_level=up.get("attack_per_level", 0.5),
            poise_per_level=up.get("poise_per_level", 0.3),
        )

        WEAPONS[wid] = Weapon(
            id=wid,
            name=data["name"],
            description=data["description"],
            weapon_class=wclass,
            value=data.get("value", 0),
            damage_bonus=data.get("damage_bonus", 0),
            requirements=dict(data.get("requirements", {})),
            attacks=attacks,
            upgrade=upgrade,
        )

        # Mirror into items.ITEMS so the rest of the codebase still sees a
        # plain weapon Item with damage_bonus + requirements.
        items_module.ITEMS[wid] = items_module.Item(
            id=wid,
            name=data["name"],
            description=data["description"],
            type="weapon",
            value=data.get("value", 0),
            damage_bonus=data.get("damage_bonus", 0),
            requirements=dict(data.get("requirements", {})),
        )


_load()


def get(weapon_id: str) -> Weapon | None:
    return WEAPONS.get(weapon_id.lower())


def is_weapon(item_id: str) -> bool:
    return item_id.lower() in WEAPONS
