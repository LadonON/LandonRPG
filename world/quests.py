"""Quest definitions loaded from json/quests/*.json.

Each quest has:
  id, name, description, objective {type, ...}, rewards {xp, gold, items, unlock_zone},
  requirements {level?, combat?, farming?, foraging?, ...}

Objective types:
  - collect_item    {item_id, amount}            baseline-relative count in inventory
  - kill_monster    {monster_id, amount}         counter incremented on PvE victory
  - reach_stat_level {stat, level}               check `<stat>_level` >= level
  - visit_zone      {zone_id}                    flag set on next warp into zone
"""
import json
import os
from dataclasses import dataclass, field

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "quests")

_OBJECTIVE_TYPES = ("collect_item", "kill_monster", "reach_stat_level", "visit_zone")


@dataclass(frozen=True)
class Objective:
    type: str
    item_id: str = ""
    monster_id: str = ""
    stat: str = ""
    zone_id: str = ""
    amount: int = 0
    level: int = 0


@dataclass(frozen=True)
class Rewards:
    xp: int = 0
    gold: int = 0
    items: tuple = ()
    unlock_zone: str = ""


@dataclass(frozen=True)
class Quest:
    id: str
    name: str
    description: str
    objective: Objective
    rewards: Rewards
    requirements: dict = field(default_factory=dict)


QUESTS: dict[str, Quest] = {}


def _build_objective(d: dict) -> Objective:
    t = d["type"]
    if t not in _OBJECTIVE_TYPES:
        raise ValueError(f"unknown quest objective type: {t}")
    return Objective(
        type=t,
        item_id=d.get("item_id", ""),
        monster_id=d.get("monster_id", ""),
        stat=d.get("stat", ""),
        zone_id=d.get("zone_id", ""),
        amount=d.get("amount", 0),
        level=d.get("level", 0),
    )


def _build_rewards(d: dict) -> Rewards:
    return Rewards(
        xp=d.get("xp", 0),
        gold=d.get("gold", 0),
        items=tuple(d.get("items", [])),
        unlock_zone=d.get("unlock_zone", "") or "",
    )


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        QUESTS[data["id"]] = Quest(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            objective=_build_objective(data["objective"]),
            rewards=_build_rewards(data.get("rewards", {})),
            requirements=dict(data.get("requirements", {})),
        )


_load()


def get(quest_id: str) -> Quest | None:
    return QUESTS.get(quest_id.lower())
