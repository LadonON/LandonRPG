"""Dungeon battle state and resolution.

A `DungeonRun` represents one party progressing through a dungeon's rooms.
Each room is a multi-combatant fight with initiative rolled per round.

State is in-memory only (lost on bot restart).
"""
from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass, field

from ..world import dungeons, monsters as monster_world, bosses as boss_world
from ..world import lootboxes
from ..pvp import engine as pvpe
from ..world import weapons


# ── Combatants ───────────────────────────────────────────────────────────────

@dataclass
class PartyMember:
    user_id: int
    name: str
    hp: int
    max_hp: int
    poise: int = 12
    max_poise: int = 12
    is_defending: bool = False
    initiative: int = 0
    pending_lootboxes: list = field(default_factory=list)   # rarities awarded


@dataclass
class EnemySlot:
    """One enemy in the room — wraps a Monster object or a Boss."""
    kind: str                       # "monster" or "boss"
    obj: object                     # Monster or BossInstance
    initiative: int = 0
    is_defending: bool = False

    @property
    def name(self) -> str:
        return self.obj.name

    @property
    def hp(self) -> int:
        return self.obj.health if self.kind == "monster" else self.obj.health

    @hp.setter
    def hp(self, v: int) -> None:
        self.obj.health = max(0, v)

    @property
    def max_hp(self) -> int:
        return self.obj.max_health

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def defense(self) -> int:
        return getattr(self.obj, "defense", 0)


@dataclass
class BossInstance:
    """Stateful copy of a Boss config for one fight."""
    boss: boss_world.Boss
    health: int
    poise: int

    @property
    def name(self) -> str:
        return self.boss.name

    @property
    def max_health(self) -> int:
        return self.boss.max_health

    @property
    def max_poise(self) -> int:
        return self.boss.max_poise

    @property
    def defense(self) -> int:
        return self.boss.defense


@dataclass
class DungeonRun:
    id: str
    zone_id: str
    difficulty: str
    host_user_id: int
    party: list                     # list[PartyMember]
    dungeon: dungeons.Dungeon
    zone_difficulty: int
    enemies: list = field(default_factory=list)             # current room enemies
    room_index: int = 0                                     # 0-based; len(rooms) is boss room
    in_boss_room: bool = False
    started_at: float = field(default_factory=time.time)
    ended: bool = False


RUNS: dict[str, DungeonRun] = {}
PLAYER_RUN: dict[int, str] = {}     # user_id -> run_id


def in_dungeon(user_id: int) -> bool:
    return user_id in PLAYER_RUN


def get_run(user_id: int) -> DungeonRun | None:
    rid = PLAYER_RUN.get(user_id)
    return RUNS.get(rid) if rid else None


def new_run_id() -> str:
    return uuid.uuid4().hex[:6]


# ── Room population ──────────────────────────────────────────────────────────

def _scaled_count(base_min: int, base_max: int, difficulty: str, party_size: int) -> int:
    """Difficulty + party-size scaling on enemy counts."""
    mult = dungeons.DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
    party_mult = 1.0 + 0.5 * (party_size - 1)        # 1p=1.0, 2p=1.5, 3p=2.0, 4p=2.5
    raw = random.randint(base_min, base_max) * mult * party_mult
    return max(1, int(round(raw)))


def populate_room(run: DungeonRun) -> None:
    """Fill run.enemies based on the current room index."""
    if run.room_index < len(run.dungeon.rooms):
        room = run.dungeon.rooms[run.room_index]
        count = _scaled_count(room.enemy_count_min, room.enemy_count_max,
                              run.difficulty, len(run.party))
        pool = list(room.spawn_pool) or list(run.dungeon.spawn_pool)
        run.enemies = []
        # Difficulty also scales per-monster level slightly.
        mult = dungeons.DIFFICULTY_MULTIPLIERS.get(run.difficulty, 1.0)
        monster_level = max(1, int(round(run.zone_difficulty * mult)))
        for _ in range(count):
            mid = random.choice(pool)
            m = monster_world.spawn(mid, monster_level)
            if m is None:
                continue
            run.enemies.append(EnemySlot(kind="monster", obj=m))
        run.in_boss_room = False
    else:
        # Boss room
        boss_cfg = boss_world.get(run.dungeon.boss_id)
        if boss_cfg is None:
            run.enemies = []
            return
        # Boss HP scales with difficulty + party size.
        mult = dungeons.DIFFICULTY_MULTIPLIERS.get(run.difficulty, 1.0)
        party_mult = 1.0 + 0.4 * (len(run.party) - 1)
        scaled_hp = int(boss_cfg.max_health * mult * party_mult)
        instance = BossInstance(
            boss=boss_cfg,
            health=scaled_hp,
            poise=boss_cfg.max_poise,
        )
        # Override max_health on instance via boss copy is not allowed (frozen);
        # we keep boss.max_health for HP-bar; engine reads instance.max_health
        # which mirrors boss config. To support scaled HP display, we override:
        instance.boss = boss_cfg  # frozen; max_health stays from JSON
        # Patch the live HP only — display will show {health}/{boss.max_health}*scale isn't necessary.
        run.enemies = [EnemySlot(kind="boss", obj=instance)]
        run.in_boss_room = True


