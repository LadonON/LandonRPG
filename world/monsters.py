import json
import os

from ..models.monster import Monster

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "monsters")

# Raw config keyed by monster_id
_DATA: dict[str, dict] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        _DATA[data["monster_id"].lower()] = data


_load()


def spawn(monster_id: str, level: int = 1) -> Monster | None:
    data = _DATA.get(monster_id.lower())
    if data is None:
        return None
    m = Monster(
        name=data["name"],
        max_health=data["max_health"],
        damage=data["damage"],
        attack_msg=data.get("attack_msg", "attacks"),
        xp_reward=data.get("xp_reward", 10),
        loot=list(data.get("loot", [])),
        damage_die=data.get("damage_die", "1d6"),
        to_hit_bonus=data.get("to_hit_bonus", level),
        defense=data.get("defense", 0),
        max_poise=data.get("poise", 8),
        poise=data.get("poise", 8),
        poise_break=data.get("poise_break", 1),
        monster_id=data["monster_id"].lower(),
    )
    m.max_health *= level
    m.damage *= level
    m.xp_reward = int(m.xp_reward * level ** 1.4)
    m.health = m.max_health
    m.level = level
    m.name = f"L{level} {m.name}"
    return m
