"""PvE battle engine — mirrors the PVP arena for monster fights.

Reuses dice/class helpers from pvp.engine. Each battle is a single player
versus a single monster, alternating turns. Same poise-stagger rules apply.
"""
from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass, field

from ..pvp import engine as pvpe
from ..world import items, weapons


# ── State ────────────────────────────────────────────────────────────────────

@dataclass
class PlayerSide:
    user_id: int
    name: str
    hp: int
    max_hp: int
    poise: int = 10
    max_poise: int = 10
    is_defending: bool = False


@dataclass
class MonsterSide:
    monster: object              # Monster instance from world.monsters.spawn()
    is_defending: bool = False

    @property
    def name(self) -> str:
        return self.monster.name

    @property
    def hp(self) -> int:
        return self.monster.health

    @hp.setter
    def hp(self, v: int) -> None:
        self.monster.health = max(0, v)

    @property
    def max_hp(self) -> int:
        return self.monster.max_health

    @property
    def poise(self) -> int:
        return self.monster.poise

    @poise.setter
    def poise(self, v: int) -> None:
        self.monster.poise = max(0, v)

    @property
    def max_poise(self) -> int:
        return self.monster.max_poise


@dataclass
class PVEBattle:
    id: str
    player: PlayerSide
    enemy: MonsterSide
    turn: str = "player"   # "player" or "monster"
    started_at: float = field(default_factory=time.time)
    ended: bool = False


BATTLES: dict[str, PVEBattle] = {}
PLAYER_BATTLE: dict[int, str] = {}


def in_battle(user_id: int) -> bool:
    return user_id in PLAYER_BATTLE


def get_battle(user_id: int) -> PVEBattle | None:
    bid = PLAYER_BATTLE.get(user_id)
    return BATTLES.get(bid) if bid else None


def new_battle_id() -> str:
    return uuid.uuid4().hex[:6]


def start_battle(player_obj, monster) -> PVEBattle:
    side_p = PlayerSide(
        user_id=player_obj.user_id if hasattr(player_obj, "user_id") else 0,
        name=player_obj.name,
        hp=player_obj.health,
        max_hp=player_obj.max_health,
    )
    side_m = MonsterSide(monster=monster)
    battle = PVEBattle(id=new_battle_id(), player=side_p, enemy=side_m)
    BATTLES[battle.id] = battle
    PLAYER_BATTLE[side_p.user_id] = battle.id
    return battle


def end_battle(battle: PVEBattle) -> None:
    battle.ended = True
    BATTLES.pop(battle.id, None)
    PLAYER_BATTLE.pop(battle.player.user_id, None)


# ── Player attacks monster ───────────────────────────────────────────────────

@dataclass
class AttackResult:
    actor_name: str
    target_name: str
    weapon_name: str
    attack_name: str
    swings: list[dict]
    total_damage: int
    target_hp_after: int
    target_poise_after: int
    poise_broken: bool = False


def _ac_for(target_defense: int, weapon_class: str) -> int:
    bypass = pvpe.class_defense_ignored(weapon_class, target_defense)
    return 10 + max(0, target_defense - bypass)


def resolve_player_attack(
    player_obj,
    enemy: MonsterSide,
    weapon_id: str,
    attack_id: str,
) -> tuple[AttackResult | None, str | None]:
    weapon = weapons.get(weapon_id)
    if weapon is None:
        return None, f"Unknown weapon `{weapon_id}`."
    attack = pvpe.find_attack(player_obj, weapon_id, attack_id)
    if attack is None:
        listing = ", ".join(a.id for a in pvpe.available_attacks(player_obj, weapon_id))
        return None, f"`{weapon.name}` has no attack `{attack_id}`. Try: {listing}."
    if player_obj.equipped_weapon != weapon_id:
        return None, f"You aren't wielding **{weapon.name}**. Equip it first."

    target_def = enemy.monster.defense
    armor_class = _ac_for(target_def, weapon.weapon_class)

    swings_count = 1
    if random.random() < pvpe.class_extra_attack_chance(weapon.weapon_class):
        swings_count += 1

    damage_mod = pvpe.total_damage_bonus(player_obj, weapon_id) + attack.damage_bonus
    cls_mult = _class_damage_multiplier_vs_monster(weapon.weapon_class, target_def)
    if enemy.is_defending:
        cls_mult *= 0.5

    swings, total_damage = _roll_swings(
        swings_count, attack, weapon.weapon_class, armor_class, damage_mod, cls_mult
    )

    enemy.hp = max(0, enemy.hp - total_damage)
    poise_loss = pvpe.total_poise_break(player_obj, weapon_id, attack)
    new_poise = enemy.poise - poise_loss
    poise_broken = new_poise <= 0 and enemy.poise > 0
    if poise_broken:
        enemy.poise = enemy.max_poise
    else:
        enemy.poise = max(0, new_poise)

    return (
        AttackResult(
            actor_name=player_obj.name,
            target_name=enemy.name,
            weapon_name=weapon.name,
            attack_name=attack.name,
            swings=swings,
            total_damage=total_damage,
            target_hp_after=enemy.hp,
            target_poise_after=enemy.poise,
            poise_broken=poise_broken,
        ),
        None,
    )


