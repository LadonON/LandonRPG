"""Quest commands.

`!quest`                       — list available, active, and completed quests
`!quest <id>`                  — start a quest
`!quest progress [<id>]`       — show progress for one or all active quests
`!quest claim <id>`            — claim rewards once the objective is met
`!quest abandon <id>`          — drop an active quest
"""
from discord.ext import commands

from ..services import players
from ..world import quests as quests_world
from ..quests import engine as quests_engine
from .. import style
from ._helpers import block_during_battle


class Quests(commands.Cog):

    @commands.group(name="quest", invoke_without_command=True)
    @block_during_battle()
    async def quest(self, ctx, *args: str):
        """Top-level !quest — without args, lists quests; with one arg, starts that quest."""
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)

        if not args:
            await ctx.send(embed=self._build_quest_list_embed(player, ctx.author.display_name))
            return

        sub = args[0].lower()
        if sub in ("progress", "claim", "abandon"):
            await ctx.send(embed=style.info(
                "Quest command usage",
                "`!quest` lists quests • `!quest <id>` starts • "
                "`!quest progress [<id>]` shows status • "
                "`!quest claim <id>` collects rewards • "
                "`!quest abandon <id>` drops it."
            ))
            return

        ok, msg = quests_engine.start(player, sub)
        await ctx.send(embed=(style.success(msg) if ok else style.error(msg)))

    @quest.command(name="progress")
    @block_during_battle()
    async def quest_progress(self, ctx, quest_id: str = None):
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)

        if quest_id:
            quest = quests_world.get(quest_id)
            if quest is None:
                await ctx.send(embed=style.error(f"Unknown quest `{quest_id}`."))
                return
            if quest.id not in player.active_quests:
                await ctx.send(embed=style.warning(f"{quest.name} is not active."))
                return
            ready = quests_engine.is_complete(player, quest.id)
            embed = style.lookup(
                quest.name,
                description=quests_engine.progress_summary(player, quest.id),
                footer_context="Ready to claim" if ready else "In progress",
            )
            await ctx.send(embed=embed)
            return

        if not player.active_quests:
            await ctx.send(embed=style.info(
                "No active quests.",
                "Use `!quest` to see what's available."
            ))
            return

        lines = []
        for qid in player.active_quests:
            quest = quests_world.get(qid)
            name = quest.name if quest else qid
            ready = quests_engine.is_complete(player, qid)
            mark = "  ✅" if ready else ""
            lines.append(f"• **{name}** (`{qid}`) — {quests_engine.progress_summary(player, qid)}{mark}")

        embed = style.lookup("Active Quests",
                             footer_context=f"{len(player.active_quests)} active")
        style.add_fields(embed, [("Progress", "\n".join(lines), False)])
        await ctx.send(embed=embed)

    @quest.command(name="claim")
    @block_during_battle()
    async def quest_claim(self, ctx, quest_id: str = None):
        if quest_id is None:
            await ctx.send(embed=style.error(
                "`!quest claim` needs an id.",
                "Usage: `!quest claim <id>`."
            ))
            return
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        ok, msg = quests_engine.claim(player, quest_id.lower())
        if ok:
            await ctx.send(embed=style.celebration(msg))
        else:
            await ctx.send(embed=style.warning(msg))

    @quest.command(name="abandon")
    @block_during_battle()
    async def quest_abandon(self, ctx, quest_id: str = None):
        if quest_id is None:
            await ctx.send(embed=style.error(
                "`!quest abandon` needs an id.",
                "Usage: `!quest abandon <id>`."
            ))
            return
        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        ok, msg = quests_engine.abandon(player, quest_id.lower())
        await ctx.send(embed=(style.success(msg) if ok else style.warning(msg)))

    # ── Rendering ────────────────────────────────────────────────────────────

    def _build_quest_list_embed(self, player, requester_name: str):
        active_ids = set(player.active_quests.keys())
        completed_ids = set(player.completed_quests)

        available = [
            q for q in quests_world.QUESTS.values()
            if q.id not in active_ids and q.id not in completed_ids
        ]

        embed = style.lookup(
            "Quests",
            description="`!quest <id>` to start, `!quest progress` for status.",
            footer_context=f"Requested by {requester_name}",
        )

        if available:
            avail_lines = []
            for q in available:
                req = self._format_requirements(q.requirements)
                rew = self._format_rewards(q.rewards)
                avail_lines.append(f"• **{q.name}** (`{q.id}`) — {q.description}{req}\n  Rewards: {rew}")
            avail_text = "\n".join(avail_lines)
        else:
            avail_text = "No new quests available."

        fields = [("Available", avail_text, False)]

        if player.active_quests:
            active_lines = []
            for qid in player.active_quests:
                quest = quests_world.get(qid)
                name = quest.name if quest else qid
                ready = quests_engine.is_complete(player, qid)
                mark = "  ✅" if ready else ""
                active_lines.append(f"• **{name}** (`{qid}`) — {quests_engine.progress_summary(player, qid)}{mark}")
            fields.append(("Active", "\n".join(active_lines), False))

        if player.completed_quests:
            fields.append(("Completed", f"{len(player.completed_quests)} quest(s)", True))

        style.add_fields(embed, fields)
        return embed

    @staticmethod
    def _format_requirements(reqs: dict) -> str:
        if not reqs:
            return ""
        parts = [f"{k.title()} L{v}" for k, v in reqs.items()]
        return f" _(requires {', '.join(parts)})_"

    @staticmethod
    def _format_rewards(r) -> str:
        bits = []
        if r.xp:
            bits.append(f"{r.xp} XP")
        if r.gold:
            bits.append(f"{r.gold}g")
        for item in r.items:
            bits.append(item)
        if r.unlock_zone:
            bits.append(f"unlock zone `{r.unlock_zone}`")
        return ", ".join(bits) if bits else "(none)"


async def setup(bot):
    await bot.add_cog(Quests())
