import asyncio
import os
import logging

import discord
from discord.ext import commands
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from dotenv import load_dotenv

from .services import players
from .world import seeds as _seeds                # registers seed/crop items at import time
from .world import weapons as _weapons            # registers weapon items at import time
from .world import weapon_skills as _weapon_skills  # registers weapon-skill items at import time
from .world import pickaxes as _pickaxes          # registers pickaxe items at import time
from .world import resources as _resources        # registers resource items at import time
from .world import quests as _quests              # registers quests at import time
from .world import lootboxes as _lootboxes        # registers lootbox items + drop tiers
from .world import bosses as _bosses              # registers bosses
from .world import dungeons as _dungeons          # registers dungeons

EXTENSIONS = [
    "landonrpg.commands.help",
    "landonrpg.commands.combat",
    "landonrpg.commands.exploration",
    "landonrpg.commands.shop",
    "landonrpg.commands.inventory",
    "landonrpg.commands.crafting",
    "landonrpg.commands.farming",
    "landonrpg.commands.gathering",
    "landonrpg.commands.trading",
    "landonrpg.commands.pvp",
    "landonrpg.commands.quests",
    "landonrpg.commands.dungeon",
    "landonrpg.commands.lootbox",
]


def _build_logger():
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=Console(force_terminal=True))],
    )
    install(show_locals=True)
    return logging.getLogger("rich")


def make_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True  # required to resolve usernames for !trade
    bot = commands.Bot(command_prefix="!", intents=intents)
    log = _build_logger()

    @bot.event
    async def on_ready():
        await bot.tree.sync()
        log.info("Logged in as %s", bot.user)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        raise error

    @bot.event
    async def on_member_join(member: discord.Member):
        try:
            await member.send(
                f"**Welcome to LandonRPG, {member.display_name}.**\n\n"
                "You've just arrived in a persistent text-based RPG world with combat, "
                "crafting, gathering, quests, dungeons, and more.\n\n"
                "**Quick start:**\n"
                "1. Head to the game channel and run `!equip rusty_sword`\n"
                "2. Travel to the forest: `!warp Whispering Forest`\n"
                "3. Start fighting: `!attack` → `!rusty_sword slash`\n\n"
                "For a full interactive walkthrough of every feature, run:\n"
                "```\n!tutorial\n```\n"
                "For a command reference at any time:\n"
                "```\n!help\n```\n"
                "Good luck, adventurer!"
            )
        except discord.Forbidden:
            pass  # DMs disabled — silently skip

    @bot.after_invoke
    async def _autosave(ctx):
        # Run the SQLAlchemy commit in a worker thread so concurrent commands
        # don't serialize on a single sync DB write blocking the event loop.
        await asyncio.to_thread(players.save, ctx.author.id)

    @bot.event
    async def setup_hook():
        for ext in EXTENSIONS:
            await bot.load_extension(ext)

    return bot


def run():
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    bot = make_bot()
    bot.run(token)
