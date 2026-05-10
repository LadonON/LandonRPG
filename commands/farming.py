import random
import time
from collections import Counter

from discord.ext import commands

from ..services import players
from ..world import seeds as seed_catalog, zones, unlocks, items, stats as stats_mod
from .. import style
from ._helpers import block_during_pvp

# Forage cooldown in seconds
FORAGE_COOLDOWN = 30
FORAGE_XP_PER_ACTION = 5

# In-memory forage cooldowns: user_id -> last forage timestamp
_forage_cd: dict[int, float] = {}


def _yield_amount(base: int, farming_level: int) -> int:
    return base + farming_level // 3


def _fmt_seconds(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s}s" if s else f"{m}m"


class Farming(commands.Cog):

    # ── !forage ──────────────────────────────────────────────────────────────

    @commands.command(name="forage")
    @block_during_pvp()
    async def forage(self, ctx):
        """Gather random seeds from your current zone (not in village)."""
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        zone = zones.world.get((player.x, player.y))

        if zone is None or zone.zone_id == "village":
            await ctx.send("There's nothing to forage in the village. Head to the Forest or Cave.")
            return

        if not zone.forage_table:
            await ctx.send(f"There's nothing to forage in **{zone.name}**.")
            return

        # Cooldown check
        now = time.time()
        remaining = FORAGE_COOLDOWN - (now - _forage_cd.get(ctx.author.id, 0))
        if remaining > 0:
            await ctx.send(f"You need to rest before foraging again. ({remaining:.0f}s)")
            return
        _forage_cd[ctx.author.id] = now

        # Weighted random pick — always 1–2 seeds per forage,
        # plus +1 per (foraging_level // 4) from the foraging skill bonus.
        weights = [drop.weight for drop in zone.forage_table]
        chosen = random.choices(zone.forage_table, weights=weights, k=1)[0]
        amount = random.randint(1, 2) + (player.foraging_level // 4)

        for _ in range(amount):
            player.inventory.append(chosen.seed_id)

        leveled = stats_mod.gain_xp(player, "foraging", FORAGE_XP_PER_ACTION)
        level_msg = f"\nForaging reached Level {player.foraging_level}!" if leveled else ""

        seed = seed_catalog.get(chosen.seed_id)
        name = seed.seed_name if seed else chosen.seed_id
        await ctx.send(
            f"You search the {zone.name} and find **{amount}x {name}**! "
            f"(+{FORAGE_XP_PER_ACTION} foraging XP, cooldown {FORAGE_COOLDOWN}s)"
            + level_msg
        )

    # ── !farm ─────────────────────────────────────────────────────────────────

    @commands.command(name="farm")
    @block_during_pvp()
    async def farm(self, ctx, seed_id: str = None, amount: str = "1"):
        """Plant seeds from your inventory: !farm <seed_id> [amount]"""
        if seed_id is None:
            rows = sorted(seed_catalog.SEEDS.values(), key=lambda s: s.min_farming_level)
            listing = ", ".join(f"{s.seed_name} (L{s.min_farming_level})" for s in rows)
            await ctx.send(f"Usage: `!farm <seed_id> [amount]`\nAvailable seeds: {listing}")
            return

        try:
            amount = max(1, int(amount))
        except ValueError:
            await ctx.send("Amount must be a whole number.")
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        seed = seed_catalog.get(seed_id.lower())

        if seed is None:
            names = ", ".join(seed_catalog.SEEDS.keys())
            await ctx.send(f"Unknown seed `{seed_id}`. Known seeds: {names}")
            return

        if player.farming_level < seed.min_farming_level:
            await ctx.send(
                f"**{seed.seed_name}** requires Farming Level {seed.min_farming_level} "
                f"(you are Level {player.farming_level})."
            )
            return

        available = player.inventory.count(seed.seed_id)
        if available < amount:
            await ctx.send(
                f"You need **{amount}x {seed.seed_name}** but only have {available}. "
                f"Use `!forage` to find seeds."
            )
            return

        # Remove seeds and create a growing plot
        for _ in range(amount):
            player.inventory.remove(seed.seed_id)

        player.growing_plots.append({
            "seed_id": seed.seed_id,
            "crop_id": seed.crop_id,
            "crop_name": seed.crop_name,
            "seed_name": seed.seed_name,
            "amount": amount,
            "planted_at": time.time(),
            "grow_time": seed.grow_time_seconds,
            "yield_base": seed.yield_base,
            "farming_xp": seed.farming_xp,
        })

        await ctx.send(
            f"Planted **{amount}x {seed.seed_name}**. "
            f"Ready to harvest in **{_fmt_seconds(seed.grow_time_seconds)}**. "
            f"Check with `!plots`, collect with `!harvest`."
        )

    # ── !harvest ──────────────────────────────────────────────────────────────

    @commands.command(name="harvest")
    @block_during_pvp()
    async def harvest(self, ctx):
        """Collect all fully-grown crops."""
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)

        if not player.growing_plots:
            await ctx.send("You have no planted crops. Use `!forage` to find seeds, then `!farm`.")
            return

        now = time.time()
        ready     = [p for p in player.growing_plots if now >= p["planted_at"] + p["grow_time"]]
        not_ready = [p for p in player.growing_plots if now <  p["planted_at"] + p["grow_time"]]

        if not ready:
            soonest = min(player.growing_plots, key=lambda p: p["planted_at"] + p["grow_time"])
            remaining = (soonest["planted_at"] + soonest["grow_time"]) - now
            await ctx.send(
                f"No crops are ready yet. "
                f"Soonest: **{soonest['seed_name']}** in {_fmt_seconds(remaining)}."
            )
            return

        harvested: Counter = Counter()
        xp_total = 0
        leveled = False

        for plot in ready:
            per_seed = _yield_amount(plot["yield_base"], player.farming_level)
            total = plot["amount"] * per_seed
            for _ in range(total):
                player.inventory.append(plot["crop_id"])
            harvested[plot["crop_name"]] += total
            xp = plot["farming_xp"] * plot["amount"]
            xp_total += xp
            if stats_mod.gain_xp(player, "farming", xp):
                leveled = True

        player.growing_plots = not_ready

        harvest_str = ", ".join(f"{n} x{q}" for n, q in harvested.items())
        level_msg   = f"\nFarming reached Level {player.farming_level}!" if leveled else ""
        pending_msg = f"\n{len(not_ready)} plot(s) still growing." if not_ready else ""

        await ctx.send(
            f"Harvested: **{harvest_str}** (+{xp_total} farming XP)"
            + level_msg + pending_msg
        )

    # ── !plots ────────────────────────────────────────────────────────────────

    @commands.command(name="plots")
    async def plots(self, ctx):
        """Show the status of all your growing plots."""
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)

        if not player.growing_plots:
            await ctx.send(embed=style.info(
                "No planted crops.",
                "Use `!forage` to find seeds, then `!farm <seed_id>`."
            ))
            return

        now = time.time()
        lines = []
        for plot in player.growing_plots:
            remaining = (plot["planted_at"] + plot["grow_time"]) - now
            status = "Ready to harvest" if remaining <= 0 else f"{_fmt_seconds(remaining)} remaining"
            lines.append(f"• {plot['amount']}x **{plot['seed_name']}** → {plot['crop_name']} — {status}")

        embed = style.lookup(f"{player.name}'s Plots",
                             footer_context=f"Plots: {len(player.growing_plots)}")
        style.add_fields(embed, [("Crops", "\n".join(lines), False)])
        await ctx.send(embed=embed)

    # ── !stats ────────────────────────────────────────────────────────────────

    @commands.command(name="stats")
    async def stats(self, ctx, stat: str = None, level: str = None, action: str = None):
        """
        !stats                              — usage hint (lists registered stats)
        !stats <stat>                       — your skill overview
        !stats <stat> <lvl>                 — all milestones at that level + claim status
        !stats <stat> <lvl> claim           — collect rewards for that milestone
        !stats claim all                    — claim every eligible reward across all stats
        """
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)

        registered = stats_mod.names()

        # ── Global claim-all: !stats claim all ───────────────────────────────
        if stat and stat.lower() == "claim" and level and level.lower() == "all":
            claimed_lines = []
            total_gold = 0
            total_items = 0
            for name in registered:
                cfg = stats_mod.get(name)
                cur_lvl = getattr(player, cfg.level_attr)
                for u in cfg.unlocks_pool:
                    if u.required_level > cur_lvl:
                        continue
                    if u.id in player.claimed_unlocks:
                        continue
                    player.claimed_unlocks.append(u.id)
                    gained = []
                    for item_id in u.reward_items:
                        player.inventory.append(item_id)
                        item = items.get(item_id)
                        gained.append(item.name if item else item_id)
                        total_items += 1
                    if u.reward_gold:
                        player.gold += u.reward_gold
                        gained.append(f"{u.reward_gold}g")
                        total_gold += u.reward_gold
                    claimed_lines.append(
                        f"[{name.title()} L{u.required_level}] **{u.label}** — "
                        f"{', '.join(gained) if gained else 'no items'}"
                    )
            if not claimed_lines:
                await ctx.send("Nothing to claim — you're all caught up across every stat.")
                return
            await ctx.send(
                f"Claimed **{len(claimed_lines)}** milestone(s) "
                f"({total_items} item(s), {total_gold}g):\n"
                + "\n".join(claimed_lines)
            )
            return

        # ── No args → top-level usage ────────────────────────────────────────
        if stat is None:
            lines = ["**Stats**"]
            for name in registered:
                lines.append(f"`!stats {name}` — view your {name} skill")
            stat_choices = "|".join(registered) if registered else "stat"
            lines.append(f"`!stats <{stat_choices}> <level>` — see milestones at a level")
            lines.append(f"`!stats <{stat_choices}> <level> claim` — collect milestone rewards")
            lines.append("`!stats claim all` — collect every eligible reward across all stats")
            await ctx.send("\n".join(lines))
            return

        cfg = stats_mod.get(stat)
        if cfg is None:
            choices = ", ".join(f"`{n}`" for n in registered) or "(none)"
            await ctx.send(f"Unknown stat. Available: {choices}.")
            return

        stat    = cfg.name
        pool    = cfg.unlocks_pool
        cur_lvl = getattr(player, cfg.level_attr)
        cur_xp  = getattr(player, cfg.xp_attr)
        nxt     = cfg.xp_to_next(player)
        unit    = cfg.unit
        bonus   = cur_lvl // cfg.bonus_divisor
        bonus_label = cfg.bonus_label

        # ── Stat only → skill overview ────────────────────────────────────────
        if level is None:
            next_milestone = next(
                (u for u in pool if u.required_level > cur_lvl
                 or u.id not in player.claimed_unlocks),
                None,
            )
            if next_milestone:
                next_text = (f"L{next_milestone.required_level} {next_milestone.label} "
                             f"— `!stats {stat} {next_milestone.required_level}`")
            else:
                next_text = "All milestones reached."
            embed = style.lookup(
                f"{stat.title()} — Level {cur_lvl}",
                description=f"Use `!stats {stat} <level>` to inspect any milestone.",
                footer_context=f"Requested by {ctx.author.display_name}",
            )
            style.add_fields(embed, [
                ("Progress", f"{cur_xp}/{nxt} {unit}", True),
                ("Bonus",    f"+{bonus} {bonus_label}", True),
                ("Next",     next_text, False),
            ])
            await ctx.send(embed=embed)
            return

        # ── Stat + level → show milestones at that level ──────────────────────
        try:
            req_lvl = int(level)
        except ValueError:
            await ctx.send(f"Level must be a number. Example: `!stats {stat} 3`")
            return

        milestone_list = unlocks.get_at_level(stat, req_lvl)
        if not milestone_list:
            await ctx.send(f"No {stat} milestones at level {req_lvl}.")
            return

        # ── Claim ─────────────────────────────────────────────────────────────
        if action and action.lower() == "claim":
            claimable = [u for u in milestone_list if u.id not in player.claimed_unlocks]
            if not claimable:
                await ctx.send(f"You've already claimed all {stat} L{req_lvl} rewards.")
                return
            if cur_lvl < req_lvl:
                await ctx.send(
                    f"You need {stat.title()} Level {req_lvl} to claim these rewards. "
                    f"You are Level {cur_lvl}."
                )
                return

            reward_lines = []
            for u in claimable:
                player.claimed_unlocks.append(u.id)
                gained = []
                for item_id in u.reward_items:
                    player.inventory.append(item_id)
                    item = items.get(item_id)
                    gained.append(item.name if item else item_id)
                if u.reward_gold:
                    player.gold += u.reward_gold
                    gained.append(f"{u.reward_gold}g")
                reward_lines.append(
                    f"[Claimed] **{u.label}** -- {', '.join(gained) if gained else 'no items'}"
                )

            await ctx.send(
                f"Claimed {stat.title()} L{req_lvl} rewards:\n"
                + "\n".join(reward_lines)
            )
            return

        # ── Display milestones at level ───────────────────────────────────────
        qualified = cur_lvl >= req_lvl
        lines = []
        for u in milestone_list:
            claimed   = u.id in player.claimed_unlocks
            status    = "[Claimed]" if claimed else ("[Ready to claim]" if qualified else "[Locked]")
            item_names = [items.get(i).name if items.get(i) else i for i in u.reward_items]
            rewards    = ", ".join(item_names) + (f", {u.reward_gold}g" if u.reward_gold else "")
            if not rewards:
                rewards = "none"
            lines.append(
                f"**{u.label}** [{status}]\n"
                f"  {u.description}\n"
                f"  Rewards: {rewards}"
                + ("" if claimed else f"\n  → `!stats {stat} {req_lvl} claim`")
            )

        level_status = f"Level {req_lvl}" + (" [unlocked]" if qualified else f" [locked - you are L{cur_lvl}]")
        await ctx.send(
            f"**{stat.title()} {level_status} Milestones:**\n\n"
            + "\n\n".join(lines)
        )


async def setup(bot):
    await bot.add_cog(Farming())
