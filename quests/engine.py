"""Quest state, progress evaluation, and reward awarding.

Player-side state (persisted on Player):
  active_quests:    {quest_id: {progress: {...}, started_at: float}}
  completed_quests: [quest_id, ...]
  unlocked_zones:   [zone_id, ...]    # zones unlocked via quest rewards

Manual claim model: a quest never auto-completes. Players must
`!quest claim <id>` once the objective is met; rewards are awarded then.
"""
from __future__ import annotations

import time

from ..world import quests as quests_world
from ..world import items as items_world
from ..world import stats as stats_mod


# ── Helpers ──────────────────────────────────────────────────────────────────

def _stat_level(player, stat_name: str) -> int:
    cfg = stats_mod.get(stat_name)
    if cfg is None:
        return 0
    return getattr(player, cfg.level_attr, 0)


def _check_requirements(player, requirements: dict) -> list[str]:
    """Return human-readable strings for any unmet quest start-requirements."""
    miss = []
    for key, req in (requirements or {}).items():
        if key == "level":
            cur = getattr(player, "level", 1)
            if cur < req:
                miss.append(f"Player Level {req} (you are L{cur})")
            continue
        cfg = stats_mod.get(key)
        if cfg is None:
            continue
        cur = getattr(player, cfg.level_attr, 1)
        if cur < req:
            miss.append(f"{key.title()} L{req} (you are L{cur})")
    return miss


# ── State init / progress ────────────────────────────────────────────────────

def _init_progress(player, quest: quests_world.Quest) -> dict:
    obj = quest.objective
    if obj.type == "collect_item":
        return {"baseline": player.inventory.count(obj.item_id)}
    if obj.type == "kill_monster":
        return {"count": 0}
    if obj.type == "visit_zone":
        return {"visited": False}
    if obj.type == "reach_stat_level":
        return {}  # nothing to track; check live at completion
    return {}


def progress_summary(player, quest_id: str) -> str:
    """Human-readable progress for an active quest."""
    quest = quests_world.get(quest_id)
    if quest is None:
        return f"unknown quest `{quest_id}`"
    state = player.active_quests.get(quest_id)
    if state is None:
        return f"quest `{quest_id}` not active"

    obj = quest.objective
    p = state["progress"]
    if obj.type == "collect_item":
        cur = player.inventory.count(obj.item_id)
        gained = max(0, cur - p.get("baseline", 0))
        item = items_world.get(obj.item_id)
        label = item.name if item else obj.item_id
        return f"{gained}/{obj.amount} {label} collected"
    if obj.type == "kill_monster":
        return f"{p.get('count', 0)}/{obj.amount} {obj.monster_id} defeated"
    if obj.type == "visit_zone":
        return "visited" if p.get("visited") else f"travel to `{obj.zone_id}`"
    if obj.type == "reach_stat_level":
        cur = _stat_level(player, obj.stat)
        return f"{obj.stat.title()} L{cur} / L{obj.level}"
    return "(unknown objective)"


def is_complete(player, quest_id: str) -> bool:
    quest = quests_world.get(quest_id)
    state = player.active_quests.get(quest_id)
    if quest is None or state is None:
        return False
    obj = quest.objective
    p = state["progress"]
    if obj.type == "collect_item":
        cur = player.inventory.count(obj.item_id)
        return (cur - p.get("baseline", 0)) >= obj.amount
    if obj.type == "kill_monster":
        return p.get("count", 0) >= obj.amount
    if obj.type == "visit_zone":
        return bool(p.get("visited"))
    if obj.type == "reach_stat_level":
        return _stat_level(player, obj.stat) >= obj.level
    return False


# ── Lifecycle ────────────────────────────────────────────────────────────────

def start(player, quest_id: str) -> tuple[bool, str]:
    quest = quests_world.get(quest_id)
    if quest is None:
        return False, f"Unknown quest `{quest_id}`."
    if quest_id in player.completed_quests:
        return False, f"You have already completed **{quest.name}**."
    if quest_id in player.active_quests:
        return False, f"**{quest.name}** is already active."

    miss = _check_requirements(player, quest.requirements)
    if miss:
        return False, f"Requirements not met: {', '.join(miss)}."

    player.active_quests[quest_id] = {
        "progress": _init_progress(player, quest),
        "started_at": time.time(),
    }
    return True, f"Quest started: **{quest.name}** — {quest.description}"


def abandon(player, quest_id: str) -> tuple[bool, str]:
    quest = quests_world.get(quest_id)
    if quest_id not in player.active_quests:
        return False, "That quest isn't active."
    del player.active_quests[quest_id]
    name = quest.name if quest else quest_id
    return True, f"Abandoned **{name}**."


def claim(player, quest_id: str) -> tuple[bool, str]:
    quest = quests_world.get(quest_id)
    if quest is None:
        return False, f"Unknown quest `{quest_id}`."
    if quest_id not in player.active_quests:
        return False, f"**{quest.name}** is not active."
    if not is_complete(player, quest_id):
        return False, f"Objective not yet met — {progress_summary(player, quest_id)}."

    rewards = quest.rewards
    awarded: list[str] = []

    if rewards.xp:
        leveled = player.gain_xp(rewards.xp)
        awarded.append(f"+{rewards.xp} XP")
        if leveled:
            awarded.append(f"**Player leveled up to {player.level}!**")
    if rewards.gold:
        player.gold += rewards.gold
        awarded.append(f"+{rewards.gold}g")
    for item_id in rewards.items:
        player.inventory.append(item_id)
        item = items_world.get(item_id)
        awarded.append(item.name if item else item_id)
    if rewards.unlock_zone:
        if rewards.unlock_zone not in player.unlocked_zones:
            player.unlocked_zones.append(rewards.unlock_zone)
        awarded.append(f"unlocked zone `{rewards.unlock_zone}`")

    del player.active_quests[quest_id]
    if quest_id not in player.completed_quests:
        player.completed_quests.append(quest_id)

    summary = ", ".join(awarded) if awarded else "no rewards"
    return True, f"**{quest.name}** complete! Rewards: {summary}"


# ── Event hooks (called from gameplay code) ─────────────────────────────────

def on_monster_killed(player, monster_id: str) -> None:
    """Increment kill_monster counters on any active matching quests."""
    for qid, state in player.active_quests.items():
        quest = quests_world.get(qid)
        if quest is None:
            continue
        obj = quest.objective
        if obj.type == "kill_monster" and obj.monster_id == monster_id:
            state["progress"]["count"] = state["progress"].get("count", 0) + 1


def on_zone_entered(player, zone_id: str) -> None:
    """Mark visit_zone quests as satisfied for the visited zone."""
    for qid, state in player.active_quests.items():
        quest = quests_world.get(qid)
        if quest is None:
            continue
        obj = quest.objective
        if obj.type == "visit_zone" and obj.zone_id == zone_id:
            state["progress"]["visited"] = True
