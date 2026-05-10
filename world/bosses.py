"""Boss definitions for dungeons.

Each boss JSON defines:
  id, name, max_health, defense, poise, poise_break, xp_reward, loot,
  initiative_bonus, dialogue {on_spawn, on_attack, on_low_hp, on_death},
  attacks: list of attack profiles, each with:
    - id, name, damage_die, damage_bonus, to_hit_bonus, poise_break
    - target_mode: "single" (default) or "all"  (hits every party member)
    - summon: optional {monster_id, amount, level}
"""
import json
import os
from dataclasses import dataclass

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "bosses")


@dataclass(frozen=True)
class BossAttack:
    id: str
    name: str
    damage_die: str
    damage_bonus: int = 0
    to_hit_bonus: int = 0
    poise_break: int = 1
    target_mode: str = "single"          # "single" | "all"
    summon_monster: str = ""             # monster_id to summon
    summon_amount: int = 0
    summon_level: int = 1


@dataclass(frozen=True)
class Boss:
    id: str
    name: str
    max_health: int
    defense: int
    max_poise: int
    poise_break: int
    initiative_bonus: int
    xp_reward: int
    loot: tuple
    attacks: tuple
    dialogue: dict


BOSSES: dict[str, Boss] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)

        attacks = tuple(
            BossAttack(
                id=a["id"],
                name=a["name"],
                damage_die=a["damage_die"],
                damage_bonus=a.get("damage_bonus", 0),
                to_hit_bonus=a.get("to_hit_bonus", 0),
                poise_break=a.get("poise_break", 1),
                target_mode=a.get("target_mode", "single"),
                summon_monster=a.get("summon", {}).get("monster_id", ""),
                summon_amount=a.get("summon", {}).get("amount", 0),
                summon_level=a.get("summon", {}).get("level", 1),
            )
            for a in data.get("attacks", [])
        )

        BOSSES[data["id"]] = Boss(
            id=data["id"],
            name=data["name"],
            max_health=data["max_health"],
            defense=data.get("defense", 0),
            max_poise=data.get("poise", 15),
            poise_break=data.get("poise_break", 2),
            initiative_bonus=data.get("initiative_bonus", 3),
            xp_reward=data.get("xp_reward", 200),
            loot=tuple(data.get("loot", [])),
            attacks=attacks,
            dialogue=dict(data.get("dialogue", {})),
        )


_load()


def get(boss_id: str) -> Boss | None:
    return BOSSES.get(boss_id.lower())
