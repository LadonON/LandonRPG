# LandonRPG — Content Expansion Design

A complete content plan: 10 zones (plus the Village hub), 10 bosses, 10 dungeons, 45 monsters, 100 weapons, 13 pickaxes, 30 ores, 20 fish, 33 seeds, 180 quests. Built on the schemas in your README.

---

## Design philosophy

- **Tiers drive everything.** 10 tiers map to 10 zones, level ranges 1→50. Weapons, pickaxes, ores, and monsters all index against tier so power curves stay readable.
- **Each zone has a job.** Every zone is built around 1–3 of: combat, foraging, mining, fishing, lore. No zone tries to do all five — they each have a personality.
- **Existing content stays.** Your current zones (Forest, Sunlit Meadow, Damp Cave, Murk Swamp), weapons, seeds, pickaxes, ores, and monsters are kept as Tier 1–3 content and extended outward.
- **Bosses each have a hook.** No "big monster with more HP." Every boss has one mechanic that makes it different (summons, AoE, phase shift, environmental trick).
- **Quest variety per zone.** Mix of kill / collect / reach-stat / visit / story chains so no zone feels grindy.

---

## World map — tier-by-tier

| Tier | Zone | Coords | Level Range | Primary Loops | Boss |
|------|------|--------|-------------|---------------|------|
| 0 | **Village** | (0,0) | — | Hub: shop, rest, craft | — |
| 1 | Whispering Forest | (0,1) | 1–3 | Combat, foraging, fishing | Mossback Ogre |
| 2 | Sunlit Meadow | (0,2) | 3–5 | Foraging, fishing | Queen Pollenwing |
| 3 | Damp Cave | (1,0) | 5–8 | Combat, mining | Stonefist Troll |
| 4 | Murk Swamp | (1,1) | 8–12 | All four loops | Bogfather |
| 5 | Ashfall Plateau | (2,1) | 12–17 | Combat, mining | Magmaw the Sundering |
| 6 | Frostbound Peaks | (2,2) | 17–22 | Mining, fishing | Glacien, Frostfanged |
| 7 | Tidewreck Reef | (3,1) | 22–28 | Fishing, combat | Krakora, Tide-Spawn |
| 8 | Hollow Marches | (3,2) | 28–35 | Combat, foraging | The Hollowed King |
| 9 | Stormvault Citadel | (4,2) | 35–42 | Combat, mining | Volthrax the Unbound |
| 10 | Skyforge Crucible | (4,3) | 42–50 | Combat only | Astralith, Forgegod |

Access gates suggest a primary route (forest → meadow OR cave → swamp → ashfall → …) but quest unlocks can skip stat gates as before.

---

## Zones

### `village` — Tier 0 (hub)
**Coords:** (0,0) • **Access:** none • **Combat:** disabled
Smith, alchemist, board of contracts. Respawn point. Existing behaviour preserved.

### `whispering_forest` — Tier 1
**Coords:** (0,1) • **Level:** 1–3 • **Access:** none
**Theme:** Sun-dappled woodland on the edge of civilization. The first place players learn to fight.
**Monsters:** young_orc (L1), forest_wolf (L1), forest_skeleton (L2), giant_spider (L3)
**Foraging:** blueberry_seed, herb_seed, sunpetal_seed
**Fishing pool:** river_minnow 60% / bluegill 30% / forest_perch 10%
**Boss:** Mossback Ogre • **Dungeon:** Forest Hollow

### `sunlit_meadow` — Tier 2
**Coords:** (0,2) • **Level:** 3–5 • **Access:** Foraging 2
**Theme:** Open grassland and wildflower fields. Soft-locked behind foraging because it rewards it.
**Monsters:** meadow_orc (L3), honey_drake (L4), pollen_wisp (L5)
**Foraging:** sunpetal_seed, pumpkin_seed, corn_seed, carrot_seed
**Fishing pool:** sunfish 55% / golden_carp 35% / meadow_eel 10%
**Boss:** Queen Pollenwing • **Dungeon:** Hive of the Sun-Queen

### `damp_cave` — Tier 3
**Coords:** (1,0) • **Level:** 5–8 • **Access:** Combat 3
**Theme:** Wet limestone tunnels. The first mining zone.
**Monsters:** cave_orc (L6), cave_skeleton (L7), bat_swarm (L5), kobold_miner (L8)
**Mining:** stone, copper_ore, tin_ore, iron_ore
**Fishing pool:** blind_eel 60% / glow_shrimp 30% / cave_grouper 10%
**Boss:** Stonefist Troll • **Dungeon:** The Sunken Vein

### `murk_swamp` — Tier 4
**Coords:** (1,1) • **Level:** 8–12 • **Access:** Combat 5 + Foraging 4
**Theme:** Bog, rot, and old magic. The midgame pivot — all four gathering loops are present.
**Monsters:** swamp_skeleton (L10), bog_orc (L11), mire_serpent (L9), will_o_wisp (L12), gator_brute (L12)
**Foraging:** mandrake_seed, moonflower_seed, glowmushroom_seed, foxglove_seed
**Mining:** iron_ore, coal, gold_ore, mythril_chunk
**Fishing pool:** mudpike 40% / bog_leech 30% / glowfin 20% / swamp_pike 10%
**Boss:** Bogfather • **Dungeon:** Cradle of Rot

### `ashfall_plateau` — Tier 5
**Coords:** (2,1) • **Level:** 12–17 • **Access:** Combat 10 + Mining 6
**Theme:** Scorched volcanic flats, slow-flowing lava channels, basalt columns.
**Monsters:** cinder_imp (L13), ash_walker (L14), molten_golem (L16), salamander_lord (L17), pyre_orc (L15)
**Mining:** obsidian, volcanic_shard, sulfur_chunk, cobalt_ore
**Fishing pool:** magmacarp 70% / ashfin 25% / lavakraken_spawn 5% (lava pools)
**Foraging:** ashpetal_seed, dragonweed_seed
**Boss:** Magmaw the Sundering • **Dungeon:** Heart of the Caldera

### `frostbound_peaks` — Tier 6
**Coords:** (2,2) • **Level:** 17–22 • **Access:** Combat 14 + Foraging 10
**Theme:** Glaciated mountain spine. Wind, ice caves, snow-buried ruins.
**Monsters:** frost_wolf (L18), ice_revenant (L19), yeti_brute (L20), snow_witch (L21), glacial_drake (L22)
**Mining:** frostsilver, iceshard, glacial_crystal, silver_ore
**Fishing pool:** ice_salmon 55% / glacier_trout 35% / frozen_pike 10%
**Foraging:** frostberry_seed, icebloom_seed, mooncress_seed, silverleaf_seed
**Boss:** Glacien, Frostfanged • **Dungeon:** The Throne of Hoar

### `tidewreck_reef` — Tier 7
**Coords:** (3,1) • **Level:** 22–28 • **Access:** Combat 18 + Fishing 10
**Theme:** Half-submerged shipwrecks, coral spires, abyss trenches.
**Monsters:** reef_drowner (L23), siren_thrall (L24), tide_skeleton (L25), shark_brood (L26), kraken_hatchling (L28)
**Mining:** pearl_coral, seabed_quartz, abyssal_stone, salt_crystal
**Fishing pool:** deepsquid 40% / anglerfish 30% / kraken_spawn 20% / sunken_relic 10%
**Foraging:** kelp_seed, coral_seed
**Boss:** Krakora, Tide-Spawn • **Dungeon:** The Drowned Cathedral

### `hollow_marches` — Tier 8
**Coords:** (3,2) • **Level:** 28–35 • **Access:** Combat 22 + Foraging 16
**Theme:** Cursed plains and bone forests, mist that drinks the light. Where dead kings dream.
**Monsters:** hollow_knight (L29), wraith (L30), bone_collector (L31), grave_orc (L32), lich_acolyte (L34)
**Mining:** soulstone, bonemarble, shadowsteel, cursed_iron
**Fishing pool:** bonefish 60% / cursed_catch 30% / spectralfin 10%
**Foraging:** bonebloom_seed, soulroot_seed, shadowmoss_seed, nightshade_seed
**Boss:** The Hollowed King • **Dungeon:** The Marrow Keep

### `stormvault_citadel` — Tier 9
**Coords:** (4,2) • **Level:** 35–42 • **Access:** Combat 28 + Mining 22
**Theme:** Sky-fortress wrapped in perpetual storm. Tesla-coil corridors, levitating platforms.
**Monsters:** storm_sentinel (L36), thunderkin (L37), arc_construct (L39), storm_giant (L41)
**Mining:** stormsteel, voltite, skyiron, adamantite
**Fishing pool:** voltcatfish 100% (lightning ponds — rare encounter)
**Foraging:** stormvine_seed, voltflower_seed
**Boss:** Volthrax the Unbound • **Dungeon:** The Tempest Spire

