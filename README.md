# LandonRPG

A Discord RPG bot with turn-based PvE encounters, a co-op dungeon runner, a 1v1 PvP arena, four gathering loops (farming / foraging / mining / fishing), a quest system, a lootbox economy, and a JSON-driven content pipeline. Combat uses D&D-style rolls — d20 to-hit vs AC, weapon-class effects, crits, poise stagger.

Add a stat, weapon, pickaxe, resource, monster, boss, dungeon, or quest by dropping a JSON file in the right folder. Player schema and DB columns adapt automatically on next startup.

---

## Setup

1. **Install dependencies**
   ```
   pip install discord.py sqlalchemy python-dotenv rich
   ```

2. **Create `.env`** in the project root:
   ```
   DISCORD_TOKEN=your_token_here
   ```

3. **Discord Developer Portal** — under your app → **Bot** → **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent**

4. **Run**
   ```
   python main.py
   ```

The SQLite database (`landonrpg.db`) is created on first run; missing columns auto-migrate on startup. Players are created on first command. New players spawn in the Village with a Rusty Sword.

---

## Output style

Every substantive output is a styled Discord embed. Colors and emoji come from intent (success / error / warning / info / lookup / celebration) — never hardcoded in command files. See [CLAUDE.md](CLAUDE.md) for the full styling spec and [landonrpg/style.py](landonrpg/style.py) for the constants.

Short acknowledgements ("Wager locked at 50g.", per-turn battle narration) stay as plain text — embeds are for panels, not streaming flow.

---

## Command Reference

All commands use the `!` prefix. Arguments in `<>` are required; `[]` are optional. Commands are blocked while you're in a PvP / PvE / dungeon battle (the bot tells you which one to forfeit / flee / abandon).

---

### General

| Command | Description |
|---------|-------------|
| `!me` | Full player panel: level, HP, XP, damage, equipped gear (weapon / armor / pickaxe / rod), gold, location, inventory |
| `!ping` | Health check |

---

### Exploration

| Command | Description |
|---------|-------------|
| `!warp <zone name>` | Teleport to a zone by name. Shows a rich overview (monsters, foraging, mining, fishing, dungeon, access gates). |
| `!warp` | List all zones with coordinates |

**Zones:**

| Zone | Coords | Access | Activities |
|------|--------|--------|------------|
| Village | (0,0) | None | Shop • Rest • No combat |
| Forest | (0,1) | None | Orc/Skeleton L1 • Forage • Fish • **Dungeon: Forest Hollow** |
| Damp Cave | (1,0) | Combat L3 | Orc L15 / Skeleton L10 • Forage • **Mining** (stone / copper / iron) |
| Sunlit Meadow | (0,2) | Foraging L2 | Orc L2 • Forage (sunpetal / pumpkin) • Fish |
| Murk Swamp | (1,1) | Combat L5 + Foraging L4 | Skeleton L12 / Orc L8 • Forage • **Mining** (stone / iron / gold / mythril) • Fish |

Players always respawn in the Village when the bot restarts. Zones can be unlocked via quest rewards — those bypass the level gates.

---

### Combat (PvE arena)

| Command | Description |
|---------|-------------|
| `!attack [<monster>]` | Open a turn-based encounter against one monster in the current zone |
| `!fight ...` | Alias for `!attack` |
| `!<weapon_id> <attack_id>` | Make your attack during the encounter (e.g. `!iron_sword slash`) |
| `!<weapon_id> defend` | Brace — the next monster hit does 50% damage; ends your turn |
| `!pve arena` | Show current encounter state |
| `!pve arena flee` | Retreat (no XP, no loot) |

Combat is a one-vs-one turn loop using D&D-style rolls:
- d20 + attack's `to_hit_bonus` + weapon-class modifier vs `AC = 10 + monster defense − class bypass`.
- Natural 20 = crit (extra damage dice). Natural 1 = miss.
- **Poise**: every weapon attack drains poise; reaching 0 staggers the target, restores their poise, and grants the attacker another turn.

**Victory rewards:** `monster.xp_reward × 3` regular XP + `monster.level × 2` combat-skill XP + scaled loot. **Death penalty:** lose 10% gold + one random inventory item, revive in the Village.

Monsters are defined in `json/monsters/<id>.json`. Add a new file, then add a `MonsterSpawn` entry to a zone in `world/zones.py`.

---

### Inventory & Equipment