def roll_initiative(run: DungeonRun) -> list:
    """Roll d20 + bonus for every combatant; return list ordered by initiative desc."""
    order = []
    for p in run.party:
        # Player initiative bonus = combat_level // 2 (loose D&D dex proxy).
        bonus = 1
        p.initiative = pvpe.d20() + bonus
        order.append(("player", p, p.initiative))
    for e in run.enemies:
        if not e.is_alive:
            continue
        if e.kind == "boss":
            bonus = e.obj.boss.initiative_bonus
        else:
            bonus = getattr(e.obj, "to_hit_bonus", 0) // 2
        e.initiative = pvpe.d20() + bonus
        order.append(("enemy", e, e.initiative))
    order.sort(key=lambda x: x[2], reverse=True)
    return order


def alive_enemies(run: DungeonRun) -> list:
    return [e for e in run.enemies if e.is_alive]


def alive_party(run: DungeonRun) -> list:
    return [p for p in run.party if p.hp > 0]


def room_cleared(run: DungeonRun) -> bool:
    return not alive_enemies(run)


# ── Player action ────────────────────────────────────────────────────────────

def player_attack(player_obj, party: PartyMember, run: DungeonRun,
                  weapon_id: str, attack_id: str, target_index: int = 0):
    """Resolve a player's weapon attack against an enemy in the room."""
    weapon = weapons.get(weapon_id)
    if weapon is None:
        return None, f"Unknown weapon `{weapon_id}`."
    if player_obj.equipped_weapon != weapon_id:
        return None, f"You aren't wielding **{weapon.name}**."
    attack = pvpe.find_attack(player_obj, weapon_id, attack_id)
    if attack is None:
        listing = ", ".join(a.id for a in pvpe.available_attacks(player_obj, weapon_id))
        return None, f"`{weapon.name}` has no attack `{attack_id}`. Try: {listing}."

    enemies = alive_enemies(run)
    if not enemies:
        return None, "Nothing left to hit."
    target_index = max(0, min(target_index, len(enemies) - 1))
    target = enemies[target_index]

    target_def = target.defense
    bypass = pvpe.class_defense_ignored(weapon.weapon_class, target_def)
    armor_class = 10 + max(0, target_def - bypass)

    swings_count = 1
    if random.random() < pvpe.class_extra_attack_chance(weapon.weapon_class):
        swings_count += 1

    damage_mod = pvpe.total_damage_bonus(player_obj, weapon_id) + attack.damage_bonus
    cls_mult = 1.0
    if weapon.weapon_class == "heavy" and target_def >= 5:
        cls_mult = 1.5
    elif weapon.weapon_class == "two_handed":
        cls_mult = 1.25
    elif weapon.weapon_class == "ranged":
        cls_mult = 0.75
    if target.is_defending:
        cls_mult *= 0.5

    swings = []
    total_damage = 0
    for _ in range(swings_count):
        roll = pvpe.d20()
        total_to_hit = roll + attack.to_hit_bonus + pvpe.class_to_hit_modifier(weapon.weapon_class)
        crit = roll == 20
        miss = roll == 1 or (not crit and total_to_hit < armor_class)
        if miss:
            swings.append({"hit": False, "crit": False, "roll": roll, "ac": armor_class, "damage": 0, "dice": []})
            continue
        dmg, dice = pvpe.roll_die_string(attack.damage_die)
        if crit:
            extra, ed = pvpe.roll_die_string(attack.damage_die)
            dmg += extra
            dice = dice + ed
        dmg = max(1, int((dmg + damage_mod) * cls_mult))
        total_damage += dmg
        swings.append({"hit": True, "crit": crit, "roll": roll, "ac": armor_class, "damage": dmg, "dice": dice})

    target.hp = max(0, target.hp - total_damage)
    return {
        "weapon": weapon.name,
        "attack": attack.name,
        "target_name": target.name,
        "swings": swings,
        "total_damage": total_damage,
        "target_hp": target.hp,
        "target_dead": target.hp <= 0,
    }, None