### `skyforge_crucible` — Tier 10
**Coords:** (4,3) • **Level:** 42–50 • **Access:** Combat 36 + clear all prior bosses
**Theme:** A forge between worlds. Where gods anneal reality. Endgame.
**Monsters:** crucible_warden (L43), star_revenant (L45), void_herald (L47), forgewraith (L48)
**Mining:** celestium, stardust, voidstone, sunstone, moonstone, aether_crystal
**Fishing pool:** starwhale 100% (rare singular catch from celestial pools)
**Foraging:** starbloom_seed, godsblood_seed, celestial_lily_seed
**Boss:** Astralith, Forgegod • **Dungeon:** The Anvil at the End

---

## Bosses

Every boss has one signature mechanic beyond raw stats. Boss HP scales with party size per your existing dungeon scaler.

### `mossback_ogre` — Tier 1
**HP:** 80 • **DMG die:** 1d10+2 • **Poise:** 20
**Mechanic — Earthquake Stomp:** Every 3rd turn, AoE on all party members (`target_mode: "all"`, 1d6 damage). Lore: an ogre old enough that moss has grown into the cracks of its hide.

### `queen_pollenwing` — Tier 2
**HP:** 140 • **DMG die:** 1d8 • **Poise:** 24
**Mechanic — Hive Call:** At 50% HP, summons 2× `pollen_wisp` (L4) once. Drops `honey_essence` for crafting.

### `stonefist_troll` — Tier 3
**HP:** 240 • **DMG die:** 2d8+1 • **Poise:** 35
**Mechanic — Stone Skin:** Defense doubles below 30% HP for one phase. Stagger-bait fight; encourages two-handed weapons.

### `bogfather` — Tier 4
**HP:** 420 • **DMG die:** 2d8+3 • **Poise:** 40
**Mechanic — Drowning Mist:** AoE poison every 4 turns. Summons `mire_serpent` (L9) twice per fight. Drops `bogfather_heart` (unique crafting reagent for Murk-tier weapons).

### `magmaw_the_sundering` — Tier 5
**HP:** 720 • **DMG die:** 3d6+4 • **Poise:** 50
**Mechanic — Eruption Phase:** At 50% HP, swaps to all-AoE attacks for 3 turns (2d6 to all). Vulnerable while in this phase (defense −3).

### `glacien_frostfanged` — Tier 6
**HP:** 1100 • **DMG die:** 3d8+2 • **Poise:** 60
**Mechanic — Glacial Lock:** On crit hit, skips target's next turn (1 turn freeze). Drops `frostfang` shard, prereq for tier-6 finesse weapons.

### `krakora_tide_spawn` — Tier 7
**HP:** 1800 • **DMG die:** 3d10+3 • **Poise:** 75
**Mechanic — Tentacle Adds:** Spawns 4× `kraken_tendril` (L24) at 75%, 50%, 25% HP. Tendrils have 60 HP each and disappear at next phase.

### `the_hollowed_king` — Tier 8
**HP:** 2800 • **DMG die:** 4d8+4 • **Poise:** 90
**Mechanic — Soul Drain:** Standard attacks heal him for 25% of damage dealt. Designed to punish parties that don't focus down. Drops `crown_shard`.

### `volthrax_the_unbound` — Tier 9
**HP:** 4200 • **DMG die:** 4d10+5 • **Poise:** 110
**Mechanic — Chain Lightning:** Every 3rd turn, chains damage across all alive party members (full damage to first target, 50% to next, 25% to third). Position-of-turn-order matters.

### `astralith_forgegod` — Tier 10
**HP:** 7500 • **DMG die:** 5d10+8 • **Poise:** 150
**Mechanic — Three Anvils:** Three phases at 75%/50%/25% HP, each granting a new attack: Anvil of Flame (AoE 4d6), Anvil of Frost (single target freeze), Anvil of Sky (chain lightning + summon). Drops `forgegod_essence` (sole source for Tier-10 weapon crafting).

---

## Dungeons

Each dungeon has rooms with random enemy counts followed by the boss room. Counts are `[min, max]` per the engine.

| ID | Zone | Rooms | Spawn Pool | Boss |
|---|---|---|---|---|
| `forest_hollow` | whispering_forest | 3× `[1,2]` → boss | young_orc, forest_wolf, forest_skeleton | mossback_ogre |
| `hive_of_the_sun_queen` | sunlit_meadow | 3× `[2,3]` → boss | meadow_orc, honey_drake, pollen_wisp | queen_pollenwing |
| `the_sunken_vein` | damp_cave | 4× `[2,3]` → boss | cave_orc, cave_skeleton, kobold_miner, bat_swarm | stonefist_troll |
| `cradle_of_rot` | murk_swamp | 4× `[2,4]` → boss | swamp_skeleton, mire_serpent, will_o_wisp, gator_brute | bogfather |
| `heart_of_the_caldera` | ashfall_plateau | 5× `[2,4]` → boss | cinder_imp, ash_walker, salamander_lord, pyre_orc | magmaw_the_sundering |
| `the_throne_of_hoar` | frostbound_peaks | 5× `[3,4]` → boss | frost_wolf, ice_revenant, yeti_brute, snow_witch | glacien_frostfanged |
| `the_drowned_cathedral` | tidewreck_reef | 6× `[3,5]` → boss | reef_drowner, siren_thrall, tide_skeleton, shark_brood | krakora_tide_spawn |
| `the_marrow_keep` | hollow_marches | 6× `[3,5]` → boss | hollow_knight, wraith, bone_collector, grave_orc | the_hollowed_king |
| `the_tempest_spire` | stormvault_citadel | 7× `[4,5]` → boss | storm_sentinel, thunderkin, arc_construct | volthrax_the_unbound |
| `the_anvil_at_the_end` | skyforge_crucible | 8× `[4,6]` → boss | crucible_warden, star_revenant, void_herald, forgewraith | astralith_forgegod |

---

## Endgame Dungeon: The Crucible of Reckoning

**Difficulty:** Impossible (intended for coordinated 5-player teams at level 48–50, fully geared)

**Access:** Skyforge Crucible zone, after defeating Astralith in main story. Separate from the standard `the_anvil_at_the_end` dungeon.

### Layout

The Crucible of Reckoning is a **gauntlet dungeon** with escalating difficulty and no breaks between rooms. Party composition matters heavily here.

| Room | Enemies | Enemy Count | Notes |
|---|---|---|---|
| 1 | arc_construct, storm_giant | [3, 4] | Warm-up room; still lethal if unprepared |
| 2 | forgewraith × 2, void_herald | [2, 3] | Damage checks; no room for mistakes |
| 3 | crucible_warden × 3 | [3, 3] | Tanking test; punishes poor positioning |
| 4 | star_revenant × 2, void_herald × 1, forgewraith × 1 | [4, 4] | Chaotic room; adds spawn as prior adds die |
| 5 | **Sun Eater** (boss) | [1, 1] | Deus ex machina fight; auto-scale to party size |

**Party size scaling:** Each room's enemy count is `base + (0.3 × (party_size - 1))`, rounded down. A 3-person party faces [2,3] in room 1; a 5-person party faces [3,4].

**Respawning:** No mid-dungeon respawn. Once a player drops, they're out until the boss is cleared or the dungeon wipe occurs. A full-party wipe (everyone KO) resets the dungeon to room 1.

---

### Boss: Sun Eater

**HP:** 800 (does not scale with party size — the fight is about mechanics, not raw damage)  
**DMG die:** 5d12+10 base (varies per attack)  
**Poise:** 200 (massive poise pool to prevent easy stagger-loops)  
**Defense:** 8

**Attacks & Turn Structure:**

Sun Eater uses a **6-turn cycle** that repeats. Each turn is either a single attack or a multi-target sequence. Initiative matters; Sun Eater acts after the party's fastest member each round.

#### Turn 1: **Consuming Rays** (AoE, unavoidable)
- Target: all party members
- Damage: 3d8 to each
- Effect: each hit party member gains a stack of `Consumed` (max 5 stacks). At end of Sun Eater's next turn, if any member has ≥3 stacks, Sun Eater heals 25 HP per stack total and **resets all stacks to 0**.
- Strategy: Party must coordinate to heal/cleanse or burst before the heal triggers.

#### Turn 2: **Photon Lash** (single target, repeats)
- Sun Eater targets the party member with the **lowest max HP**.
- Damage: 4d10+5
- Effect: target is `Blinded` (all attacks have −3 to-hit) for 2 turns.
- Must use `defend` or die; designed to punish glass cannons.

#### Turn 3: **Solar Flare** (delayed AoE)
- Sun Eater announces: "The sky fractures!"
- No immediate damage. At the **end of this turn**, all party members take 2d10 damage. Party has one turn to either: (a) attack Sun Eater ≥100 total damage to "cool" the flare, or (b) use `defend` to halve the damage.
- If the flare isn't "cooled," it triggers the next turn with +50% damage (3d10 instead of 2d10).
- Flares stack if ignored.

#### Turn 4: **Radiant Collapse** (phase mechanic)
- Sun Eater pulls all party members toward the center of the arena (no escape).
- Damage: 2d12 to all party members
- Effect: party is `Stunned` (lose next turn) unless they succeed a "break stun" check: deal ≥80 damage to Sun Eater **this turn** (before the stun resolves). Only ONE party member can attempt this per Collapse.
- If no one attempts/succeeds, entire party is stunned and loses turn 5 (giving Sun Eater a free turn 5 attack).

