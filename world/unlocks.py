import json
import os
from dataclasses import dataclass

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "unlocks")


@dataclass(frozen=True)
class Unlock:
    id: str
    label: str
    description: str
    required_level: int
    category: str               # "combat" | "farming" | ...
    reward_items: tuple = ()    # item_ids granted on claim
    reward_gold: int = 0


# category name → list of Unlocks (sorted by required_level)
UNLOCKS_BY_CATEGORY: dict[str, list[Unlock]] = {}

# (category, required_level) → list[Unlock]
_BY_LEVEL: dict[tuple[str, int], list[Unlock]] = {}


def get_at_level(category: str, level: int) -> list[Unlock]:
    return _BY_LEVEL.get((category.lower(), level), [])


def unlocks_for(category: str) -> list[Unlock]:
    return UNLOCKS_BY_CATEGORY.get(category.lower(), [])


def _load_file(path: str, category: str) -> list[Unlock]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)
    result = [
        Unlock(
            id=e["id"],
            label=e["label"],
            description=e["description"],
            required_level=e["required_level"],
            category=category,
            reward_items=tuple(e.get("reward_items", [])),
            reward_gold=e.get("reward_gold", 0),
        )
        for e in entries
    ]
    result.sort(key=lambda u: u.required_level)
    return result


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        category = os.path.splitext(filename)[0].lower()
        loaded = _load_file(os.path.join(json_dir, filename), category)
        UNLOCKS_BY_CATEGORY[category] = loaded
        for u in loaded:
            _BY_LEVEL.setdefault((u.category, u.required_level), []).append(u)


_load()


# ── Backwards-compatible aliases ──────────────────────────────────────────────
# Existing code references these module-level lists directly.

COMBAT_UNLOCKS: list[Unlock] = UNLOCKS_BY_CATEGORY.get("combat", [])
FARMING_UNLOCKS: list[Unlock] = UNLOCKS_BY_CATEGORY.get("farming", [])
