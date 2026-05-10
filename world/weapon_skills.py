"""Weapon Skills (formerly 'power tokens').

A weapon skill is a craftable consumable item that, when attached to a
weapon, grants that weapon an extra attack. Only ONE skill can be attached
to a weapon at a time — attaching a new skill returns the previously
attached one to the player's inventory.

Each skill JSON in `landonrpg/json/weapon_skills/` defines:
  id, name, description, value, attack: { id, name, damage_die, damage_bonus, poise_break, to_hit_bonus }
"""
import json
import os
from dataclasses import dataclass

from . import items as items_module
from . import weapons as weapons_module

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "weapon_skills")


@dataclass(frozen=True)
class WeaponSkill:
    id: str
    name: str
    description: str
    value: int
    attack: weapons_module.Attack    # the attack granted when attached


SKILLS: dict[str, WeaponSkill] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        a = data["attack"]
        skill = WeaponSkill(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            value=data.get("value", 0),
            attack=weapons_module.Attack(
                id=a["id"],
                name=a["name"],
                damage_die=a["damage_die"],
                damage_bonus=a.get("damage_bonus", 0),
                poise_break=a.get("poise_break", 0),
                to_hit_bonus=a.get("to_hit_bonus", 0),
            ),
        )
        SKILLS[skill.id] = skill
        # Register as a weapon_skill item so it can sit in inventory / shop.
        items_module.ITEMS[skill.id] = items_module.Item(
            id=skill.id,
            name=skill.name,
            description=skill.description,
            type="weapon_skill",
            value=skill.value,
        )


_load()


def get(skill_id: str) -> WeaponSkill | None:
    return SKILLS.get(skill_id.lower())