#### Turn 5: **Incandescent Barrage** (multi-attack)
- Sun Eater rapidly attacks the **two party members with the highest defense** (5 times each, one attack per member per round, rolling initiative each time — very chaotic).
- Damage per hit: 2d8+3
- Party that's been coordinating high-defense tank rotation lives; party that hasn't gets overwhelmed.
- This turn takes ~30 seconds of real time to resolve if there are contested targets.

#### Turn 6: **Cataclysm** (massive AoE)
- Damage: 5d10 to all party members
- Effect: all active buffs/debuffs on party members are **wiped** (including Blinded, Stunned, heals-over-time).
- This is essentially Sun Eater's reset button; everything resets and cycle begins again.

---

### Boss Mechanics Summary

**Difficulty spikes:**
- **Healing puzzle** (Turn 1): Party must coordinate to either burst 25+ HP in a turn (hard) or have cleanse/heal available.
- **Glass cannon punishment** (Turn 2): Rogue/ranged players are specifically targeted and blinded. Encourages hybrid builds.
- **DPS check** (Turn 3): If party can't consistently deal 100 DPS, Solar Flare damage compounds and kills over time.
- **Stun breaking** (Turn 4): One party member MUST break focus from regular attacks to focus-fire 80 damage in one turn. Requires build diversity.
- **Tanking skill** (Turn 5): Tanks need high defense AND high poise to survive 10 rapid hits. Squishy tanks die.
- **Hard reset** (Turn 6): All coordination wiped. Party must restart buff management. Discourages pre-buffing strategies.

**Win condition:**  
Deal 800 damage total before party is wiped. No DPS race; mechanical mastery is the gate. Average party should kill in 4–5 full cycles (24–30 turns) if executing mechanics perfectly.

**Loot upon victory:**  
Each party member receives one random drop from the Sun Eater loot pool (see below). Plus a guaranteed `crucible_triumph_token` × 1 per party member (currency for crafting exclusive weapons).

---

## Sun Eater Exclusive Loot Pool

These items drop **only** from Sun Eater, nowhere else in the game.

