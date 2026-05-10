"""PVP battle engine.

State lives in-memory only — battles do not persist across bot restarts.
"""
from __future__ import annotations

import random
import re
import time
import uuid
from dataclasses import dataclass, field

from ..world import items, weapons, weapon_skills


# ── Weapon instance helpers ──────────────────────────────────────────────────

def get_instance(player, weapon_id: str) -> dict:
    """Return the player's per-weapon state dict, creating it if needed.

    Schema:
      {"level": int, "attacks": [<reserved>], "skill": <skill_id|None>}
    Only one weapon skill may be attached per weapon at a time.
    """
    inst = player.weapon_instances.get(weapon_id)
    if inst is None:
        inst = {"level": 1, "attacks": [], "skill": None}
        player.weapon_instances[weapon_id] = inst
    inst.setdefault("skill", None)
    inst.setdefault("attacks", [])
    inst.setdefault("level", 1)
    return inst


def attached_skill(player, weapon_id: str):
    """Return the WeaponSkill attached to this weapon for this player, or None."""
    inst = get_instance(player, weapon_id)
    sid = inst.get("skill")
    return weapon_skills.get(sid) if sid else None


def available_attacks(player, weapon_id: str):
    """All attacks available on this weapon — base attacks plus the attached skill's attack."""
    w = weapons.get(weapon_id)
    if w is None:
        return []
    result = list(w.attacks)
    skill = attached_skill(player, weapon_id)
    if skill:
        result.append(skill.attack)
    return result


def find_attack(player, weapon_id: str, attack_id: str):
    """Look up an attack id across base + attached-skill attacks."""
    aid = attack_id.lower()
    for a in available_attacks(player, weapon_id):
        if a.id.lower() == aid:
            return a
    return None


def instance_level(player, weapon_id: str) -> int:
    return get_instance(player, weapon_id).get("level", 1)


def total_damage_bonus(player, weapon_id: str) -> int:
    """Base damage_bonus + per-level upgrade bonus."""
    w = weapons.get(weapon_id)
    if w is None:
        return 0
    lvl = instance_level(player, weapon_id)
    return w.damage_bonus + int(w.upgrade.attack_per_level * (lvl - 1))


def total_poise_break(player, weapon_id: str, attack: weapons.Attack) -> int:
    w = weapons.get(weapon_id)
    if w is None:
        return attack.poise_break
    lvl = instance_level(player, weapon_id)
    return attack.poise_break + int(w.upgrade.poise_per_level * (lvl - 1))


# ── Dice ─────────────────────────────────────────────────────────────────────

_DIE_RE = re.compile(r"^\s*(\d+)d(\d+)\s*$")


def roll_die_string(spec: str) -> tuple[int, list[int]]:
    m = _DIE_RE.match(spec)
    if not m:
        return 0, []
    n, sides = int(m.group(1)), int(m.group(2))
    rolls = [random.randint(1, sides) for _ in range(n)]
    return sum(rolls), rolls


def d20() -> int:
    return random.randint(1, 20)


# ── Defense / armor ──────────────────────────────────────────────────────────

def player_defense(player) -> int:
    """Total defense from equipped armor."""
    if not player.equipped_armor:
        return 0
    armor = items.get(player.equipped_armor)
    return armor.defense if armor else 0


def is_heavily_armored(player) -> bool:
    return player_defense(player) >= 5


# ── Class ability hooks ──────────────────────────────────────────────────────

def class_to_hit_modifier(weapon_class: str) -> int:
    return {
        "heavy": -2,
        "light": 0,
        "finesse": 2,
        "two_handed": -1,
        "ranged": 0,
    }.get(weapon_class, 0)


def class_damage_multiplier(weapon_class: str, target) -> float:
    if weapon_class == "heavy" and is_heavily_armored(target):
        return 1.5  # heavy weapons shred heavy armor
    if weapon_class == "two_handed":
        return 1.25
    if weapon_class == "ranged":
        return 0.75
    return 1.0


def class_defense_ignored(weapon_class: str, target_defense: int) -> int:
    """How much of the defender's armor this class bypasses."""
    if weapon_class == "finesse":
        return min(2, target_defense)
    if weapon_class == "ranged":
        return target_defense // 2
    return 0


def class_extra_attack_chance(weapon_class: str) -> float:
    if weapon_class == "light":
        return 0.25
    return 0.0


# ── Battle state ─────────────────────────────────────────────────────────────

@dataclass
class Combatant:
    user_id: int
    name: str
    hp: int
    max_hp: int
    poise: int = 10
    max_poise: int = 10
    is_defending: bool = False


