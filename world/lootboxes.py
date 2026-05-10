"""Lootbox rarities, drop tier tables, and the open-a-box roller.

Rarities ordered worst → best. Each rarity has:
  - a per-rarity loot pool JSON (json/lootboxes/<rarity>.json)
  - a registered Item id `lootbox_<rarity>` so unopened boxes sit in inventory

Drop tiers (json/lootboxes/drop_tiers.json) map a dungeon difficulty + zone
difficulty band to a rarity-weight distribution. These percentages NEVER change.
"""
import json
import os
import random
from dataclasses import dataclass

from . import items as items_module

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "lootboxes")

RARITIES = ("common", "uncommon", "rare", "epic", "legendary", "mythic", "chroma")
RARITY_INDEX = {r: i for i, r in enumerate(RARITIES)}


@dataclass(frozen=True)
class LootboxPool:
    rarity: str
    pulls: int                       # how many roll picks per box
    gold_range: tuple                # (min, max)
    weighted_items: tuple            # tuple of dicts: {item, weight, amount: (min, max)}


POOLS: dict[str, LootboxPool] = {}
DROP_TIERS: dict = {}
BOSS_BONUS_STEPS: int = 1


def _zone_band(zone_difficulty: int) -> str:
    if zone_difficulty <= 2:
        return "low"
    if zone_difficulty <= 5:
        return "mid"
    return "high"


def _load_pools() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    for filename in sorted(os.listdir(json_dir)):
        if filename == "drop_tiers.json" or not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        rarity = data["rarity"]
        POOLS[rarity] = LootboxPool(
            rarity=rarity,
            pulls=data.get("pulls", 1),
            gold_range=tuple(data.get("gold_range", [0, 0])),
            weighted_items=tuple(
                {
                    "item": e["item"],
                    "weight": e["weight"],
                    "amount": tuple(e.get("amount", [1, 1])),
                }
                for e in data.get("items", [])
            ),
        )
        # Register lootbox as an inventory item.
        box_id = f"lootbox_{rarity}"
        items_module.ITEMS[box_id] = items_module.Item(
            id=box_id,
            name=f"{rarity.title()} Lootbox",
            description=f"A sealed {rarity} lootbox. Open with `!open {rarity}`.",
            type="lootbox",
            value=10 * (RARITY_INDEX[rarity] + 1),
        )


def _load_drop_tiers() -> None:
    global BOSS_BONUS_STEPS
    path = os.path.join(_JSON_DIR, "drop_tiers.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    BOSS_BONUS_STEPS = data.get("boss_bonus_rarity_steps", 1)
    for k, v in data.items():
        if k.startswith("_") or k == "boss_bonus_rarity_steps":
            continue
        DROP_TIERS[k] = v


_load_pools()
_load_drop_tiers()


# ── Rolling ──────────────────────────────────────────────────────────────────

def pick_rarity(difficulty: str, zone_difficulty: int, boss_bonus: bool = False) -> str:
    """Roll a lootbox rarity for the given (difficulty, zone) combo."""
    diff_table = DROP_TIERS.get(difficulty.lower(), DROP_TIERS["normal"])
    band = diff_table[_zone_band(zone_difficulty)]
    rarities = list(band.keys())
    weights = [band[r] for r in rarities]
    chosen = random.choices(rarities, weights=weights, k=1)[0]
    if boss_bonus and BOSS_BONUS_STEPS > 0:
        idx = min(RARITY_INDEX[chosen] + BOSS_BONUS_STEPS, len(RARITIES) - 1)
        chosen = RARITIES[idx]
    return chosen


@dataclass
class OpenedBox:
    rarity: str
    gold: int
    items: list             # [(item_id, count), ...]


def open_box(rarity: str) -> OpenedBox | None:
    pool = POOLS.get(rarity.lower())
    if pool is None:
        return None
    gold = random.randint(pool.gold_range[0], pool.gold_range[1]) if pool.gold_range else 0
    items_won: list = []
    if pool.weighted_items:
        weights = [w["weight"] for w in pool.weighted_items]
        for _ in range(pool.pulls):
            entry = random.choices(pool.weighted_items, weights=weights, k=1)[0]
            amount = random.randint(entry["amount"][0], entry["amount"][1])
            items_won.append((entry["item"], amount))
    return OpenedBox(rarity=rarity.lower(), gold=gold, items=items_won)


def lootbox_item_id(rarity: str) -> str:
    return f"lootbox_{rarity.lower()}"