| ID | Name | Rarity | Type | Effect / Flavor |
|---|---|---|---|---|
| `sunburst_core` | Sunburst Core | Mythic | Crafting material | Sole material for Sun Eater's Light (unique tier-10 sword); radiates heat |
| `photon_shard` | Photon Shard | Legendary | Crafting material | Component for light-based weapons; bends light visibly |
| `stellar_essence` | Stellar Essence | Legendary | Crafting material | Essence of a star made manifest; required for tier-9+ cosmetic glow effects |
| `corona_circlet` | Corona Circlet | Epic | Head cosmetic | Glowing halo above head; no combat bonus; pure prestige |
| `incandescent_vial` | Incandescent Vial | Epic | Consumable (one-time) | Restores ALL party members to full HP + mana instantly; single-use |
| `blinding_powder` | Blinding Powder` | Rare | Consumable (stackable) | Blinds enemies for 2 turns; crafting material for stealth builds |
| `sun_eater_trophy_head` | Sun Eater Trophy Head | Mythic | Head cosmetic | Legendary bragging rights; intimidates NPCs in lore (no mechanical effect) |
| `eternal_flame` | Eternal Flame | Legendary | Crafting material | Unquenchable flame; fuel for fire-elemental weapon recipes; never burns out |
| `radiant_blessing` | Radiant Blessing | Mythic | Quest item / cosmetic | Blessing of the sun itself; grants +5 HP/turn regeneration for 24 real hours after obtaining |
| `eclipse_stone` | Eclipse Stone | Epic | Crafting material | Paradox material; shadow within light; combines with stellar_essence for unique weapons |

**Drop rate:** Each victory drops 5 random items (one per party member), weighted:
- Sunburst Core: 15% per slot
- Photon Shard: 20% per slot
- Stellar Essence: 20% per slot
- Corona Circlet: 10% per slot
- Incandescent Vial: 10% per slot
- Blinding Powder: 10% per slot
- Sun Eater Trophy Head: 5% per slot (prestige; super rare)
- Eternal Flame: 5% per slot
- Radiant Blessing: 3% per slot (rarest)
- Eclipse Stone: 2% per slot

**Crafting unlock:** First time a player obtains `sunburst_core`, a new recipe unlocks: **Sun Eater's Light** (unique tier-10 sword, requires sunburst_core + godly_fragment + crucible_triumph_token, grants +3 light damage, +15% crit chance, glows blindingly white).

---

## Crucible of Reckoning Progression Rewards

Beyond loot drops, defeating Sun Eater grants:
- **Crucible Triumph Token** ×1 per party member (tradeable currency; can be traded to NPC "Forge Master Solus" for cosmetics or weapon-leveling materials)
- **Title unlock:** "[Player] Eater of the Sun" (cosmetic title)
- **Achievement:** "Impossible Task" (hidden achievement; triggers other NPC dialogue changes)
- **Repeatable weekly:** Can run the dungeon once per week for loot reset (Tuesdays at reset); beyond once weekly, bosses drop nothing and serve as a training dummy

---

## Monsters (45)

Listed once each. Same monster can spawn at different levels in different zones via `MonsterSpawn(level=…)`.

| # | ID | Tier | HP | DMG die | Defense | Poise | Loot |
|---|---|---|---|---|---|---|---|
| 1 | `young_orc` | 1 | 18 | 1d6 | 0 | 4 | bone, tooth |
| 2 | `forest_wolf` | 1 | 14 | 1d6+1 | 0 | 3 | wolf_pelt, tooth |
| 3 | `forest_skeleton` | 1 | 16 | 1d6 | 1 | 5 | bone, skull |
| 4 | `giant_spider` | 1 | 22 | 1d8 | 1 | 4 | spider_silk, fang |
| 5 | `meadow_orc` | 2 | 28 | 1d8 | 1 | 6 | bone, club_fragment |
| 6 | `honey_drake` | 2 | 32 | 1d8+1 | 2 | 6 | drake_scale, honey_essence |
| 7 | `pollen_wisp` | 2 | 18 | 1d6+1 | 0 | 3 | sunpetal_seed, glow_dust |
| 8 | `cave_orc` | 3 | 48 | 1d10 | 2 | 8 | bone, club_fragment, stone |
| 9 | `cave_skeleton` | 3 | 42 | 1d8+1 | 2 | 7 | bone, skull, rusted_blade |
| 10 | `bat_swarm` | 3 | 26 | 1d6 (×2) | 0 | 4 | bat_wing, glow_dust |
| 11 | `kobold_miner` | 3 | 40 | 1d8 | 2 | 6 | copper_ore, stone, pickaxe_fragment |
| 12 | `swamp_skeleton` | 4 | 70 | 2d6 | 3 | 10 | bone, skull, swamp_essence |
| 13 | `bog_orc` | 4 | 90 | 2d6+1 | 3 | 12 | club_fragment, swamp_essence |
| 14 | `mire_serpent` | 4 | 60 | 2d6+2 | 2 | 8 | serpent_scale, venom_sac |
| 15 | `will_o_wisp` | 4 | 40 | 1d10 | 1 | 6 | glow_dust, soul_fragment |
| 16 | `gator_brute` | 4 | 110 | 2d8 | 4 | 14 | gator_hide, fang |
| 17 | `cinder_imp` | 5 | 80 | 2d6+2 | 3 | 9 | sulfur_chunk, imp_horn |
| 18 | `ash_walker` | 5 | 130 | 2d8 | 4 | 12 | ash_dust, bone |
| 19 | `molten_golem` | 5 | 220 | 2d8+3 | 6 | 18 | obsidian, molten_core |
| 20 | `salamander_lord` | 5 | 160 | 2d10 | 4 | 14 | salamander_hide, fire_gland |
| 21 | `pyre_orc` | 5 | 180 | 2d8+2 | 4 | 14 | club_fragment, cinder_brand |
| 22 | `frost_wolf` | 6 | 200 | 2d8+2 | 4 | 14 | frost_pelt, fang |
| 23 | `ice_revenant` | 6 | 220 | 2d10 | 5 | 16 | revenant_dust, iceshard |
| 24 | `yeti_brute` | 6 | 320 | 2d10+2 | 6 | 20 | yeti_fur, frost_bone |
| 25 | `snow_witch` | 6 | 180 | 3d6+2 | 4 | 12 | hex_charm, mooncress_seed |
| 26 | `glacial_drake` | 6 | 380 | 3d8 | 7 | 22 | drake_scale, glacial_crystal |
| 27 | `reef_drowner` | 7 | 280 | 3d6+2 | 5 | 16 | drowner_pearl, kelp |
| 28 | `siren_thrall` | 7 | 240 | 3d6+3 | 4 | 14 | siren_voice, scale |
| 29 | `tide_skeleton` | 7 | 320 | 3d8 | 6 | 18 | bone, skull, salt_crystal |
| 30 | `shark_brood` | 7 | 360 | 3d8+2 | 6 | 18 | shark_fang, shark_hide |
| 31 | `kraken_hatchling` | 7 | 460 | 3d10 | 7 | 22 | kraken_tendril, abyssal_stone |
| 32 | `hollow_knight` | 8 | 480 | 3d8+3 | 7 | 22 | cursed_iron, knight_sigil |
| 33 | `wraith` | 8 | 360 | 3d10 | 5 | 18 | soul_fragment, shadowsteel |
| 34 | `bone_collector` | 8 | 520 | 4d6+2 | 8 | 24 | bonemarble, skull |
| 35 | `grave_orc` | 8 | 580 | 3d10+2 | 8 | 24 | club_fragment, soulstone |
| 36 | `lich_acolyte` | 8 | 440 | 4d6+3 | 6 | 20 | lich_phylactery, dark_tome |
| 37 | `storm_sentinel` | 9 | 680 | 4d8 | 9 | 26 | stormsteel, sentinel_core |
| 38 | `thunderkin` | 9 | 600 | 4d8+2 | 8 | 24 | voltite, lightning_rod |
| 39 | `arc_construct` | 9 | 820 | 4d8+3 | 11 | 30 | skyiron, arc_capacitor |
| 40 | `storm_giant` | 9 | 1100 | 4d10+3 | 10 | 32 | giant_femur, stormsteel |
| 41 | `crucible_warden` | 10 | 1300 | 5d8+3 | 12 | 34 | celestium, warden_plate |
| 42 | `star_revenant` | 10 | 1100 | 5d8+4 | 10 | 30 | stardust, soul_fragment |
| 43 | `void_herald` | 10 | 1400 | 5d10 | 11 | 32 | voidstone, herald_eye |
| 44 | `forgewraith` | 10 | 1600 | 5d10+3 | 13 | 36 | aether_crystal, wraith_dust |
| 45 | `kraken_tendril` | 7 | 60 | 2d6+2 | 4 | 12 | (boss add — no loot) |

---

## Weapons (100)

20 per class × 5 classes. Two weapons per class per tier; one usually "fast / lower damage" and one "slow / higher damage" variant.

### Light (20)

| ID | Name | Tier | Level Req | Class Effect |
|---|---|---|---|---|
| `rusty_sword` | Rusty Sword | 1 | 1 | light |
| `hunter_dagger` | Hunter's Dagger | 1 | 2 | light |
| `iron_sword` | Iron Sword | 2 | 3 | light |
| `meadow_shortsword` | Meadow Shortsword | 2 | 4 | light |
| `steel_sword` | Steel Sword | 3 | 5 | light |
| `cave_kris` | Cave Kris | 3 | 7 | light |
| `marsh_blade` | Marsh Blade | 4 | 9 | light |
| `bogfather_fang` | Bogfather's Fang | 4 | 11 | light |
| `ashforged_sword` | Ashforged Sword | 5 | 13 | light |
| `cinder_dagger` | Cinder Dagger | 5 | 16 | light |
| `frostbite_blade` | Frostbite Blade | 6 | 18 | light |
| `hoarsteel_sword` | Hoarsteel Sword | 6 | 21 | light |
| `coral_kris` | Coral Kris | 7 | 23 | light |
| `tideborn_sword` | Tideborn Sword | 7 | 26 | light |
| `hollow_blade` | Hollow Blade | 8 | 29 | light |
| `marrow_dagger` | Marrow Dagger | 8 | 33 | light |
| `stormcut_sword` | Stormcut Sword | 9 | 36 | light |
| `voltsteel_dagger` | Voltsteel Dagger | 9 | 40 | light |
| `skyborn_sword` | Skyborn Sword | 10 | 43 | light |
| `forgegod_blade` | Forgegod Blade | 10 | 48 | light |

### Heavy (20)

| ID | Name | Tier | Level Req | Class Effect |
|---|---|---|---|---|
| `crude_club` | Crude Club | 1 | 1 | heavy |
| `bone_mace` | Bone Mace | 1 | 2 | heavy |
| `war_axe` | War Axe | 2 | 3 | heavy |
| `meadow_maul` | Meadow Maul | 2 | 4 | heavy |
| `steel_warhammer` | Steel Warhammer | 3 | 5 | heavy |
| `stonefist_mace` | Stonefist Mace | 3 | 7 | heavy |
| `swamp_maul` | Swamp Maul | 4 | 9 | heavy |
| `mirewrought_axe` | Mirewrought Axe | 4 | 11 | heavy |
| `ashforged_maul` | Ashforged Maul | 5 | 13 | heavy |
| `volcanic_warhammer` | Volcanic Warhammer | 5 | 16 | heavy |
| `frostbound_axe` | Frostbound Axe | 6 | 18 | heavy |
| `glacien_maul` | Glacien Maul | 6 | 21 | heavy |
| `coralfall_axe` | Coralfall Axe | 7 | 23 | heavy |
| `abyssal_warhammer` | Abyssal Warhammer | 7 | 26 | heavy |
| `hollow_maul` | Hollow Maul | 8 | 29 | heavy |
| `bonecrown_axe` | Bonecrown Axe | 8 | 33 | heavy |
| `stormbreaker_maul` | Stormbreaker Maul | 9 | 36 | heavy |
| `tempest_warhammer` | Tempest Warhammer | 9 | 40 | heavy |
| `skyforge_maul` | Skyforge Maul | 10 | 43 | heavy |
| `godsteel_warhammer` | Godsteel Warhammer | 10 | 48 | heavy |

### Finesse (20)

| ID | Name | Tier | Level Req | Class Effect |
|---|---|---|---|---|
| `forager_sickle` | Forager's Sickle | 1 | 1 | finesse |
| `hunter_rapier` | Hunter's Rapier | 1 | 2 | finesse |
| `iron_rapier` | Iron Rapier | 2 | 3 | finesse |
| `meadow_sickle` | Meadow Sickle | 2 | 4 | finesse |
| `cave_estoc` | Cave Estoc | 3 | 5 | finesse |
| `kobold_dirk` | Kobold Dirk | 3 | 7 | finesse |
| `marsh_rapier` | Marsh Rapier | 4 | 9 | finesse |
| `serpent_fang` | Serpent Fang | 4 | 11 | finesse |
| `cinder_estoc` | Cinder Estoc | 5 | 13 | finesse |
| `ashforged_rapier` | Ashforged Rapier | 5 | 16 | finesse |
| `frostfang_rapier` | Frostfang Rapier | 6 | 18 | finesse |
| `glacial_estoc` | Glacial Estoc | 6 | 21 | finesse |
| `coral_rapier` | Coral Rapier | 7 | 23 | finesse |
| `tideborn_estoc` | Tideborn Estoc | 7 | 26 | finesse |
| `hollow_rapier` | Hollow Rapier | 8 | 29 | finesse |
| `marrow_estoc` | Marrow Estoc | 8 | 33 | finesse |
| `stormpiercer` | Stormpiercer | 9 | 36 | finesse |
| `voltsteel_rapier` | Voltsteel Rapier | 9 | 40 | finesse |
| `skyborn_estoc` | Skyborn Estoc | 10 | 43 | finesse |
| `forgegod_rapier` | Forgegod Rapier | 10 | 48 | finesse |

### Two-handed (20)

| ID | Name | Tier | Level Req | Class Effect |
|---|---|---|---|---|
| `harvest_scythe` | Harvest Scythe | 1 | 1 | two_handed |
| `dragonslayer` | Dragonslayer | 1 | 2 | two_handed |
| `iron_greatsword` | Iron Greatsword | 2 | 3 | two_handed |
| `meadow_glaive` | Meadow Glaive | 2 | 4 | two_handed |
| `steel_greatsword` | Steel Greatsword | 3 | 5 | two_handed |
| `troll_breaker` | Trollbreaker | 3 | 7 | two_handed |
| `swamp_scythe` | Swamp Scythe | 4 | 9 | two_handed |
| `bogfather_glaive` | Bogfather Glaive | 4 | 11 | two_handed |
| `ashforged_greatsword` | Ashforged Greatsword | 5 | 13 | two_handed |
| `magma_scythe` | Magma Scythe | 5 | 16 | two_handed |
| `glacial_greatsword` | Glacial Greatsword | 6 | 18 | two_handed |
| `frostfang_glaive` | Frostfang Glaive | 6 | 21 | two_handed |
| `tideborn_glaive` | Tideborn Glaive | 7 | 23 | two_handed |
| `abyssal_greatsword` | Abyssal Greatsword | 7 | 26 | two_handed |
| `hollow_scythe` | Hollow Scythe | 8 | 29 | two_handed |
| `marrow_greatsword` | Marrow Greatsword | 8 | 33 | two_handed |
| `stormcaller_glaive` | Stormcaller Glaive | 9 | 36 | two_handed |
| `tempest_greatsword` | Tempest Greatsword | 9 | 40 | two_handed |
| `skyborn_glaive` | Skyborn Glaive | 10 | 43 | two_handed |
| `forgegod_scythe` | Forgegod Scythe | 10 | 48 | two_handed |

### Ranged (20)

| ID | Name | Tier | Level Req | Class Effect |
|---|---|---|---|---|
| `hunter_shortbow` | Hunter Shortbow | 1 | 1 | ranged |
| `crude_sling` | Crude Sling | 1 | 2 | ranged |
| `iron_longbow` | Iron Longbow | 2 | 3 | ranged |
| `meadow_recurve` | Meadow Recurve | 2 | 4 | ranged |
| `steel_crossbow` | Steel Crossbow | 3 | 5 | ranged |
| `cave_throwing_axe` | Cave Throwing Axe | 3 | 7 | ranged |
| `swamp_longbow` | Swamp Longbow | 4 | 9 | ranged |
| `bog_crossbow` | Bog Crossbow | 4 | 11 | ranged |
| `cinder_longbow` | Cinder Longbow | 5 | 13 | ranged |
| `ashforged_crossbow` | Ashforged Crossbow | 5 | 16 | ranged |
| `frostbound_recurve` | Frostbound Recurve | 6 | 18 | ranged |
| `hoarsteel_crossbow` | Hoarsteel Crossbow | 6 | 21 | ranged |
| `coral_longbow` | Coral Longbow | 7 | 23 | ranged |
| `tideborn_crossbow` | Tideborn Crossbow | 7 | 26 | ranged |
| `hollow_longbow` | Hollow Longbow | 8 | 29 | ranged |
| `marrow_crossbow` | Marrow Crossbow | 8 | 33 | ranged |
| `stormcaller_recurve` | Stormcaller Recurve | 9 | 36 | ranged |
| `voltsteel_crossbow` | Voltsteel Crossbow | 9 | 40 | ranged |
| `skyborn_longbow` | Skyborn Longbow | 10 | 43 | ranged |
| `forgegod_crossbow` | Forgegod Crossbow | 10 | 48 | ranged |

**Common attack set per class:** every weapon ships with one default attack (`slash`, `swing`, `thrust`, `cleave`, `shoot`) plus one or two class-themed attacks. You can attach a weapon skill on top of these per existing rules.

---

## Pickaxes (13)

| ID | Name | Tier | Mining Req | Level Req | Notes |
|---|---|---|---|---|---|
| `wood_pickaxe` | Wooden Pickaxe | 1 | 1 | 1 | Starter |
| `stone_pickaxe` | Stone Pickaxe | 1 | 1 | 2 | |
| `copper_pickaxe` | Copper Pickaxe | 2 | 2 | 4 | |
| `iron_pickaxe` | Iron Pickaxe | 3 | 4 | 6 | |
| `steel_pickaxe` | Steel Pickaxe | 4 | 5 | 9 | |
| `silver_pickaxe` | Silver Pickaxe | 4 | 6 | 11 | Unlocks gold ore branch |
| `gold_pickaxe` | Gold Pickaxe | 5 | 7 | 14 | |
| `mythril_pickaxe` | Mythril Pickaxe | 6 | 9 | 17 | Required for mythril_chunk |
| `adamantite_pickaxe` | Adamantite Pickaxe | 7 | 11 | 22 | Required for adamantite_ore |
| `obsidian_pickaxe` | Obsidian Pickaxe | 7 | 12 | 24 | Required for obsidian, volcanic_shard |
| `crystal_pickaxe` | Crystal Pickaxe | 8 | 14 | 28 | Required for glacial_crystal, salt_crystal |
| `voidsteel_pickaxe` | Voidsteel Pickaxe | 9 | 17 | 36 | Required for voidstone, soulstone |
| `celestial_pickaxe` | Celestial Pickaxe | 10 | 20 | 44 | Required for celestium, stardust, aether_crystal |

Each follows the existing upgrade curve (Apprentice/Adept/Expert/Master) via `per_level_materials` + `world/upgrade_scaling.py`.

---

## Ores (30)

| # | ID | Tier | Mining Req | Pickaxe | Drop % | Zone(s) |
|---|---|---|---|---|---|---|
| 1 | `stone` | 1 | 1 | 1 | 80% | cave, swamp |
| 2 | `copper_ore` | 1 | 2 | 1 | 55% | cave |
| 3 | `tin_ore` | 1 | 2 | 1 | 50% | cave |
| 4 | `iron_ore` | 2 | 4 | 2 | 40% | cave, swamp |
| 5 | `coal` | 2 | 4 | 2 | 45% | swamp, ashfall |
| 6 | `silver_ore` | 3 | 5 | 4 | 30% | frostbound |
| 7 | `gold_ore` | 3 | 6 | 4 | 25% | swamp |
| 8 | `mythril_chunk` | 4 | 9 | `mythril_pickaxe` | 12% | swamp, frostbound |
| 9 | `cobalt_ore` | 5 | 10 | 4 | 22% | ashfall |
| 10 | `obsidian` | 5 | 11 | `obsidian_pickaxe` | 18% | ashfall |
| 11 | `volcanic_shard` | 5 | 12 | `obsidian_pickaxe` | 14% | ashfall |
| 12 | `sulfur_chunk` | 5 | 10 | 4 | 25% | ashfall |
| 13 | `frostsilver` | 6 | 13 | 5 | 22% | frostbound |
| 14 | `iceshard` | 6 | 13 | 5 | 26% | frostbound |
| 15 | `glacial_crystal` | 6 | 15 | `crystal_pickaxe` | 14% | frostbound |
| 16 | `pearl_coral` | 7 | 16 | 6 | 20% | tidewreck |
| 17 | `seabed_quartz` | 7 | 17 | 6 | 18% | tidewreck |
| 18 | `abyssal_stone` | 7 | 18 | 6 | 16% | tidewreck |
| 19 | `salt_crystal` | 7 | 16 | `crystal_pickaxe` | 22% | tidewreck |
| 20 | `soulstone` | 8 | 19 | `voidsteel_pickaxe` | 14% | hollow |
| 21 | `bonemarble` | 8 | 19 | 7 | 20% | hollow |
| 22 | `shadowsteel` | 8 | 20 | 7 | 16% | hollow |
| 23 | `cursed_iron` | 8 | 19 | 7 | 18% | hollow |
| 24 | `stormsteel` | 9 | 22 | 8 | 18% | stormvault |
| 25 | `voltite` | 9 | 22 | 8 | 16% | stormvault |
| 26 | `skyiron` | 9 | 23 | 8 | 14% | stormvault |
| 27 | `adamantite` | 9 | 24 | `adamantite_pickaxe` | 10% | stormvault, ashfall |
| 28 | `celestium` | 10 | 26 | `celestial_pickaxe` | 12% | skyforge |
| 29 | `stardust` | 10 | 27 | `celestial_pickaxe` | 10% | skyforge |
| 30 | `aether_crystal` | 10 | 28 | `celestial_pickaxe` | 8% | skyforge |

`voidstone`, `sunstone`, and `moonstone` are reserved as boss-drop / dungeon-room mining nodes rather than standard ore loops — not in this count.

---

## Fish (20)

| ID | Tier | Fishing Req | Zone | Weight in pool |
|---|---|---|---|---|
| `river_minnow` | 1 | 1 | forest | 60% |
| `bluegill` | 1 | 2 | forest | 30% |
| `forest_perch` | 1 | 3 | forest | 10% |
| `sunfish` | 2 | 3 | meadow | 55% |
| `golden_carp` | 2 | 4 | meadow | 35% |
| `meadow_eel` | 2 | 5 | meadow | 10% |
| `blind_eel` | 3 | 5 | damp_cave | 60% |
| `glow_shrimp` | 3 | 6 | damp_cave | 30% |
| `cave_grouper` | 3 | 7 | damp_cave | 10% |
| `mudpike` | 4 | 7 | swamp | 40% |
| `glowfin` | 4 | 9 | swamp | 20% |
| `swamp_pike` | 4 | 10 | swamp | 10% |
| `magmacarp` | 5 | 11 | ashfall | 70% |
| `ashfin` | 5 | 13 | ashfall | 25% |
| `ice_salmon` | 6 | 14 | frostbound | 55% |
| `glacier_trout` | 6 | 16 | frostbound | 35% |
| `deepsquid` | 7 | 18 | tidewreck | 40% |
| `anglerfish` | 7 | 20 | tidewreck | 30% |
| `bonefish` | 8 | 22 | hollow | 60% |
| `starwhale` | 10 | 28 | skyforge | 100% (rare single-catch pool) |

---

## Seeds (33)

Existing 8 preserved. 25 new.

| # | ID | Farming Req | Grow Time | Yield | Crop | Heal |
|---|---|---|---|---|---|---|
| 1 | `corn_seed` | 1 | 2m | 2 | Corn | — |
| 2 | `wheat_seed` | 1 | 2m | 3 | Wheat | — |
| 3 | `blueberry_seed` | 2 | 3m | 2 | Blueberry | 5 |
| 4 | `sunpetal_seed` | 2 | 4m | 2 | Sunpetal | 4 |
| 5 | `herb_seed` | 3 | 5m | 1 | Herbs | 20 |
| 6 | `pumpkin_seed` | 4 | 8m | 1 | Pumpkin | 8 |
| 7 | `moonflower_seed` | 6 | 10m | 1 | Moonflower | 50 |
| 8 | `glowmushroom_seed` | 6 | 10m | 1 | Glowmushroom | 12 |
| 9 | `carrot_seed` | 1 | 2m | 3 | Carrot | 3 |
| 10 | `potato_seed` | 2 | 3m | 3 | Potato | 6 |
| 11 | `onion_seed` | 2 | 3m | 2 | Onion | 4 |
| 12 | `tomato_seed` | 3 | 4m | 2 | Tomato | 6 |
| 13 | `cabbage_seed` | 3 | 5m | 1 | Cabbage | 10 |
| 14 | `strawberry_seed` | 3 | 4m | 3 | Strawberry | 8 |
| 15 | `mandrake_seed` | 5 | 8m | 1 | Mandrake | 30 |
| 16 | `foxglove_seed` | 5 | 7m | 1 | Foxglove | 25 |
| 17 | `nightshade_seed` | 7 | 10m | 1 | Nightshade | 40 |
| 18 | `dragonweed_seed` | 8 | 12m | 1 | Dragonweed | 35 |
| 19 | `mooncress_seed` | 8 | 12m | 1 | Mooncress | 45 |
| 20 | `silverleaf_seed` | 9 | 14m | 1 | Silverleaf | 60 |
| 21 | `ashpetal_seed` | 7 | 10m | 1 | Ashpetal | 30 |
| 22 | `frostberry_seed` | 9 | 12m | 2 | Frostberry | 25 |
| 23 | `icebloom_seed` | 10 | 15m | 1 | Icebloom | 70 |
| 24 | `kelp_seed` | 9 | 12m | 2 | Kelp | 20 |
| 25 | `coral_seed` | 11 | 18m | 1 | Coral Bud | 50 |
| 26 | `bonebloom_seed` | 12 | 18m | 1 | Bonebloom | 80 |
| 27 | `soulroot_seed` | 13 | 20m | 1 | Soulroot | 100 |
| 28 | `shadowmoss_seed` | 13 | 20m | 1 | Shadowmoss | 90 |
| 29 | `stormvine_seed` | 15 | 25m | 1 | Stormvine | 110 |
| 30 | `voltflower_seed` | 16 | 25m | 1 | Voltflower | 120 |
| 31 | `starbloom_seed` | 18 | 30m | 1 | Starbloom | 150 |
| 32 | `godsblood_seed` | 19 | 35m | 1 | Godsblood | 180 |
| 33 | `celestial_lily_seed` | 20 | 40m | 1 | Celestial Lily | 250 (full heal at low levels) |

---

## Lootbox Exclusives (20)

These items drop **only** from lootboxes, never from monsters, mining, foraging, or quests. They serve as prestige items and crafting gates for top-tier content.

| # | ID | Name | Rarity | Tiers Available | Use / Flavor |
|---|---|---|---|---|
| 1 | `prismatic_shard` | Prismatic Shard | Rare+ | rare–chroma | Weapon glow / cosmetic upgrading; combines 3 for one tier of any weapon |
| 2 | `echo_core` | Echo Core | Epic+ | epic–chroma | Crafting gate for repeatable dungeon weapons; holds echo of defeated boss |
| 3 | `void_essence` | Void Essence | Legendary+ | legendary–chroma | High-tier crafting material; essence of the between-worlds |
| 4 | `celestial_ember` | Celestial Ember | Mythic+ | mythic–chroma | Tier-10 weapon fuel; infinitesimal; glows softly |
| 5 | `corrupted_pearl` | Corrupted Pearl | Epic+ | epic–chroma | Crafting material for cursed / shadow weapons; dark luster |
| 6 | `eon_crystal` | Eon Crystal | Legendary+ | legendary–chroma | Crafting material for time-themed or heirloom weapons; predates the world |
| 7 | `leviathan_scale` | Leviathan Scale | Epic+ | epic–chroma | Armor upgrade material; impenetrable; from Krakora's hide |
| 8 | `forge_catalyst` | Forge Catalyst | Rare+ | rare–chroma | Crafting consumable; +50% material efficiency on next craft; single-use |
| 9 | `soulweaver_thread` | Soulweaver Thread | Rare+ | rare–chroma | Crafting material for multi-skill weapons; binds essence to steel |
| 10 | `elder_bone` | Elder Bone | Uncommon+ | uncommon–chroma | Crafting material; bone of ancient creature; only found in loot, not mined |
| 11 | `starfall_dust` | Starfall Dust | Legendary+ | legendary–chroma | Crafting material; meteorite powder; enhances any weapon with +2 light damage |
| 12 | `hollowed_talisman` | Hollowed Talisman | Epic+ | epic–chroma | Trinket (cosmetic slot); worn by the Hollowed King; whispers cryptic advice |
| 13 | `tempest_feather` | Tempest Feather | Rare+ | rare–chroma | Crafting material / cosmetic; from storm-eagles; light as air but sharp as steel |
| 14 | `sunken_locket` | Sunken Locket | Uncommon+ | uncommon–chroma | Trinket; keeps a photo inside; from shipwreck sailors; no combat effect |
| 15 | `malice_stone` | Malice Stone | Epic+ | epic–chroma | Crafting material; pure hatred crystallized; +10% crit chance to cursed weapons |
| 16 | `moonveil_silk` | Moonveil Silk | Rare+ | rare–chroma | Armor upgrade; woven by night spiders; boosts fishing XP gain by 15% |
| 17 | `ashen_crown` | Ashen Crown | Uncommon+ | uncommon–chroma | Cosmetic / trophy head slot item; from Ashfall; grants 5% mining speed |
| 18 | `abyssal_fang` | Abyssal Fang` | Epic+ | epic–chroma | Crafting material; from deep waters; required for one tier-7 weapon tree |
| 19 | `godly_fragment` | Godly Fragment | Mythic+ | mythic–chroma | Crafting material; shard of divine essence; sole material for Tier-10 weapon recipe |
| 20 | `chronicle_ink` | Chronicle Ink | Rare+ | rare–chroma | Quest item / cosmetic; used to unlock hidden lore entries; blue shimmer, smells of ages |

