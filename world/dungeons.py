"""Per-zone dungeon definitions loaded from json/dungeons/*.json.

Each dungeon JSON:
  zone_id, name, description, spawn_pool [monster_ids],
  rooms: [{enemy_count: [min, max], spawn_pool?: override}],
  boss_id

Difficulty multipliers (applied at runtime):
  easy: 0.7, normal: 1.0, hard: 1.3, insane: 1.6,
  nightmare: 2.0, cataclysm: 2.5, abyssal: 3.0
"""
import json
import os
from dataclasses import dataclass

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "dungeons")


DIFFICULTY_MULTIPLIERS = {
    "easy":      0.7,
    "normal":    1.0,
    "hard":      1.3,
    "insane":    1.6,
    "nightmare": 2.0,
    "cataclysm": 2.5,
    "abyssal":   3.0,
}

DIFFICULTIES = tuple(DIFFICULTY_MULTIPLIERS.keys())


@dataclass(frozen=True)
class DungeonRoom:
    enemy_count_min: int
    enemy_count_max: int
    spawn_pool: tuple                # tuple[str], may override dungeon default


@dataclass(frozen=True)
class Dungeon:
    zone_id: str
    name: str
    description: str
    spawn_pool: tuple                # tuple[str] of monster_ids
    rooms: tuple                     # tuple[DungeonRoom]
    boss_id: str


# zone_id -> Dungeon
DUNGEONS: dict[str, Dungeon] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        rooms = tuple(
            DungeonRoom(
                enemy_count_min=r["enemy_count"][0],
                enemy_count_max=r["enemy_count"][1],
                spawn_pool=tuple(r.get("spawn_pool", [])) or tuple(data.get("spawn_pool", [])),
            )
            for r in data.get("rooms", [])
        )
        DUNGEONS[data["zone_id"]] = Dungeon(
            zone_id=data["zone_id"],
            name=data["name"],
            description=data.get("description", ""),
            spawn_pool=tuple(data.get("spawn_pool", [])),
            rooms=rooms,
            boss_id=data.get("boss_id", ""),
        )


_load()


def get(zone_id: str) -> Dungeon | None:
    return DUNGEONS.get(zone_id.lower())
