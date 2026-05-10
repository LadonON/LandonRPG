import json
import os
from dataclasses import dataclass

from . import items as items_module

_JSON_DIR = os.path.join(os.path.dirname(__file__), "..", "json", "seeds")


@dataclass(frozen=True)
class SeedConfig:
    seed_id: str
    seed_name: str
    crop_id: str
    crop_name: str
    grow_time_seconds: int
    yield_base: int
    farming_xp: int
    min_farming_level: int


SEEDS: dict[str, SeedConfig] = {}


def _load() -> None:
    json_dir = os.path.realpath(_JSON_DIR)
    if not os.path.isdir(json_dir):
        return
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(json_dir, filename), encoding="utf-8") as f:
            data = json.load(f)

        seed_id = data["seed_id"]
        crop_id = data["crop_id"]

        # Register seed item into the shared items catalog
        items_module.ITEMS[seed_id] = items_module.Item(
            id=seed_id,
            name=data["seed_name"],
            description=f"Plant to grow {data['crop_name']}.",
            type="seed",
            value=data.get("seed_value", 1),
        )

        # Register crop item into the shared items catalog
        items_module.ITEMS[crop_id] = items_module.Item(
            id=crop_id,
            name=data["crop_name"],
            description=data.get("crop_description", ""),
            type=data.get("crop_type", "food"),
            value=data.get("crop_value", 2),
            heal=data.get("crop_heal", 0),
        )

        SEEDS[seed_id] = SeedConfig(
            seed_id=seed_id,
            seed_name=data["seed_name"],
            crop_id=crop_id,
            crop_name=data["crop_name"],
            grow_time_seconds=int(data.get("grow_time_minutes", 5) * 60),
            yield_base=data.get("yield_base", 1),
            farming_xp=data.get("farming_xp", 5),
            min_farming_level=data.get("min_farming_level", 1),
        )


_load()


def get(seed_id: str) -> SeedConfig | None:
    return SEEDS.get(seed_id.lower())
