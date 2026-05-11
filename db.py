from sqlalchemy import Column, Integer, String, JSON, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .world import stats as stats_mod

DB_URL = "sqlite:///landonrpg.db"
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
Base = declarative_base()


# Static columns. Stat columns are appended below from world.stats.DEFINITIONS,
# so adding a new stat needs only an entry in stats.py.
_PLAYER_ROW_ATTRS: dict = {
    "__tablename__": "players",
    "user_id":         Column(Integer, primary_key=True),  # Discord user id
    "name":            Column(String, nullable=False),
    "max_health":      Column(Integer, nullable=False),
    "damage":          Column(Integer, nullable=False),
    "health":          Column(Integer, nullable=False),
    "level":           Column(Integer, default=1),
    "xp":              Column(Integer, default=0),
    "inventory":       Column(JSON, default=list),
    "gold":            Column(Integer, default=0),
    "equipped_weapon": Column(String, nullable=True),
    "equipped_armor":  Column(String, nullable=True),
    "x":               Column(Integer, default=0),
    "y":               Column(Integer, default=0),
    "growing_plots":    Column(JSON, default=list),
    "claimed_unlocks":  Column(JSON, default=list),
    "weapon_instances": Column(JSON, default=dict),
    "active_quests":    Column(JSON, default=dict),
    "completed_quests": Column(JSON, default=list),
    "unlocked_zones":   Column(JSON, default=list),
    "equipped_pickaxe": Column(String, nullable=True),
    "pickaxe_instances": Column(JSON, default=dict),
    "equipped_fishing_rod": Column(String, nullable=True),
}

for _d in stats_mod.DEFINITIONS:
    _PLAYER_ROW_ATTRS[_d.resolved_level_attr] = Column(Integer, default=_d.default_level)
    _PLAYER_ROW_ATTRS[_d.resolved_xp_attr]    = Column(Integer, default=_d.default_xp)

PlayerRow = type("PlayerRow", (Base,), _PLAYER_ROW_ATTRS)


# Idempotent ALTER TABLEs for upgrading existing DBs. SQLite raises on duplicate
# columns; we swallow that. Adding a stat appends new ALTERs automatically.
_MIGRATIONS = [
    "ALTER TABLE players ADD COLUMN growing_plots JSON DEFAULT '[]'",
    "ALTER TABLE players ADD COLUMN claimed_unlocks JSON DEFAULT '[]'",
    "ALTER TABLE players ADD COLUMN weapon_instances JSON DEFAULT '{}'",
    "ALTER TABLE players ADD COLUMN active_quests JSON DEFAULT '{}'",
    "ALTER TABLE players ADD COLUMN completed_quests JSON DEFAULT '[]'",
    "ALTER TABLE players ADD COLUMN unlocked_zones JSON DEFAULT '[]'",
    "ALTER TABLE players ADD COLUMN equipped_pickaxe VARCHAR",
    "ALTER TABLE players ADD COLUMN pickaxe_instances JSON DEFAULT '{}'",
    "ALTER TABLE players ADD COLUMN equipped_fishing_rod VARCHAR",
]
for _d in stats_mod.DEFINITIONS:
    _MIGRATIONS.append(
        f"ALTER TABLE players ADD COLUMN {_d.resolved_level_attr} INTEGER DEFAULT {_d.default_level}"
    )
    _MIGRATIONS.append(
        f"ALTER TABLE players ADD COLUMN {_d.resolved_xp_attr} INTEGER DEFAULT {_d.default_xp}"
    )


def init_db():
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        for stmt in _MIGRATIONS:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # column already exists
