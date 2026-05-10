"""Single source of truth for player skill stats.

To add a new stat, append a StatDefinition below. Everything else — Player
storage attributes, DB columns, migrations, persistence, the !stats command,
and item/zone requirement checks — picks it up automatically.

Each stat needs:
  - a name           ("combat", "farming", ...)
  - an XP unit label ("kills", "XP", ...)
  - a bonus_label    (shown in !stats; e.g. "loot/kill")
  - an XP curve      (xp_coeff * level ** xp_exp = XP needed for next level)

Optional knobs: bonus_divisor, default level/xp, custom attribute names.
A matching `json/unlocks/<name>.json` file provides the milestone rewards.
"""
from dataclasses import dataclass, field
from typing import Callable

from . import unlocks


# ── Declarative stat definitions ──────────────────────────────────────────────
# Add a stat here and re-run the bot. New columns are migrated on startup.

@dataclass(frozen=True)
class StatDefinition:
    name: str
    unit: str
    bonus_label: str
    xp_coeff: float
    xp_exp: float
    bonus_divisor: int = 3
    default_level: int = 1
    default_xp: int = 0
    # Storage attribute names on Player. Default convention is
    #   level_attr = f"{name}_level"
    #   xp_attr    = f"{name}_xp"
    # Combat is the historical odd one out: its xp attribute is "combat_kills".
    level_attr: str = ""
    xp_attr: str = ""

    @property
    def resolved_level_attr(self) -> str:
        return self.level_attr or f"{self.name}_level"

    @property
    def resolved_xp_attr(self) -> str:
        return self.xp_attr or f"{self.name}_xp"


DEFINITIONS: list[StatDefinition] = [
    StatDefinition(
        name="combat",
        unit="kills",
        bonus_label="loot/kill",
        xp_coeff=15,
        xp_exp=1.3,
        xp_attr="combat_kills",
    ),
    StatDefinition(
        name="farming",
        unit="XP",
        bonus_label="yield/harvest",
        xp_coeff=50,
        xp_exp=1.5,
    ),
    StatDefinition(
        name="foraging",
        unit="XP",
        bonus_label="extra seed/forage",
        xp_coeff=15,
        xp_exp=1.3,
        bonus_divisor=4,
    ),
]


# ── Runtime registry consumed by the rest of the codebase ────────────────────

@dataclass(frozen=True)
class StatConfig:
    name: str
    level_attr: str
    xp_attr: str
    xp_to_next: Callable
    unit: str
    bonus_label: str
    bonus_divisor: int = 3

    @property
    def unlocks_pool(self):
        return unlocks.unlocks_for(self.name)


def _curve(coeff: float, exp: float, level_attr: str) -> Callable:
    return lambda player: int(coeff * getattr(player, level_attr) ** exp)


STATS: dict[str, StatConfig] = {}
for _d in DEFINITIONS:
    STATS[_d.name] = StatConfig(
        name=_d.name,
        level_attr=_d.resolved_level_attr,
        xp_attr=_d.resolved_xp_attr,
        xp_to_next=_curve(_d.xp_coeff, _d.xp_exp, _d.resolved_level_attr),
        unit=_d.unit,
        bonus_label=_d.bonus_label,
        bonus_divisor=_d.bonus_divisor,
    )


def get(name: str) -> StatConfig | None:
    return STATS.get(name.lower())


def names() -> list[str]:
    return list(STATS.keys())


def definitions() -> list[StatDefinition]:
    return list(DEFINITIONS)


# ── Generic level/XP helpers (replace the per-stat methods on Player) ────────

def level_of(player, stat_name: str) -> int:
    return getattr(player, STATS[stat_name].level_attr)


def xp_of(player, stat_name: str) -> int:
    return getattr(player, STATS[stat_name].xp_attr)


def xp_to_next(player, stat_name: str) -> int:
    return STATS[stat_name].xp_to_next(player)


def gain_xp(player, stat_name: str, amount: int) -> bool:
    """Add XP to the named stat. Returns True if the player leveled up."""
    cfg = STATS[stat_name]
    cur_xp = getattr(player, cfg.xp_attr) + amount
    if cur_xp >= cfg.xp_to_next(player):
        setattr(player, cfg.xp_attr, 0)
        setattr(player, cfg.level_attr, getattr(player, cfg.level_attr) + 1)
        return True
    setattr(player, cfg.xp_attr, cur_xp)
    return False