# ── Enemy action ─────────────────────────────────────────────────────────────

def enemy_action(enemy: EnemySlot, run: DungeonRun) -> dict:
    """Pick and resolve an action for an enemy. Returns a result dict."""
    party_alive = alive_party(run)
    if not party_alive:
        return {"text": f"{enemy.name} stands triumphant.", "summons": []}

    # Boss: pick from boss attacks, may summon or AoE.
    if enemy.kind == "boss":
        atk = random.choice(enemy.obj.boss.attacks)
        return _resolve_boss_attack(enemy, atk, run)

    # Regular monster: single-target d20 vs. random party member.
    target = random.choice(party_alive)
    return _resolve_monster_attack(enemy, target, run)


def _resolve_monster_attack(enemy: EnemySlot, target: PartyMember, run: DungeonRun) -> dict:
    m = enemy.obj
    armor_class = 10 + 0   # players' defense omitted from monster swing for simplicity here
    roll = pvpe.d20()
    total_to_hit = roll + m.to_hit_bonus
    crit = roll == 20
    miss = roll == 1 or (not crit and total_to_hit < armor_class)
    damage = 0
    dice = []
    if not miss:
        dmg, dice = pvpe.roll_die_string(m.damage_die)
        if crit:
            extra, ed = pvpe.roll_die_string(m.damage_die)
            dmg += extra
            dice += ed
        dmg = max(1, dmg + m.damage // 2)
        if target.is_defending:
            dmg = max(1, int(dmg * 0.5))
        damage = dmg
    target.hp = max(0, target.hp - damage)
    target.is_defending = False
    text = (
        f"**{m.name}** {m.attack_msg} → **{target.name}** "
        + (f"(d20={roll} miss vs AC {armor_class})" if miss
           else f"(d20={roll}{'CRIT! ' if crit else ''} hit, dice {dice} → **{damage}** dmg). HP {target.hp}/{target.max_hp}.")
    )
    return {"text": text, "summons": [], "target_dead": target.hp <= 0}


def _resolve_boss_attack(enemy: EnemySlot, atk: boss_world.BossAttack, run: DungeonRun) -> dict:
    """Boss attack: supports target_mode='all' and summons."""
    party_alive = alive_party(run)
    summons = []
    lines = [f"**{enemy.name}** uses **{atk.name}**!"]

    # Summon component
    if atk.summon_monster and atk.summon_amount > 0:
        for _ in range(atk.summon_amount):
            m = monster_world.spawn(atk.summon_monster, atk.summon_level)
            if m is not None:
                run.enemies.append(EnemySlot(kind="monster", obj=m))
                summons.append(m.name)
        if summons:
            lines.append(f"  Summoned: {', '.join(summons)}.")

    # Damage component (skip if pure summon attack)
    if atk.damage_die and atk.damage_die != "0d0":
        targets = list(party_alive) if atk.target_mode == "all" else [random.choice(party_alive)]
        for target in targets:
            armor_class = 10
            roll = pvpe.d20()
            total_to_hit = roll + atk.to_hit_bonus
            crit = roll == 20
            miss = roll == 1 or (not crit and total_to_hit < armor_class)
            if miss:
                lines.append(f"  → {target.name}: d20={roll} miss.")
                continue
            dmg, dice = pvpe.roll_die_string(atk.damage_die)
            if crit:
                extra, ed = pvpe.roll_die_string(atk.damage_die)
                dmg += extra
                dice += ed
            dmg = max(1, dmg + atk.damage_bonus)
            if target.is_defending:
                dmg = max(1, int(dmg * 0.5))
            target.hp = max(0, target.hp - dmg)
            target.is_defending = False
            lines.append(
                f"  → {target.name}: d20={roll}"
                + (" **CRIT!**" if crit else "")
                + f" dice {dice} → **{dmg}** dmg. HP {target.hp}/{target.max_hp}."
            )

    return {"text": "\n".join(lines), "summons": summons}


# ── Lootbox / room rewards ───────────────────────────────────────────────────

def grant_room_lootboxes(run: DungeonRun, boss_room: bool = False) -> dict:
    """Award one lootbox to every party member based on difficulty + zone diff."""
    awarded: dict[int, str] = {}
    for p in run.party:
        rarity = lootboxes.pick_rarity(run.difficulty, run.zone_difficulty, boss_bonus=boss_room)
        p.pending_lootboxes.append(rarity)
        awarded[p.user_id] = rarity
    return awarded


def end_run(run: DungeonRun) -> None:
    run.ended = True
    RUNS.pop(run.id, None)
    for p in run.party:
        PLAYER_RUN.pop(p.user_id, None)