**Rarity distribution:** Uncommon items drop from uncommon+ boxes. Rare items drop from rare+ boxes, etc. This means:
- Uncommon lootbox: chance of elder_bone, sunken_locket, ashen_crown
- Rare lootbox: all of above + prismatic_shard, forge_catalyst, soulweaver_thread, tempest_feather, moonveil_silk, chronicle_ink
- Epic lootbox: all of above + echo_core, corrupted_pearl, leviathan_scale, malice_stone, abyssal_fang
- Legendary lootbox: all of above + void_essence, eon_crystal, starfall_dust, hollowed_talisman
- Mythic lootbox: all of above + celestial_ember, godly_fragment
- Chroma lootbox: 100% one of: celestial_ember, godly_fragment, or starfall_dust (guaranteed boss-drop tier materials)

**Crafting gating:** Boss-drop ores + lootbox exclusives = the two bottlenecks that gate endgame recipes. A player can't craft a Tier-10 weapon without both `forgegod_essence` (boss-only) and `godly_fragment` (mythic/chroma lootbox-only).

---

## Quests (180)

Format: `id | name | objective | rewards`. Rewards key: `XP / gold / items / unlock`.

Eighteen quests per zone, mixed across the four supported objective types plus story chains.

### Zone 1 — Whispering Forest (q001–q018)