| Command | Description |
|---------|-------------|
| `!inv` (`!inventory`, `!bag`) | Inventory + equipped gear |
| `!equip <item_id>` | Equip a weapon / armor / pickaxe / fishing rod (checks requirements) |
| `!unequip <slot>` | `!unequip weapon`, `armor`, `pickaxe`, or `fishing_rod` |
| `!use <item_id>` | Use a consumable (potions, edible crops) |
| `!inspect <item_id>` | Item card with type / stats / value / requirements |
| `!rest` | Restore HP — Village only |

**Four equipment slots:** weapon (combat), armor (defense), pickaxe (mining), fishing rod (fishing). Pickaxes and rods can't be used in PvP / PvE.

**Item requirements** support both stat level keys (`combat: 8`) and overall player level (`level: 5`). Mixed requirements all must pass.

**Catalog (partial):**

| Category | Items |
|---|---|
| Weapons (light) | `rusty_sword`, `iron_sword` |
| Weapons (heavy) | `war_axe` |
| Weapons (finesse) | `forager_sickle` |
| Weapons (two-handed) | `dragonslayer`, `harvest_scythe` |
| Armor | `leather_armor`, `iron_armor`, `dragonscale` |
| Pickaxes | `wood_pickaxe`, `iron_pickaxe`, `mythril_pickaxe` |
| Fishing rods | `wood_fishing_rod`, `iron_fishing_rod` |
| Consumables | `small_potion`, `large_potion`, crops with `heal` |
| Junk (sellable) | `bone`, `skull`, `tooth`, `club_fragment` |
| Resources | `stone`, `copper_ore`, `iron_ore`, `gold_ore`, `mythril_chunk` |
| Weapon skills | `power_swing_skill`, `whirlwind_skill`, `parry_strike_skill` |
| Lootboxes | `lootbox_common` through `lootbox_chroma` |

---

### Shop

Requires the Village.

| Command | Description |
|---------|-------------|
| `!shop` | Stock listing with buy prices |
| `!buy <item_id>` | Purchase an item |
| `!sell <item_id> [item_id ...]` | Sell specific items |
| `!sell all` | Sell everything sellable |

The smith stocks: potions, basic weapons + armor (rusty/iron), all three pickaxes, both fishing rods.

---

### Crafting

| Command | Description |
|---------|-------------|
| `!craft recipes [<page>]` | View recipes |
| `!craft <ingredient> [xN] ... [count]` | Craft from a recipe (matches ingredients exactly) |
| `!craft upgrade <item_id>` | **Preview** the next level's cost |
| `!craft upgrade <item_id> <level>` | Advance to that level (must be `current + 1`) |
| `!craft attach <weapon_id> <weapon_skill_id>` | Attach a weapon skill (replaces existing — old skill returns to inventory) |

**Crafting basics.** `xN` after an ingredient means N of that ingredient. A trailing number crafts that many of the result.
```
!craft bone x2 skull         — craft one item requiring 2 bones + 1 skull
!craft bone x2 skull 3       — craft three of that item (uses 6 bones + 3 skulls)
```

**Upgrading.** Every weapon and pickaxe has an instance level (cap 100). Materials are figured out from each item's `upgrade.per_level_materials` JSON block plus the **global tier curve** in [world/upgrade_scaling.py](landonrpg/world/upgrade_scaling.py):

| Tier | Levels | Multiplier | Extra materials per step |
|---|---|---|---|
| Apprentice | 1 → 25 | ×1 | none |
| Adept | 26 → 50 | ×2 | bone × 2 |
| Expert | 51 → 75 | ×3 | skull × 1 |
| Master | 76 → 100 | ×5 | skull × 2 + iron_ore × 1 |

Example progression for Iron Sword (base cost: tooth × 2):

| Step | Cost |
|---|---|
| L1 → L2 (Apprentice) | tooth × 2 |
| L25 → L26 (Adept) | tooth × 4 + bone × 2 |
| L50 → L51 (Expert) | tooth × 6 + skull × 1 |
| L75 → L76 (Master) | tooth × 10 + skull × 2 + iron_ore × 1 |

Run `!craft upgrade iron_sword` (no level) to see the exact cost and the follow-up command for the next step.

**Weapon Skills.** Crafted consumables that add an extra attack to a weapon when attached. Only one skill per weapon — attaching a new one returns the previous one to inventory. Ships with `power_swing_skill`, `whirlwind_skill`, `parry_strike_skill`. Skill attacks become available in PvP, PvE, and dungeons as `!<weapon_id> <skill_attack_id>`.

