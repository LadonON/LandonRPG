"""Gathering commands: !mine and !fish.

Both follow the foraging model: instant attempts gated by a per-zone cooldown.
- !mine <resource> [amount]: requires an equipped pickaxe; rolls each swing
  against the resource's drop chance; awards mining XP per successful hit.
- !fish [amount]: rolls weighted picks from the zone's fishing pool; awards
  fishing XP per attempt regardless of result.
"""
import random
import time
from collections import Counter

from discord.ext import commands

from ..services import players
from ..world import zones, resources as res_world, pickaxes as pick_world, items, stats as stats_mod
from .. import style
from ._helpers import block_during_battle


MINING_COOLDOWN = 30
FISHING_COOLDOWN = 30
MINING_XP_PER_HIT = 5             # added on top of resource.mining_xp on success
FISHING_XP_PER_CAST = 5
MAX_ATTEMPTS_PER_COMMAND = 10     # cap so spammers can't grind 999 in one call

_mine_cd: dict[int, float] = {}
_fish_cd: dict[int, float] = {}


def _pickaxe_ok_for(player, resource: res_world.Resource) -> tuple[bool, str]:
    """Validate the player's pickaxe against a resource's requirements."""
    pid = player.equipped_pickaxe
    if not pid:
        return False, "You have no pickaxe equipped. Use `!equip <pickaxe_id>` first."
    pickaxe = pick_world.get(pid)
    if pickaxe is None:
        return False, f"Equipped item `{pid}` isn't a known pickaxe."
    if resource.required_pickaxe and resource.required_pickaxe != pid:
        return False, (
            f"**{resource.name}** can only be mined with `{resource.required_pickaxe}`. "
            f"You're wielding `{pid}`."
        )
    effective = pick_world.effective_pickaxe_level(player, pid)
    if effective < resource.min_pickaxe_level:
        return False, (
            f"**{resource.name}** needs an effective pickaxe level of "
            f"{resource.min_pickaxe_level} (your {pickaxe.name} is at {effective})."
        )
    return True, ""


class Gathering(commands.Cog):

    # ── !mine ────────────────────────────────────────────────────────────────

    @commands.command(name="mine")
    @block_during_battle()
    async def mine(self, ctx, resource_id: str = None, amount: str = "1"):
        if resource_id is None:
            listing = ", ".join(sorted(res_world.RESOURCES.keys()))
            await ctx.send(embed=style.error(
                "`!mine` needs a resource.",
                f"Usage: `!mine <resource_id> [amount]`. Known: {listing}."
            ))
            return

        try:
            amount = max(1, min(MAX_ATTEMPTS_PER_COMMAND, int(amount)))
        except ValueError:
            await ctx.send(embed=style.error("Amount must be a whole number."))
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        zone = zones.world.get((player.x, player.y))
        if zone is None or not zone.mining_resources:
            await ctx.send(embed=style.warning(
                "Nothing to mine here.",
                "Travel to a zone with mining (e.g. Damp Cave or Murk Swamp)."
            ))
            return

        resource = res_world.get(resource_id)
        if resource is None or resource.id not in zone.mining_resources:
            avail = ", ".join(zone.mining_resources) or "(none)"
            await ctx.send(embed=style.error(
                f"Can't mine `{resource_id}` here.",
                f"Available in **{zone.name}**: {avail}."
            ))
            return

        if player.mining_level < resource.min_mining_level:
            await ctx.send(embed=style.error(
                f"{resource.name} requires Mining L{resource.min_mining_level}.",
                f"You're at L{player.mining_level}."
            ))
            return

        ok, msg = _pickaxe_ok_for(player, resource)
        if not ok:
            await ctx.send(embed=style.error(msg))
            return

        now = time.time()
        remaining = MINING_COOLDOWN - (now - _mine_cd.get(ctx.author.id, 0))
        if remaining > 0:
            await ctx.send(embed=style.warning(
                "Catching your breath.",
                f"Try again in {remaining:.0f}s."
            ))
            return
        _mine_cd[ctx.author.id] = now

        # Roll each swing independently.
        hits = 0
        bonus_per_hit = player.mining_level // 4
        xp_gained = 0
        leveled = False
        for _ in range(amount):
            if random.randint(1, 100) <= resource.drop_chance:
                qty = 1 + bonus_per_hit
                for _ in range(qty):
                    player.inventory.append(resource.id)
                hits += qty
                xp_gained += resource.mining_xp + MINING_XP_PER_HIT
                if stats_mod.gain_xp(player, "mining", resource.mining_xp + MINING_XP_PER_HIT):
                    leveled = True

        if hits == 0:
            embed = style.warning(
                f"Mined {amount}x — found nothing.",
                f"{resource.name} drops {resource.drop_chance}% per swing. (cooldown {MINING_COOLDOWN}s)"
            )
            await ctx.send(embed=embed)
            return

        embed = style.success(
            f"Mined {hits}x {resource.name}",
            f"+{xp_gained} mining XP. (cooldown {MINING_COOLDOWN}s)",
            footer_context=f"Mining L{player.mining_level}",
        )
        if leveled:
            style.add_fields(embed, [("Milestone", f"Mining reached L{player.mining_level}.", False)])
        await ctx.send(embed=embed)

    # ── !fish ────────────────────────────────────────────────────────────────

    @commands.command(name="fish")
    @block_during_battle()
    async def fish(self, ctx, amount: str = "1"):
        try:
            amount = max(1, min(MAX_ATTEMPTS_PER_COMMAND, int(amount)))
        except ValueError:
            await ctx.send(embed=style.error("Amount must be a whole number."))
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        zone = zones.world.get((player.x, player.y))
        if zone is None or not zone.fishing_pool:
            await ctx.send(embed=style.warning(
                "No fishing here.",
                "Travel to a zone with water (Forest, Meadow, Swamp)."
            ))
            return

        if not player.equipped_fishing_rod:
            await ctx.send(embed=style.error(
                "You need a fishing rod.",
                "Buy one at the village shop, craft one, then `!equip <rod_id>`."
            ))
            return

        now = time.time()
        remaining = FISHING_COOLDOWN - (now - _fish_cd.get(ctx.author.id, 0))
        if remaining > 0:
            await ctx.send(embed=style.warning(
                "Your line is still resetting.",
                f"Try again in {remaining:.0f}s."
            ))
            return
        _fish_cd[ctx.author.id] = now

        weights = [c.weight for c in zone.fishing_pool]
        caught: Counter = Counter()
        xp_gained = 0
        leveled = False
        bonus = player.fishing_level // 4
        for _ in range(amount):
            pick = random.choices(zone.fishing_pool, weights=weights, k=1)[0]
            qty = 1 + bonus
            for _ in range(qty):
                player.inventory.append(pick.item_id)
            caught[pick.item_id] += qty
            xp_gained += FISHING_XP_PER_CAST
            if stats_mod.gain_xp(player, "fishing", FISHING_XP_PER_CAST):
                leveled = True

        catch_str = ", ".join(
            f"{items.get(i).name if items.get(i) else i} x{q}" for i, q in caught.items()
        )
        embed = style.success(
            f"Caught {sum(caught.values())} item(s)",
            f"+{xp_gained} fishing XP. (cooldown {FISHING_COOLDOWN}s)",
            footer_context=f"Fishing L{player.fishing_level}",
        )
        fields = [("Catch", catch_str, False)]
        if leveled:
            fields.append(("Milestone", f"Fishing reached L{player.fishing_level}.", False))
        style.add_fields(embed, fields)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Gathering())