```
q001 | forest_first_steps     | visit whispering_forest                       | 30 XP, 20g
q002 | wolf_culling           | kill 5 forest_wolf                            | 60 XP, 30g, 1× small_potion
q003 | bone_collector_i       | collect 8 bone                                | 50 XP, 25g
q004 | spider_hunter          | kill 3 giant_spider                           | 70 XP, 40g, 2× spider_silk
q005 | orcish_problem         | kill 6 young_orc                              | 70 XP, 40g
q006 | tooth_gather           | collect 10 tooth                              | 50 XP, 25g
q007 | first_blade            | reach combat 3                                | 100 XP, 50g, 1× iron_sword
q008 | berry_basket           | collect 6 blueberry                           | 40 XP, 20g, 1× small_potion
q009 | forager_pup            | reach foraging 2                              | 80 XP, 40g, 3× herb_seed
q010 | first_catch            | reach fishing 1                               | 40 XP, 20g, 1× wood_fishing_rod
q011 | trial_of_the_hollow    | kill mossback_ogre                            | 250 XP, 150g, hollow_charm, unlock sunlit_meadow
q012 | wolf_pelts             | collect 4 wolf_pelt                           | 70 XP, 35g
q013 | skull_collector_i      | collect 5 skull                               | 70 XP, 35g
q014 | spider_silk_run        | collect 6 spider_silk                         | 90 XP, 50g
q015 | the_lost_axe           | collect 1 club_fragment                       | 50 XP, 30g
q016 | forest_guard           | kill 10 forest_skeleton                       | 120 XP, 60g
q017 | rangers_eye            | reach fishing 3                               | 100 XP, 50g, 1× iron_fishing_rod
q018 | mossback_avenger       | kill mossback_ogre (after q011)               | 200 XP, 100g, 1× lootbox_uncommon
```