---

### Farming & Foraging

Loop: **forage seeds → plant → wait → harvest**.

| Command | Description |
|---------|-------------|
| `!forage` | Search the current zone for seeds (30s cooldown; not in Village). +5 foraging XP. |
| `!farm <seed_id> [amount]` | Plant seeds from inventory |
| `!plots` | View all active plots and timers |
| `!harvest` | Collect all fully-grown crops |

**Seed catalog:**

| Seed ID | Farming Lvl | Grow | Yield | Crop | Heal |
|---|---|---|---|---|---|
| `corn_seed` | 1 | 2 min | 2 | Corn | — |
| `wheat_seed` | 1 | 2 min | 3 | Wheat | — |
| `blueberry_seed` | 2 | 3 min | 2 | Blueberry | 5 HP |
| `sunpetal_seed` | 2 | 4 min | 2 | Sunpetal | 4 HP |
| `herb_seed` | 3 | 5 min | 1 | Herbs | 20 HP |
| `pumpkin_seed` | 4 | 8 min | 1 | Pumpkin | 8 HP |
| `moonflower_seed` | 6 | 10 min | 1 | Moonflower | 50 HP |
| `glowmushroom_seed` | 6 | 10 min | 1 | Glowmushroom | 12 HP |

**Yield bonus**: +1 per harvest per 3 Farming levels. **Forage bonus**: +1 extra seed per forage per 4 Foraging levels.

Seed config lives in `json/seeds/<id>.json`.

---

### Mining & Fishing

Both follow the foraging model: instant attempts gated by a 30-second cooldown. Both require a tool equipped (pickaxe for mining, fishing rod for fishing).

| Command | Description |
|---------|-------------|
| `!mine <resource_id> [amount]` | Roll up to N swings against the resource's drop chance. Requires equipped pickaxe. |
| `!fish [amount]` | Cast and pull a weighted catch from the zone's fishing pool. Requires equipped fishing rod. |

**Resource catalog** (`json/resources/<id>.json`):

| Resource | Drop % | Mining Lvl | Pickaxe Tier | Specific Pickaxe |
|---|---|---|---|---|
| `stone` | 80% | 1 | 1 | — |
| `copper_ore` | 55% | 2 | 1 | — |
| `iron_ore` | 40% | 4 | 2 | — |
| `gold_ore` | 25% | 6 | 3 | — |
| `mythril_chunk` | 12% | 9 | 5 | `mythril_pickaxe` (exclusive) |

Each resource auto-registers as an inventory item, so it can be sold, traded, or used in crafting recipes.

**Pickaxe progression**: tiered items (`wood` / `iron` / `mythril`) plus per-instance level (1-100) upgradable via `!craft upgrade`. Effective pickaxe level = `tier + (level - 1) × level_per_step`. The Mythril Chunk requires the `mythril_pickaxe` specifically — pickaxe level alone doesn't unlock it.

**Fishing pools** are defined per zone in `world/zones.py` as weighted catch tables. Forest: blueberry / herb / small_potion. Meadow: sunpetal / blueberry / corn. Swamp: glowmushroom / herb / large_potion.

**Mining bonus**: +1 extra resource per swing per 4 mining levels. **Fishing bonus**: +1 extra catch per cast per 4 fishing levels.

---

### Stats & Milestones

Five skill stats, each tracked independently of player level: **Combat**, **Farming**, **Foraging**, **Mining**, **Fishing**.

| Command | Description |
|---------|-------------|
| `!stats` | List registered stats and command usage |
| `!stats <stat>` | Skill panel: level, XP progress, bonus, next milestone |
| `!stats <stat> <level>` | All milestones at that level + claim status |
| `!stats <stat> <level> claim` | Claim rewards for a reached milestone |
| `!stats claim all` | Claim every eligible reward across all stats |

**Adding a stat is a one-file change.** Edit [world/stats.py](landonrpg/world/stats.py) — append a `StatDefinition` to `DEFINITIONS`. DB columns auto-migrate; Player auto-gains the new attribute; `!stats <new>` works immediately. Drop a `json/unlocks/<name>.json` to give it milestone rewards.

Milestones are defined per stat in `json/unlocks/<stat>.json` and grant XP, gold, items, or zone unlocks. Zone-unlock rewards bypass level gates permanently for that player.

