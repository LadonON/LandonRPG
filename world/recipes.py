import json
import os
from collections import Counter
from . import items

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "recipes")

# result_item_id -> {ingredient_id: quantity}
RECIPES: dict[str, dict[str, int]] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        RECIPES[data["result_id"]] = dict(data["ingredients"])


_load()


def can_craft(player, result_id: str, count: int = 1) -> tuple[bool, list[str]]:
    recipe = RECIPES.get(result_id)
    if recipe is None:
        return False, [f"No recipe for `{result_id}`."]
    have = Counter(player.inventory)
    missing = []
    for ing, qty in recipe.items():
        short = qty * count - have[ing]
        if short > 0:
            label = items.get(ing).name if items.get(ing) else ing
            missing.append(f"{label} x{short} more")
    return (not missing), missing


def craft(player, result_id: str, count: int = 1) -> tuple[bool, str]:
    ok, missing = can_craft(player, result_id, count)
    if not ok:
        if not RECIPES.get(result_id):
            return False, missing[0]
        return False, "Missing: " + ", ".join(missing)
    for ing, qty in RECIPES[result_id].items():
        for _ in range(qty * count):
            player.inventory.remove(ing)
    for _ in range(count):
        player.inventory.append(result_id)
    return True, items.get(result_id).name