### Zone 2 — Sunlit Meadow (q019–q036)

```
q019 | sun_pilgrim            | visit sunlit_meadow                           | 60 XP, 40g
q020 | bee_problem            | kill 5 honey_drake                            | 120 XP, 70g, 2× honey_essence
q021 | sunpetal_garden        | collect 8 sunpetal_seed                       | 100 XP, 50g
q022 | meadow_orc_hunt        | kill 8 meadow_orc                             | 140 XP, 80g
q023 | pumpkin_run            | collect 4 pumpkin                             | 100 XP, 50g
q024 | pollen_dust            | collect 6 glow_dust                           | 110 XP, 60g
q025 | farmer_friend          | reach farming 4                               | 140 XP, 70g, 3× pumpkin_seed
q026 | wisp_chaser            | kill 6 pollen_wisp                            | 100 XP, 60g
q027 | sun_caught             | reach fishing 4                               | 120 XP, 60g
q028 | drake_scales           | collect 5 drake_scale                         | 130 XP, 70g
q029 | golden_haul            | collect 5 golden_carp                         | 140 XP, 80g, 1× lootbox_uncommon
q030 | hive_oath              | kill queen_pollenwing                         | 350 XP, 200g, royal_jelly, unlock damp_cave
q031 | onion_basket           | collect 4 onion                               | 90 XP, 45g
q032 | tomato_run             | collect 6 tomato                              | 90 XP, 45g
q033 | meadow_eel_hunter      | collect 3 meadow_eel                          | 110 XP, 60g
q034 | sunpetal_master        | reach foraging 6                              | 180 XP, 90g, 1× lootbox_uncommon
q035 | sweet_offering         | collect 3 honey_essence                       | 140 XP, 70g
q036 | hive_avenger           | kill queen_pollenwing (repeatable)            | 250 XP, 120g
```

### Zone 3 — Damp Cave (q037–q054)

```
q037 | spelunker              | visit damp_cave                               | 100 XP, 60g
q038 | kobold_problem         | kill 6 kobold_miner                           | 180 XP, 100g
q039 | first_pick             | reach mining 2                                | 120 XP, 60g, 1× copper_pickaxe
q040 | stone_basket           | collect 30 stone                              | 100 XP, 50g
q041 | copper_run             | collect 15 copper_ore                         | 140 XP, 70g
q042 | iron_run               | collect 10 iron_ore                           | 160 XP, 80g
q043 | bat_swarm_culling      | kill 8 bat_swarm                              | 160 XP, 80g
q044 | cave_orc_hunt          | kill 10 cave_orc                              | 200 XP, 100g
q045 | rusty_blades           | collect 4 rusted_blade                        | 140 XP, 70g
q046 | troll_reckoning        | kill stonefist_troll                          | 450 XP, 250g, troll_heart, unlock murk_swamp
q047 | miner_initiate         | reach mining 4                                | 200 XP, 100g, 1× iron_pickaxe
q048 | blind_haul             | collect 5 blind_eel                           | 150 XP, 75g
q049 | cave_skeleton_culling  | kill 12 cave_skeleton                         | 220 XP, 110g
q050 | pickaxe_fragments      | collect 5 pickaxe_fragment                    | 160 XP, 80g
q051 | cavern_explorer        | reach mining 6                                | 250 XP, 130g, 1× lootbox_uncommon
q052 | glow_shrimp_haul       | collect 6 glow_shrimp                         | 140 XP, 70g
q053 | tin_ore_run            | collect 12 tin_ore                            | 140 XP, 70g
q054 | troll_avenger          | kill stonefist_troll (repeatable)             | 300 XP, 150g, 1× lootbox_rare
```

### Zone 4 — Murk Swamp (q055–q072)

```
q055 | swampwalker            | visit murk_swamp                              | 150 XP, 90g
q056 | gator_hunter           | kill 5 gator_brute                            | 280 XP, 150g
q057 | wisp_lantern           | kill 8 will_o_wisp                            | 260 XP, 130g
q058 | mandrake_picker        | collect 6 mandrake_seed                       | 240 XP, 120g
q059 | gold_run               | collect 8 gold_ore                            | 280 XP, 140g
q060 | mythril_seeker         | collect 3 mythril_chunk                       | 320 XP, 180g
q061 | swamp_skel_culling     | kill 10 swamp_skeleton                        | 280 XP, 140g
q062 | bog_orc_hunt           | kill 8 bog_orc                                | 300 XP, 160g
q063 | serpent_venom          | collect 5 venom_sac                           | 260 XP, 130g
q064 | swamp_pike_haul        | collect 4 swamp_pike                          | 240 XP, 120g
q065 | rot_pilgrim            | reach foraging 8                              | 300 XP, 150g, 1× moonflower_seed×3
q066 | hardened_miner         | reach mining 9                                | 320 XP, 160g, 1× mythril_pickaxe
q067 | bogfather_trial        | kill bogfather                                | 600 XP, 350g, bogfather_heart, unlock ashfall_plateau |
q068 | mooncress_picker       | collect 4 mooncress_seed                      | 280 XP, 140g
q069 | gator_hide_run         | collect 6 gator_hide                          | 280 XP, 140g
q070 | mire_culler            | kill 12 mire_serpent                          | 300 XP, 150g
q071 | swamp_essence_run      | collect 10 swamp_essence                      | 320 XP, 160g, 1× lootbox_rare
q072 | bogfather_avenger      | kill bogfather (repeatable)                   | 400 XP, 200g, 1× lootbox_rare
```

### Zone 5 — Ashfall Plateau (q073–q090)

```
q073 | flameborn              | visit ashfall_plateau                         | 220 XP, 130g
q074 | imp_culling            | kill 10 cinder_imp                            | 380 XP, 200g
q075 | ashwalker_hunt         | kill 8 ash_walker                             | 400 XP, 220g
q076 | molten_core_run        | collect 4 molten_core                         | 440 XP, 240g
q077 | obsidian_haul          | collect 10 obsidian                           | 420 XP, 220g
q078 | sulfur_run             | collect 14 sulfur_chunk                       | 380 XP, 200g
q079 | salamander_hunt        | kill 6 salamander_lord                        | 460 XP, 250g
q080 | volcanic_shard_haul    | collect 6 volcanic_shard                      | 460 XP, 250g
q081 | pyre_orc_hunt          | kill 8 pyre_orc                               | 420 XP, 220g
q082 | molten_golem_breaker   | kill 4 molten_golem                           | 520 XP, 280g
q083 | cobalt_run             | collect 10 cobalt_ore                         | 440 XP, 230g
q084 | magmacarp_haul         | collect 6 magmacarp                           | 380 XP, 200g
q085 | ashpetal_picker        | collect 5 ashpetal_seed                       | 400 XP, 220g
q086 | fire_initiate          | reach combat 14                               | 500 XP, 280g, 1× obsidian_pickaxe
q087 | dragonweed_picker      | collect 4 dragonweed_seed                     | 460 XP, 240g
q088 | magmaw_trial           | kill magmaw_the_sundering                     | 800 XP, 500g, sundering_core, unlock frostbound_peaks |
q089 | ash_collector          | collect 12 ash_dust                           | 380 XP, 200g
q090 | magmaw_avenger         | kill magmaw_the_sundering (repeatable)        | 550 XP, 280g, 1× lootbox_epic
```

### Zone 6 — Frostbound Peaks (q091–q108)

```
q091 | snowbreaker            | visit frostbound_peaks                        | 300 XP, 180g
q092 | frost_wolf_hunt        | kill 10 frost_wolf                            | 520 XP, 280g
q093 | revenant_dust_run      | collect 8 revenant_dust                       | 540 XP, 290g
q094 | yeti_hunt              | kill 5 yeti_brute                             | 600 XP, 320g
q095 | iceshard_haul          | collect 14 iceshard                           | 540 XP, 290g
q096 | frostsilver_run        | collect 10 frostsilver                        | 600 XP, 320g
q097 | snow_witch_culling     | kill 6 snow_witch                             | 580 XP, 310g
q098 | glacial_crystal_haul   | collect 5 glacial_crystal                     | 640 XP, 340g
q099 | drake_breaker          | kill 4 glacial_drake                          | 700 XP, 400g
q100 | hex_charm_run          | collect 4 hex_charm                           | 560 XP, 300g
q101 | mooncress_master       | collect 6 mooncress_seed                      | 560 XP, 300g
q102 | silverleaf_picker      | collect 4 silverleaf_seed                     | 600 XP, 320g
q103 | hardened_miner_ii      | reach mining 14                               | 700 XP, 380g, 1× crystal_pickaxe
q104 | salmon_run             | collect 8 ice_salmon                          | 480 XP, 260g
q105 | trout_run              | collect 6 glacier_trout                       | 540 XP, 290g
q106 | hoar_throne            | kill glacien_frostfanged                      | 1100 XP, 700g, frostfang, unlock tidewreck_reef |
q107 | frost_oath             | reach combat 18                               | 700 XP, 380g, 1× hoarsteel_sword
q108 | glacien_avenger        | kill glacien_frostfanged (repeatable)         | 800 XP, 400g, 1× lootbox_epic
```