---

### Quests

Manual claim model. Quests stay in `active_quests` until the player runs `!quest claim <id>`.

| Command | Description |
|---------|-------------|
| `!quest` | List Available / Active / Completed quests |
| `!quest <id>` | Start a quest (must meet `requirements`) |
| `!quest progress [<id>]` | Show progress, flag ✅ when ready to claim |
| `!quest claim <id>` | Award rewards (XP / gold / items / unlock_zone) |
| `!quest abandon <id>` | Drop an active quest |

**Four objective types** supported by the engine:

| Type | Tracking | Completion |
|---|---|---|
| `collect_item` | Baseline-relative inventory count | `current - baseline >= amount` |
| `kill_monster` | Counter incremented in PvE victory hook | `count >= amount` |
| `reach_stat_level` | Live check against `<stat>_level` | `level >= target` |
| `visit_zone` | Flag set in `!warp` hook | flag is true |

The collection objective is baseline-relative on purpose: if you already have 7 blueberry seeds when you start "collect 5 blueberry seeds", the quest now needs you to have 12 — five **more** since starting.

Quest config in `json/quests/<id>.json`. Ships with `blueberry_picker`, `orc_slayer`, `dedicated_farmer`, `cave_explorer`, `swamp_pioneer`.

---

### PvP Arena

A 1v1 DM-broadcast duel using the same D&D rolls as PvE.

**Challenge phase (server channel):**
```
!pvp <player>             — DM challenge
!pvp accept               — accept
!pvp decline              — decline
!pvp cancel               — host cancels their own pending challenge
!pvp wager <amount>       — propose gold wager; opponent matches to lock
!pvp public / !pvp private — spectator toggle (default public)
```

**Battle phase (DMs):**
```
!<weapon_id> <attack_id>  — attack on your turn
!<weapon_id> defend       — brace; next hit does 50% damage
!pvp arena                — battle state
!pvp arena forfeit        — surrender (alias: !pvp forfeit) — wager still pays out
```

**Spectating:**
```
!pvp spectate             — list public battles
!pvp spectate <battle_id> — receive battle log via DM
```

**Mechanics:** d20 to-hit + class modifier vs AC = 10 + defense − class bypass. Crit on 20 (extra damage dice). Damage halved if defender used `defend`. Poise break grants an extra turn.