# ── Monster attacks player ───────────────────────────────────────────────────

def resolve_monster_attack(
    enemy: MonsterSide,
    player_side: PlayerSide,
    player_obj,
) -> AttackResult:
    """Monster takes a single attack. Uses its damage_die + to_hit_bonus."""
    target_def = pvpe.player_defense(player_obj)
    armor_class = 10 + target_def  # monsters have no class bypass

    swing = {}
    roll = pvpe.d20()
    total_to_hit = roll + enemy.monster.to_hit_bonus
    crit = roll == 20
    miss = roll == 1 or (not crit and total_to_hit < armor_class)
    total_damage = 0
    dice = []
    if not miss:
        dmg, dice = pvpe.roll_die_string(enemy.monster.damage_die)
        if crit:
            extra, extra_dice = pvpe.roll_die_string(enemy.monster.damage_die)
            dmg += extra
            dice = dice + extra_dice
        dmg = max(1, dmg + enemy.monster.damage // 2)  # weapon damage_bonus analog
        if player_side.is_defending:
            dmg = max(1, int(dmg * 0.5))
        total_damage = dmg
    swing = {
        "hit": not miss, "crit": crit, "roll": roll,
        "total_to_hit": total_to_hit, "ac": armor_class,
        "damage": total_damage, "dice": dice,
    }

    player_side.hp = max(0, player_side.hp - total_damage)
    new_poise = player_side.poise - enemy.monster.poise_break
    poise_broken = new_poise <= 0 and player_side.poise > 0
    if poise_broken:
        player_side.poise = player_side.max_poise
    else:
        player_side.poise = max(0, new_poise)

    # Sync to live Player object so death penalty / heals see correct HP.
    player_obj.health = player_side.hp

    return AttackResult(
        actor_name=enemy.name,
        target_name=player_obj.name,
        weapon_name="natural weapon",
        attack_name=enemy.monster.attack_msg,
        swings=[swing],
        total_damage=total_damage,
        target_hp_after=player_side.hp,
        target_poise_after=player_side.poise,
        poise_broken=poise_broken,
    )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _class_damage_multiplier_vs_monster(weapon_class: str, target_defense: int) -> float:
    """Mirror of pvp.class_damage_multiplier but defense-aware for monsters."""
    if weapon_class == "heavy" and target_defense >= 5:
        return 1.5
    if weapon_class == "two_handed":
        return 1.25
    if weapon_class == "ranged":
        return 0.75
    return 1.0


def _roll_swings(count, attack, weapon_class, armor_class, damage_mod, cls_mult):
    swings = []
    total = 0
    for _ in range(count):
        roll = pvpe.d20()
        total_to_hit = roll + attack.to_hit_bonus + pvpe.class_to_hit_modifier(weapon_class)
        crit = roll == 20
        miss = roll == 1 or (not crit and total_to_hit < armor_class)
        if miss:
            swings.append({
                "hit": False, "crit": False, "roll": roll,
                "total_to_hit": total_to_hit, "ac": armor_class,
                "damage": 0, "dice": [],
            })
            continue
        dmg, dice = pvpe.roll_die_string(attack.damage_die)
        if crit:
            extra, extra_dice = pvpe.roll_die_string(attack.damage_die)
            dmg += extra
            dice = dice + extra_dice
        dmg = max(1, int((dmg + damage_mod) * cls_mult))
        total += dmg
        swings.append({
            "hit": True, "crit": crit, "roll": roll,
            "total_to_hit": total_to_hit, "ac": armor_class,
            "damage": dmg, "dice": dice,
        })
    return swings, total


def format_result(r: AttackResult) -> str:
    lines = [f"**{r.actor_name}** uses **{r.weapon_name} — {r.attack_name}**!"]
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
        f"  → {r.target_name}: **{r.target_hp_after} HP**, poise {r.target_poise_after}."
    )
    if r.poise_broken:
        lines.append(
            f"  ⚡ **Poise broken!** {r.target_name} is staggered — "
            f"{r.actor_name} gets another turn (poise restored)."
        )
    return "\n".join(lines)