### Zone 7 — Tidewreck Reef (q109–q126)

```
q109 | salt_breath            | visit tidewreck_reef                          | 400 XP, 240g
q110 | drowner_hunt           | kill 10 reef_drowner                          | 720 XP, 400g
q111 | siren_culling          | kill 8 siren_thrall                           | 740 XP, 410g
q112 | pearl_coral_haul       | collect 12 pearl_coral                        | 780 XP, 420g
q113 | tide_skel_culling      | kill 10 tide_skeleton                         | 760 XP, 420g
q114 | shark_hunt             | kill 6 shark_brood                            | 820 XP, 460g
q115 | seabed_quartz_haul     | collect 10 seabed_quartz                      | 780 XP, 420g
q116 | abyssal_stone_run      | collect 8 abyssal_stone                       | 800 XP, 440g
q117 | kelp_garden            | collect 8 kelp                                | 700 XP, 380g
q118 | coral_picker           | collect 4 coral_seed                          | 740 XP, 400g
q119 | salt_crystal_haul      | collect 12 salt_crystal                       | 760 XP, 420g
q120 | deepsquid_run          | collect 5 deepsquid                           | 700 XP, 380g
q121 | anglerfish_run         | collect 4 anglerfish                          | 780 XP, 420g
q122 | hatchling_breaker      | kill 3 kraken_hatchling                       | 900 XP, 500g
q123 | drowned_oath           | reach combat 22                               | 900 XP, 500g, 1× tideborn_sword
q124 | siren_voice_run        | collect 6 siren_voice                         | 780 XP, 420g
q125 | krakora_trial          | kill krakora_tide_spawn                       | 1400 XP, 900g, krakora_eye, unlock hollow_marches |
q126 | krakora_avenger        | kill krakora_tide_spawn (repeatable)          | 1000 XP, 500g, 1× lootbox_legendary
```

### Zone 8 — Hollow Marches (q127–q144)

```
q127 | hollow_pilgrim         | visit hollow_marches                          | 500 XP, 300g
q128 | knight_culling         | kill 10 hollow_knight                         | 940 XP, 520g
q129 | wraith_hunt            | kill 10 wraith                                | 920 XP, 510g
q130 | bone_collector_ii      | collect 30 bone                               | 880 XP, 480g
q131 | bonemarble_haul        | collect 10 bonemarble                         | 960 XP, 530g
q132 | shadowsteel_run        | collect 8 shadowsteel                         | 980 XP, 540g
q133 | cursed_iron_haul       | collect 10 cursed_iron                        | 980 XP, 540g
q134 | grave_orc_hunt         | kill 8 grave_orc                              | 1000 XP, 560g
q135 | lich_culling           | kill 6 lich_acolyte                           | 1040 XP, 580g
q136 | soulstone_run          | collect 6 soulstone                           | 1080 XP, 600g
q137 | dark_tome_run          | collect 4 dark_tome                           | 1020 XP, 560g
q138 | bonebloom_picker       | collect 5 bonebloom_seed                      | 940 XP, 520g
q139 | soulroot_picker        | collect 4 soulroot_seed                       | 1020 XP, 560g
q140 | shadowmoss_picker      | collect 4 shadowmoss_seed                     | 1020 XP, 560g
q141 | hollow_resolve         | reach combat 28                               | 1100 XP, 600g, 1× hollow_blade
q142 | hollow_kings_court     | kill the_hollowed_king                        | 1800 XP, 1200g, crown_shard, unlock stormvault_citadel |
q143 | bonefish_haul          | collect 5 bonefish                            | 880 XP, 480g
q144 | hollow_king_avenger    | kill the_hollowed_king (repeatable)           | 1300 XP, 700g, 1× lootbox_legendary
```

### Zone 9 — Stormvault Citadel (q145–q162)

```
q145 | stormwalker            | visit stormvault_citadel                      | 650 XP, 400g
q146 | sentinel_culling       | kill 10 storm_sentinel                        | 1200 XP, 680g
q147 | thunderkin_hunt        | kill 10 thunderkin                            | 1220 XP, 690g
q148 | arc_breaker            | kill 8 arc_construct                          | 1320 XP, 740g
q149 | giant_culling          | kill 4 storm_giant                            | 1500 XP, 850g
q150 | stormsteel_haul        | collect 12 stormsteel                         | 1280 XP, 720g
q151 | voltite_run            | collect 10 voltite                            | 1300 XP, 730g
q152 | skyiron_haul           | collect 10 skyiron                            | 1340 XP, 750g
q153 | adamantite_run         | collect 6 adamantite                          | 1440 XP, 800g
q154 | stormvine_picker       | collect 5 stormvine_seed                      | 1240 XP, 700g
q155 | voltflower_picker      | collect 4 voltflower_seed                     | 1320 XP, 740g
q156 | hardened_miner_iii     | reach mining 22                               | 1500 XP, 840g, 1× adamantite_pickaxe
q157 | tempest_oath           | reach combat 35                               | 1500 XP, 840g, 1× stormcut_sword
q158 | sentinel_core_run      | collect 6 sentinel_core                       | 1320 XP, 740g
q159 | lightning_rod_run      | collect 8 lightning_rod                       | 1300 XP, 730g
q160 | volthrax_trial         | kill volthrax_the_unbound                     | 2400 XP, 1600g, storm_crown, unlock skyforge_crucible |
q161 | voltcatfish_run        | collect 3 voltcatfish                         | 1200 XP, 680g
q162 | volthrax_avenger       | kill volthrax_the_unbound (repeatable)        | 1700 XP, 950g, 1× lootbox_mythic
```

### Zone 10 — Skyforge Crucible (q163–q180)

```
q163 | crucible_arrival       | visit skyforge_crucible                       | 850 XP, 550g
q164 | warden_culling         | kill 10 crucible_warden                       | 1700 XP, 1000g
q165 | star_revenant_hunt     | kill 10 star_revenant                         | 1720 XP, 1010g
q166 | void_herald_culling    | kill 8 void_herald                            | 1900 XP, 1100g
q167 | forgewraith_breaker    | kill 6 forgewraith                            | 2100 XP, 1200g
q168 | celestium_haul         | collect 12 celestium                          | 1900 XP, 1100g
q169 | stardust_run           | collect 10 stardust                           | 2000 XP, 1150g
q170 | aether_crystal_haul    | collect 8 aether_crystal                      | 2200 XP, 1300g
q171 | warden_plate_run       | collect 6 warden_plate                        | 1900 XP, 1100g
q172 | herald_eye_run         | collect 5 herald_eye                          | 2000 XP, 1150g
q173 | starbloom_picker       | collect 5 starbloom_seed                      | 1900 XP, 1100g
q174 | godsblood_picker       | collect 4 godsblood_seed                      | 2100 XP, 1200g
q175 | celestial_lily_picker  | collect 3 celestial_lily_seed                 | 2300 XP, 1400g
q176 | celestial_oath         | reach combat 42                               | 2200 XP, 1300g, 1× skyborn_sword
q177 | hardened_miner_iv      | reach mining 26                               | 2200 XP, 1300g, 1× celestial_pickaxe
q178 | astralith_trial        | kill astralith_forgegod                       | 4000 XP, 3000g, forgegod_essence, all stat +1 |
q179 | wraith_dust_run        | collect 10 wraith_dust                        | 2000 XP, 1150g
q180 | astralith_avenger      | kill astralith_forgegod (repeatable)          | 2800 XP, 1700g, 1× lootbox_chroma
```

---

## Notes for implementation

- **Trial quests** (`q011`, `q030`, `q046`, `q067`, `q088`, `q106`, `q125`, `q142`, `q160`, `q178`) are the main progression spine. Each unlocks the next zone bypassing stat gates. Avenger quests are repeatable for grinding boss-drop lootboxes.
- **Crafting reagents** dropped by bosses (`hollow_charm`, `royal_jelly`, `troll_heart`, `bogfather_heart`, `sundering_core`, `frostfang`, `krakora_eye`, `crown_shard`, `storm_crown`, `forgegod_essence`) should each gate at least one weapon recipe at their tier. I haven't enumerated the recipes — that's a follow-up pass.
- **Lootbox drop tier mapping** should put `forest`/`meadow` in the common-band, `cave`/`swamp` uncommon-band, `ashfall`/`frostbound` rare-band, `tidewreck`/`hollow` epic-band, `stormvault` legendary-band, `skyforge` mythic-band (with chroma as boss-only bonus rolls).
- **Boss-drop ores** (`voidstone`, `sunstone`, `moonstone`) are intentionally excluded from the 30-ore mining loop count; they're meant as guaranteed boss tokens for top-end recipes.
- **Stat gate inflation:** the existing stat-XP curve (`xp_exp=1.4`) gets steep past level 20. Either tune `xp_coeff` upward for skill stats or budget zone XP rewards so a tier-7 player isn't grinding meadow for foraging XP.