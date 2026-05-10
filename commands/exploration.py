from discord.ext import commands

from ..services import players
from ..world import zones
from ..quests import engine as quests_engine
from ._helpers import zone_summary, block_during_pvp


class Exploration(commands.Cog):
    @commands.command(name="warp")
    @block_during_pvp()
    async def warp(self, ctx, *, zone_name: str = None):
        if zone_name is None:
            listing = "; ".join(f"{z.name} ({x},{y})" for (x, y), z in zones.world.items())
            await ctx.send(f"Usage: `!warp <zone name>`. Zones: {listing}")
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        coords = zones.find_by_name(zone_name)
        if coords is None:
            await ctx.send(f"No zone named `{zone_name}`.")
            return

        zone = zones.world[coords]
        # Quest-rewarded zone unlocks bypass the level gates.
        bypass = zone.zone_id in (player.unlocked_zones or [])
        if not bypass:
            if zone.min_combat_level > player.combat_level:
                await ctx.send(
                    f"**{zone.name}** requires Combat Level {zone.min_combat_level} (you are Level {player.combat_level})."
                )
                return
            if zone.min_foraging_level > player.foraging_level:
                await ctx.send(
                    f"**{zone.name}** requires Foraging Level {zone.min_foraging_level} (you are Level {player.foraging_level})."
                )
                return
            if zone.min_farming_level > player.farming_level:
                await ctx.send(
                    f"**{zone.name}** requires Farming Level {zone.min_farming_level} (you are Level {player.farming_level})."
                )
                return
        player.x, player.y = coords
        # Quest hook: any visit_zone quests targeting this zone are now satisfied.
        quests_engine.on_zone_entered(player, zone.zone_id)
        await ctx.send(zone_summary(zone))


async def setup(bot):
    await bot.add_cog(Exploration())