@dataclass
class Battle:
    id: str
    a: Combatant
    b: Combatant
    wager: int = 0                     # gold wager per side
    public: bool = False
    spectators: set = field(default_factory=set)
    turn_user_id: int = 0              # whose turn it is
    log: list[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    ended: bool = False
    winner_user_id: int | None = None

    def opponent_of(self, user_id: int) -> Combatant:
        return self.b if user_id == self.a.user_id else self.a

    def self_of(self, user_id: int) -> Combatant:
        return self.a if user_id == self.a.user_id else self.b


# user_id -> battle_id, battle_id -> Battle
BATTLES: dict[str, Battle] = {}
PLAYER_BATTLE: dict[int, str] = {}


def new_battle_id() -> str:
    return uuid.uuid4().hex[:6]


def in_battle(user_id: int) -> bool:
    return user_id in PLAYER_BATTLE


def get_battle(user_id: int) -> Battle | None:
    bid = PLAYER_BATTLE.get(user_id)
    return BATTLES.get(bid) if bid else None


def end_battle(battle: Battle) -> None:
    battle.ended = True
    BATTLES.pop(battle.id, None)
    PLAYER_BATTLE.pop(battle.a.user_id, None)
    PLAYER_BATTLE.pop(battle.b.user_id, None)


# ── Resolve one attack ───────────────────────────────────────────────────────

@dataclass
class AttackResult:
    weapon_name: str
    attack_name: str
    swings: list[dict]                 # each: {hit, crit, roll, total_to_hit, damage, dice}
    total_damage: int
    target_hp_after: int
    target_poise_after: int
    poise_broken: bool = False         # True if this attack staggered the defender


def resolve_attack(
    attacker_player,
    defender_player,
    defender_combatant: Combatant,
    weapon_id: str,
    attack_id: str,
) -> tuple[AttackResult | None, str | None]:
    """Roll a full attack action. Returns (result, error_message)."""
    weapon = weapons.get(weapon_id)
    if weapon is None:
        return None, f"Unknown weapon `{weapon_id}`."
    attack = find_attack(attacker_player, weapon_id, attack_id)
    if attack is None:
        listing = ", ".join(a.id for a in available_attacks(attacker_player, weapon_id))
        return None, f"`{weapon.name}` has no attack `{attack_id}`. Try: {listing}."

    if attacker_player.equipped_weapon != weapon_id:
        return None, f"You aren't wielding **{weapon.name}**. Equip it first."

    # Number of swings: 1, plus possible bonus from class.
    swings_count = 1
    if random.random() < class_extra_attack_chance(weapon.weapon_class):
        swings_count += 1

    target_def = player_defense(defender_player)
    armor_class = 10 + max(0, target_def - class_defense_ignored(weapon.weapon_class, target_def))

    damage_mod = total_damage_bonus(attacker_player, weapon_id) + attack.damage_bonus
    cls_mult = class_damage_multiplier(weapon.weapon_class, defender_player)
    if defender_combatant.is_defending:
        cls_mult *= 0.5

    swings: list[dict] = []
    total_damage = 0
    for _ in range(swings_count):
        roll = d20()
        total_to_hit = roll + attack.to_hit_bonus + class_to_hit_modifier(weapon.weapon_class)
        crit = roll == 20
        miss = roll == 1 or (not crit and total_to_hit < armor_class)
        if miss:
            swings.append({
                "hit": False, "crit": False, "roll": roll,
                "total_to_hit": total_to_hit, "ac": armor_class,
                "damage": 0, "dice": [],
            })
            continue
        dmg, dice = roll_die_string(attack.damage_die)
        if crit:
            extra, extra_dice = roll_die_string(attack.damage_die)
            dmg += extra
            dice = dice + extra_dice
        dmg = max(1, int((dmg + damage_mod) * cls_mult))
        total_damage += dmg
        swings.append({
            "hit": True, "crit": crit, "roll": roll,
            "total_to_hit": total_to_hit, "ac": armor_class,
            "damage": dmg, "dice": dice,
        })

    defender_combatant.hp = max(0, defender_combatant.hp - total_damage)
    poise_loss = total_poise_break(attacker_player, weapon_id, attack)
    new_poise = defender_combatant.poise - poise_loss
    poise_broken = new_poise <= 0 and defender_combatant.poise > 0
    if poise_broken:
        # Defender is staggered; their poise resets to full and the attacker
        # is granted another turn (handled by the caller).
        defender_combatant.poise = defender_combatant.max_poise
    else:
        defender_combatant.poise = max(0, new_poise)

    return (
        AttackResult(
            weapon_name=weapon.name,
            attack_name=attack.name,
            swings=swings,
            total_damage=total_damage,
            target_hp_after=defender_combatant.hp,
            target_poise_after=defender_combatant.poise,
            poise_broken=poise_broken,
        ),
        None,
    )


def format_attack_result(attacker_name: str, defender_name: str, r: AttackResult) -> str:
    lines = [f"**{attacker_name}** uses **{r.weapon_name} — {r.attack_name}**!"]
    for i, s in enumerate(r.swings, 1):
        prefix = f"  Swing {i}: " if len(r.swings) > 1 else "  "
        if not s["hit"]:
            lines.append(f"{prefix}d20={s['roll']} (need {s['ac']}) — **miss**.")
        else:
            crit = " **CRIT!**" if s["crit"] else ""
            lines.append(
                f"{prefix}d20={s['roll']} (vs AC {s['ac']}) hit{crit} — "
                f"rolled {s['dice']} → **{s['damage']}** damage."
            )
    lines.append(
        f"  → {defender_name}: **{r.target_hp_after} HP**, poise {r.target_poise_after}."
    )
    if r.poise_broken:
        lines.append(
            f"  ⚡ **Poise broken!** {defender_name} is staggered — "
            f"{attacker_name} gets another turn (poise restored)."
        )
    return "\n".join(lines)
