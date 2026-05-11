"""Tiered cost scaling for weapon and pickaxe upgrades.

Per-level material costs declared in each weapon/pickaxe JSON act as the
*base* cost for reaching level 1. Every subsequent upgrade step adds one
more of each base material, so upgrading to level N costs:

    base_amount + (N - 1)   of each ingredient

This guarantees the cost visibly increases with every single upgrade.
Tier-specific extra materials are added on top at fixed amounts.

Example (Iron Sword, base = 2 tooth):
  L1 → 2 tooth   L5 → 6 tooth   L10 → 11 tooth   L20 → 21 tooth

To tune the grind, adjust the addend (currently 1 per level).
To tune rare-material gates, edit the TIERS extras below.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class UpgradeTier:
    max_level: int          # inclusive — applies to upgrades whose destination level is ≤ this
    extra: tuple            # tuple of (item_id, amount) added on top of scaled base
    label: str              # short human label shown in messages


TIERS: tuple = (
    UpgradeTier(max_level=25,  extra=(),                              label="Apprentice"),
    UpgradeTier(max_level=50,  extra=(("bone", 2),),                  label="Adept"),
    UpgradeTier(max_level=75,  extra=(("skull", 1),),                 label="Expert"),
    UpgradeTier(max_level=100, extra=(("skull", 2), ("iron_ore", 1)), label="Master"),
)


def tier_for(target_level: int) -> UpgradeTier:
    """Return the tier whose curve applies to reaching `target_level`."""
    for t in TIERS:
        if target_level <= t.max_level:
            return t
    return TIERS[-1]


def required_for(base_materials, target_level: int) -> Counter:
    """Compute the actual Counter of materials needed to reach `target_level`.

    `base_materials` is an iterable of (item_id, amount) tuples — typically
    the weapon/pickaxe's `upgrade.per_level_materials`.
    """
    tier = tier_for(target_level)
    counts: Counter = Counter()
    for item_id, amount in base_materials:
        counts[item_id] += amount + (target_level - 1)
    for item_id, amount in tier.extra:
        counts[item_id] += amount
    return counts