**Weapon classes** (in each weapon's JSON):

| Class | Effect |
|---|---|
| `light` | 25% chance of an extra swing per attack |
| `heavy` | +50% damage vs defense ≥ 5; −2 to-hit |
| `finesse` | +2 to-hit; ignores 2 points of defense |
| `two_handed` | +25% damage; −1 to-hit |
| `ranged` | Ignores half defense; −25% damage |

**Wager**: gold-only. Both sides escrow at battle start; winner takes the full pot — applies on KO **and** on forfeit. Spectators are read-only.

**XP on win**: `75 + 30 × loser.combat_level` regular XP + `3 + loser.combat_level` combat-skill XP.

**Blocked during PvP:** every PvE / farming / foraging / mining / fishing / crafting / quest / dungeon command. Only PvP arena commands work mid-battle.

---

### Dungeons & Lootboxes

One dungeon per zone (one ships in the Forest). Each dungeon has multiple rooms with random enemy counts, escalating toward a final boss room. Co-op up to 5 players.

**Hosting & invites (in a zone channel):**
```
!dungeon                                 — preview the current zone's dungeon
!dungeon <difficulty> [@p1 @p2 ...]     — host a run; invitees have 60s to accept
!dungeon accept / !dungeon decline      — respond to an invite
```

**Difficulties** (multipliers applied to enemy counts and boss HP): `easy 0.7×`, `normal 1.0×`, `hard 1.3×`, `insane 1.6×`, `nightmare 2.0×`, `cataclysm 2.5×`, `abyssal 3.0×`. Party-size also scales: `1 + 0.5 × (party_size - 1)`.

**Inside the run (DM fan-out):**
```
!<weapon_id> <attack_id> [target_index]  — attack on your turn
!<weapon_id> defend                      — brace
!dungeon status                           — show current state
!dungeon abandon                          — leave (HP → 0)
```

**Turn order**: per-round initiative roll (d20 + bonus) for every alive combatant.

**Bosses** are JSON-defined buffed monsters with custom attack lists (`json/bosses/<id>.json`). Attacks support:
- `target_mode: "all"` — AoE that hits every alive party member with a fresh d20 per target
- `summon: {monster_id, amount, level}` — add monsters to the room mid-fight
- Per-event `dialogue` lines (currently rendered for `on_spawn`)

**Lootboxes** drop after every cleared room and after the boss. Each party member gets one box per room. Rarity comes from a fixed-percentage table at [json/lootboxes/drop_tiers.json](landonrpg/json/lootboxes/drop_tiers.json), keyed by `(difficulty, zone_difficulty_band)`. **These percentages never change.** Boss kills shift the roll up by `boss_bonus_rarity_steps`.

Seven rarities, each with its own loot pool (`json/lootboxes/<rarity>.json`): `common`, `uncommon`, `rare`, `epic`, `legendary`, `mythic`, `chroma`. Loot pulls are weighted; each rarity defines pulls-per-box and a gold range. Boxes sit in inventory as `lootbox_<rarity>` items until opened.

**Lootbox commands:**

| Command | Description |
|---------|-------------|
| `!lootbox` | List owned lootboxes by rarity |
| `!lootbox open <rarity>` | Open one of that rarity |
| `!lootbox inspect <rarity>` | Preview the pool (item × weight as percentages) |

---

### Trading

Two-phase DM workflow. `!trade` runs in a server channel; follow-ups happen in DMs.

```
!trade <username>                                       # initiate (server)
!items select <item> <amount> [<item> <amount> ...]     # build offer (DMs)
!items confirm                                          # lock in (DMs)
!items confirm gift                                     # one-way send (DMs)
!items cancel                                           # abort (DMs)
```

Both players' inventories are validated at select-time and again at execution. Both saves run in parallel off the event loop.

---

## Performance notes

- DM fan-out uses `bot.get_user` (in-memory cache) before falling back to `bot.fetch_user` (HTTP). A 4-player dungeon turn used to issue ~32 user-lookup API calls; now it issues ~0.
- All DB writes (autosave after every command, plus explicit cross-player saves on trade, PvP-end, and dungeon-end) run on a worker thread via `asyncio.to_thread`, so SQLAlchemy commits don't block the event loop.
- The dungeon turn-await uses `asyncio.Event` + `wait_for(timeout=60)` instead of a `sleep(1)` polling loop, so player actions take effect immediately.

---

## Project Structure

```
landonrpg/
├── bot.py                 — bot setup, intents, threaded autosave hook
├── db.py                  — SQLAlchemy schema; stat columns auto-generated
├── style.py               — color / emoji / footer constants + embed builders
├── util.py                — get_or_fetch_user, save_player_async
├── main.py                — entry point
├── commands/
│   ├── _helpers.py        — block_during_battle decorator, zone_summary, etc.
│   ├── combat.py          — !attack, PvE arena listener
│   ├── crafting.py        — !craft (recipes / upgrade / attach)
│   ├── dungeon.py         — !dungeon + co-op run loop
│   ├── exploration.py     — !warp
│   ├── farming.py         — !forage, !farm, !harvest, !plots, !stats
│   ├── gathering.py       — !mine, !fish
│   ├── inventory.py       — !inv, !equip, !unequip, !use, !inspect, !me, !rest
│   ├── lootbox.py         — !lootbox group (list / open / inspect)
│   ├── pvp.py             — !pvp + arena listener
│   ├── quests.py          — !quest group
│   ├── shop.py            — !shop, !buy, !sell
│   └── trading.py         — !trade, !items group
├── dungeon/engine.py      — dungeon battle state, initiative, summons
├── pve/engine.py          — single-monster turn engine
├── pvp/engine.py          — duel state, dice, class hooks, weapon-skill resolution
├── quests/engine.py       — start/claim/abandon, objective evaluation, event hooks
├── json/
│   ├── bosses/            — one per boss
│   ├── dungeons/          — one per zone with a dungeon
│   ├── lootboxes/         — per-rarity pools + drop_tiers.json
│   ├── monsters/          — one per monster
│   ├── pickaxes/          — one per pickaxe
│   ├── quests/            — one per quest
│   ├── recipes/           — one per craftable result
│   ├── resources/         — one per mining resource
│   ├── seeds/             — one per seed/crop pair
│   ├── unlocks/           — milestone rewards per stat
│   ├── weapon_skills/     — one per skill token
│   └── weapons/           — one per weapon
├── models/                — Player, Monster, Zone, Entity dataclasses
├── services/players.py    — DB load/save (cached + threaded)
└── world/
    ├── bosses.py          — boss loader
    ├── dungeons.py        — dungeon loader, difficulty multipliers
    ├── items.py           — non-weapon item catalog + missing_requirements
    ├── lootboxes.py       — pool loader, rarity roller, drop tiers
    ├── monsters.py        — spawn() with level scaling
    ├── pickaxes.py        — pickaxe loader + instance helpers
    ├── quests.py          — quest loader
    ├── recipes.py         — crafting recipes
    ├── resources.py       — mining resource loader
    ├── seeds.py           — seed/crop loader (registers items dynamically)
    ├── stats.py           — declarative DEFINITIONS + helpers
    ├── unlocks.py         — milestone loader
    ├── upgrade_scaling.py — global per-level cost tier curve
    ├── weapon_skills.py   — skill token loader
    ├── weapons.py         — weapon loader (registers Item + Weapon config)
    └── zones.py           — zone map + access gates
```

---

## Adding Content

**New monster** — `json/monsters/<id>.json`:
```json
{
  "monster_id": "goblin",
  "name": "Goblin",
  "max_health": 20,
  "damage": 5,
  "attack_msg": "stabs with a rusty knife",
  "xp_reward": 10,
  "loot": ["bone", "tooth"],
  "damage_die": "1d6",
  "to_hit_bonus": 2,
  "defense": 1,
  "poise": 6,
  "poise_break": 1
}
```
Add a `MonsterSpawn("goblin", level=N)` entry to a zone in `world/zones.py`.

**New seed/crop** — `json/seeds/<id>.json`. Auto-registers both the seed item and the crop item.

**New weapon** — `json/weapons/<id>.json`. Auto-registers as an Item with `type="weapon"`, full `Weapon` config (class / attacks / upgrade recipe) lives in the same file.

**New pickaxe** — `json/pickaxes/<id>.json`:
```json
{
  "id": "obsidian_pickaxe",
  "name": "Obsidian Pickaxe",
  "description": "Volcanic-glass edge, sharper than iron.",
  "pickaxe_level": 4,
  "value": 300,
  "requirements": {"mining": 5},
  "upgrade": {
    "max_level": 100,
    "per_level_materials": [{"item": "iron_ore", "amount": 1}],
    "level_per_step": 0.08
  }
}
```

**New resource** — `json/resources/<id>.json`. Auto-registers as an Item so it can be sold / traded / used in recipes:
```json
{
  "id": "ruby",
  "name": "Ruby",
  "description": "A blood-red gem.",
  "value": 100,
  "drop_chance": 8,
  "mining_xp": 40,
  "min_mining_level": 12,
  "min_pickaxe_level": 5,
  "required_pickaxe": ""
}
```
Add the id to a zone's `mining_resources` tuple in `world/zones.py`.

**New weapon skill** — `json/weapon_skills/<id>.json`. Defines a skill item + the attack it grants.

**New quest** — `json/quests/<id>.json`. Pick an `objective.type` from the four supported types.

**New stat** — append a `StatDefinition` to `DEFINITIONS` in [world/stats.py](landonrpg/world/stats.py). That's the entire change:
```python
StatDefinition(
    name="alchemy",
    unit="XP",
    bonus_label="potion potency",
    xp_coeff=20,
    xp_exp=1.4,
)
```
DB columns migrate on next startup, Player gains `alchemy_level` and `alchemy_xp`, `!stats alchemy` works. Drop a `json/unlocks/alchemy.json` to give it milestone rewards. Call `stats.gain_xp(player, "alchemy", n)` from your alchemy commands.

**New dungeon** — `json/dungeons/<zone_id>.json` with `rooms` (each `{enemy_count: [min, max]}`), `spawn_pool`, and `boss_id`.

**New boss** — `json/bosses/<id>.json`. Each attack can declare `target_mode: "all"` for AoE or a `summon` block to spawn mid-fight reinforcements.

**New lootbox rarity** — add a new `json/lootboxes/<rarity>.json` file (must match a new entry in `RARITIES` in [world/lootboxes.py](landonrpg/world/lootboxes.py)) and update `drop_tiers.json` to include the rarity in the percent tables.

---

## Discord intents required

- **Message Content** — for prefix command parsing
- **Server Members** — for `@mention` resolution in `!trade`, `!pvp`, `!dungeon`
