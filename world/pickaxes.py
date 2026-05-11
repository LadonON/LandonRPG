"""Pickaxe definitions loaded from json/pickaxes/*.json.

Pickaxes are gathering tools, not weapons — they cannot be equipped in the
weapon slot and have no combat attacks. Each pickaxe has a tier
(`pickaxe_level`) plus a per-instance upgrade level (1-100) that scales
with !craft upgrade, mirroring weapons.
"""
import json
import os
from dataclasses import dataclass

from . import items as items_module

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "pickaxes")


@dataclass(frozen=True)
class PickaxeUpgrade:
    max_level: int = 100
    per_level_materials: tuple = ()          # tuple of (item_id, amount)
    level_per_step: float = 0.05              # effective +pickaxe_level per upgrade step


@dataclass(frozen=True)
class Pickaxe:
    id: str
    name: str
    description: str
    pickaxe_level: int                        # tier (1 = wood, 3 = iron, ...)
    value: int
    requirements: dict
    upgrade: PickaxeUpgrade


PICKAXES: dict[str, Pickaxe] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)

        up = data.get("upgrade", {})
        upgrade = PickaxeUpgrade(
            max_level=up.get("max_level", 100),
            per_level_materials=tuple(
                (m["item"], m["amount"]) for m in up.get("per_level_materials", [])
            ),
            level_per_step=up.get("level_per_step", 0.05),
        )

        PICKAXES[data["id"]] = Pickaxe(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            pickaxe_level=data.get("pickaxe_level", 1),
            value=data.get("value", 0),
            requirements=dict(data.get("requirements", {})),
            upgrade=upgrade,
        )

        items_module.ITEMS[data["id"]] = items_module.Item(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            type="pickaxe",
            value=data.get("value", 0),
            requirements=dict(data.get("requirements", {})),
        )


_load()


def get(pickaxe_id: str) -> Pickaxe | None:
    return PICKAXES.get(pickaxe_id.lower())


def is_pickaxe(item_id: str) -> bool:
    return item_id.lower() in PICKAXES


# ── Per-instance state helpers (mirror pvp.engine for weapons) ──────────────

def get_instance(player, pickaxe_id: str) -> dict:
    inst = player.pickaxe_instances.get(pickaxe_id)
    if inst is None:
        inst = {"level": 1}
        player.pickaxe_instances[pickaxe_id] = inst
    inst.setdefault("level", 1)
    return inst


def instance_level(player, pickaxe_id: str) -> int:
    return get_instance(player, pickaxe_id).get("level", 1)


def effective_pickaxe_level(player, pickaxe_id: str) -> int:
    """Pickaxe tier plus level-based bonus from upgrades."""
    p = get(pickaxe_id)
    if p is None:
        return 0
    inst_lvl = instance_level(player, pickaxe_id)
    return p.pickaxe_level + int(p.upgrade.level_per_step * (inst_lvl - 1))
