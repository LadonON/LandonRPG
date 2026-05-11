from ..models.player import Player
from ..db import SessionLocal, PlayerRow, init_db
from ..world import stats as stats_mod

init_db()

# user_id -> Player. Cache so each command works on the same instance.
_cache: dict[int, Player] = {}


def get_or_create(user_id: int, name: str) -> Player:
    if user_id in _cache:
        return _cache[user_id]

    with SessionLocal() as s:
        row = s.get(PlayerRow, user_id)
        if row is None:
            stat_defaults = {}
            for d in stats_mod.DEFINITIONS:
                stat_defaults[d.resolved_level_attr] = d.default_level
                stat_defaults[d.resolved_xp_attr] = d.default_xp
            # New players start with a basic rusty sword.
            row = PlayerRow(
                user_id=user_id, name=name,
                max_health=50, damage=8, health=50,
                inventory=["rusty_sword"], gold=0, level=1, xp=0, x=0, y=0,
                **stat_defaults,
            )
            s.add(row)
            s.commit()
            s.refresh(row)
        player = _row_to_player(row)

    _cache[user_id] = player
    return player


def save(user_id: int) -> None:
    """Persist the cached player back to the DB. No-op if nothing cached."""
    player = _cache.get(user_id)
    if player is None:
        return
    with SessionLocal() as s:
        row = s.get(PlayerRow, user_id)
        if row is None:
            row = PlayerRow(user_id=user_id, name=player.name,
                            max_health=player.max_health, damage=player.damage,
                            health=player.health)
            s.add(row)
        _player_to_row(player, row)
        s.commit()


def _row_to_player(row: PlayerRow) -> Player:
    p = Player(name=row.name, max_health=row.max_health, damage=row.damage)
    p.health = row.health
    p.level = row.level
    p.xp = row.xp
    p.inventory = list(row.inventory or [])
    p.gold = row.gold
    p.equipped_weapon = row.equipped_weapon
    p.equipped_armor = row.equipped_armor
    p.x = 0  # always respawn in the village on load
    p.y = 0
    for d in stats_mod.DEFINITIONS:
        setattr(p, d.resolved_level_attr,
                getattr(row, d.resolved_level_attr) or d.default_level)
        setattr(p, d.resolved_xp_attr,
                getattr(row, d.resolved_xp_attr) or d.default_xp)
    p.growing_plots = list(row.growing_plots or [])
    p.claimed_unlocks = list(row.claimed_unlocks or [])
    p.weapon_instances = dict(row.weapon_instances or {})
    p.active_quests = dict(row.active_quests or {})
    p.completed_quests = list(row.completed_quests or [])
    p.unlocked_zones = list(row.unlocked_zones or [])
    p.equipped_pickaxe = row.equipped_pickaxe
    p.pickaxe_instances = dict(row.pickaxe_instances or {})
    p.equipped_fishing_rod = row.equipped_fishing_rod
    return p


def _player_to_row(p: Player, row: PlayerRow) -> None:
    row.name = p.name
    row.max_health = p.max_health
    row.damage = p.damage
    row.health = p.health
    row.level = p.level
    row.xp = p.xp
    row.inventory = list(p.inventory)
    row.gold = p.gold
    row.equipped_weapon = p.equipped_weapon
    row.equipped_armor = p.equipped_armor
    row.x = p.x
    row.y = p.y
    for d in stats_mod.DEFINITIONS:
        setattr(row, d.resolved_level_attr, getattr(p, d.resolved_level_attr))
        setattr(row, d.resolved_xp_attr, getattr(p, d.resolved_xp_attr))
    row.growing_plots = list(p.growing_plots)
    row.claimed_unlocks = list(p.claimed_unlocks)
    row.weapon_instances = dict(p.weapon_instances)
    row.active_quests = dict(p.active_quests)
    row.completed_quests = list(p.completed_quests)
    row.unlocked_zones = list(p.unlocked_zones)
    row.equipped_pickaxe = p.equipped_pickaxe
    row.pickaxe_instances = dict(p.pickaxe_instances)
    row.equipped_fishing_rod = p.equipped_fishing_rod
