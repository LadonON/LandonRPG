"""Cross-cog performance helpers.

Centralises a few patterns we use repeatedly so a perf fix lands in one place.
"""
from __future__ import annotations

import asyncio


async def get_or_fetch_user(bot, user_id: int):
    """Return a `discord.User`, preferring the in-memory cache.

    `bot.get_user` is a O(1) dict lookup against the user cache populated by
    gateway events (members in shared guilds, anyone who has DMed the bot,
    etc.). `bot.fetch_user` is an HTTP call. In hot paths like battle log
    fan-out, we issue one DM per recipient per swing — preferring the cache
    cuts API calls dramatically.
    """
    user = bot.get_user(user_id)
    if user is not None:
        return user
    return await bot.fetch_user(user_id)


async def save_player_async(save_fn, user_id: int) -> None:
    """Run a synchronous DB save off the event loop.

    `players.save` opens a SQLAlchemy session and commits — sync I/O. Calling
    it directly from an async path blocks discord.py's event loop until commit
    returns. Wrapping with `asyncio.to_thread` lets concurrent commands keep
    making progress while the DB write happens in a worker thread.
    """
    await asyncio.to_thread(save_fn, user_id)
