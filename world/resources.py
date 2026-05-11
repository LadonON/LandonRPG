"""Mining resource definitions loaded from json/resources/*.json.

Each resource registers itself as an Item (so it sits in inventory, sells in
shop, can be a craft ingredient) and carries mining-specific metadata: drop
chance, pickaxe requirements, and mining XP.
"""
import json
import os
from dataclasses import dataclass

from . import items as items_module

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "resources")


@dataclass(frozen=True)
class Resource:
    id: str
    name: str
    description: str
    value: int
    drop_chance: int                     # base % chance per swing
    mining_xp: int                       # XP per successful hit
    min_mining_level: int                # stat-level gate
    min_pickaxe_level: int               # effective pickaxe level required
    required_pickaxe: str                # "" means any pickaxe meeting min_pickaxe_level


RESOURCES: dict[str, Resource] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)

        rid = data["id"]
        RESOURCES[rid] = Resource(
            id=rid,
            name=data["name"],
            description=data.get("description", ""),
            value=data.get("value", 1),
            drop_chance=data.get("drop_chance", 50),
            mining_xp=data.get("mining_xp", 5),
            min_mining_level=data.get("min_mining_level", 1),
            min_pickaxe_level=data.get("min_pickaxe_level", 1),
            required_pickaxe=data.get("required_pickaxe", ""),
        )

        items_module.ITEMS[rid] = items_module.Item(
            id=rid,
            name=data["name"],
            description=data.get("description", ""),
            type="resource",
            value=data.get("value", 1),
        )


_load()


def get(resource_id: str) -> Resource | None:
    return RESOURCES.get(resource_id.lower())
