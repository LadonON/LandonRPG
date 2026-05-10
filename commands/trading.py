import asyncio
from collections import Counter
from dataclasses import dataclass, field

import discord
from discord.ext import commands

from ..services import players
from ..world import items
from ..util import get_or_fetch_user, save_player_async


# ── Trade state ───────────────────────────────────────────────────────────────

@dataclass
class Trade:
    initiator_id: int
    recipient_id: int
    initiator_name: str
    recipient_name: str
    initiator_offer: list[tuple[str, int]] = field(default_factory=list)
    recipient_offer: list[tuple[str, int]] = field(default_factory=list)
    initiator_locked: bool = False
    recipient_locked: bool = False


# user_id -> Trade; both players in a trade share the same object
_trades: dict[int, Trade] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_offer(args: tuple[str, ...]) -> list[tuple[str, int]] | str:
    """Parse 'item amount item amount ...' into [(item_id, amount), ...].
    Amount is optional per item and defaults to 1.
    Returns an error string on bad input."""
    result: list[tuple[str, int]] = []
    i = 0
    tokens = list(args)
    while i < len(tokens):
        item_id = tokens[i].lower()
        i += 1
        amount = 1
        if i < len(tokens):
            try:
                amount = int(tokens[i])
                if amount < 1:
                    return f"Amount for `{item_id}` must be at least 1."
                i += 1
            except ValueError:
                pass  # next token is another item name; keep amount=1
        result.append((item_id, amount))
    return result


def _offer_str(offer: list[tuple[str, int]]) -> str:
    if not offer:
        return "nothing"
    return ", ".join(
        f"{items.get(i).name if items.get(i) else i} x{a}" for i, a in offer
    )


def _validate_offer(
    player, offer: list[tuple[str, int]]
) -> list[str]:
    """Return a list of error strings; empty list means offer is valid."""
    errors: list[str] = []
    needed: Counter = Counter()
    for item_id, amount in offer:
        if items.get(item_id) is None:
            errors.append(f"Unknown item `{item_id}`.")
        else:
            needed[item_id] += amount
    for item_id, total in needed.items():
        have = player.inventory.count(item_id)
        if have < total:
            name = items.get(item_id).name
            errors.append(f"Not enough {name}: need {total}, have {have}.")
    return errors


# ── Cog ───────────────────────────────────────────────────────────────────────

class Trading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── !trade ────────────────────────────────────────────────────────────────

    @commands.command(name="trade")
    @commands.guild_only()
    async def trade(self, ctx, *, target_name: str = None):
        if target_name is None:
            await ctx.send("Usage: `!trade <username>`")
            return

        if ctx.author.id in _trades:
            await ctx.send(
                "You already have an active trade. "
                "Use `!items cancel` in DMs to cancel it first."
            )
            return

        # Resolve member by display name or username (case-insensitive)
        target = discord.utils.find(
            lambda m: (
                m.display_name.lower() == target_name.lower()
                or m.name.lower() == target_name.lower()
            ),
            ctx.guild.members,
        )

        if target is None:
            await ctx.send(f"No player named `{target_name}` found in this server.")
            return
        if target.id == ctx.author.id:
            await ctx.send("You cannot trade with yourself.")
            return
        if target.bot:
            await ctx.send("You cannot trade with a bot.")
            return
        if target.id in _trades:
            await ctx.send(f"**{target.display_name}** already has an active trade.")
            return

        trade = Trade(
            initiator_id=ctx.author.id,
            recipient_id=target.id,
            initiator_name=ctx.author.display_name,
            recipient_name=target.display_name,
        )
        _trades[ctx.author.id] = trade
        _trades[target.id] = trade

        dm_instructions = (
            "1. Use `!items select <item> <amount> [<item> <amount> ...]` "
            "to choose what you offer.\n"
            "2. Use `!items confirm` to lock in your offer.\n"
            "3. Use `!items cancel` at any time to abort the trade."
        )

        try:
            await ctx.author.send(
                f"Trade request sent to **{target.display_name}**.\n{dm_instructions}"
            )
            await target.send(
                f"**{ctx.author.display_name}** wants to trade with you.\n"
                f"{dm_instructions}"
            )
            await ctx.send(
                f"Trade request sent to **{target.display_name}**. Check your DMs."
            )
        except Exception:
            _trades.pop(ctx.author.id, None)
            _trades.pop(target.id, None)
            await ctx.send(
                "Could not send DMs. Make sure both players allow DMs from server members."
            )

    # ── !items group ──────────────────────────────────────────────────────────

    @commands.group(name="items", invoke_without_command=True)
    async def items_group(self, ctx):
        if ctx.guild is not None:
            await ctx.send("Trade item commands only work in DMs.")
            return
        await ctx.send(
            "Usage:\n"
            "`!items select <item> <amount> [<item> <amount> ...]` — set your offer\n"
            "`!items confirm` — lock in your offer\n"
            "`!items cancel`  — cancel the trade"
        )

    @items_group.command(name="select")
    async def items_select(self, ctx, *args: str):
        if ctx.guild is not None:
            await ctx.send("Use `!items select` in DMs during an active trade.")
            return

        trade = _trades.get(ctx.author.id)
        if trade is None:
            await ctx.send("You don't have an active trade.")
            return

        is_initiator = ctx.author.id == trade.initiator_id
        already_locked = (
            trade.initiator_locked if is_initiator else trade.recipient_locked
        )
        if already_locked:
            await ctx.send(
                "You have already locked in your offer. "
                "Use `!items cancel` to abort the trade."
            )
            return

        if not args:
            await ctx.send("Provide at least one item. Example: `!items select corn 3 wheat 2`")
            return

        offer = _parse_offer(args)
        if isinstance(offer, str):
            await ctx.send(offer)
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        errors = _validate_offer(player, offer)
        if errors:
            await ctx.send("\n".join(errors))
            return

        if is_initiator:
            trade.initiator_offer = offer
        else:
            trade.recipient_offer = offer

        other_name = trade.recipient_name if is_initiator else trade.initiator_name
        await ctx.send(
            f"Offer set: **{_offer_str(offer)}**\n"
            f"Run `!items confirm` to lock this in and notify **{other_name}**.\n"
            f"You can run `!items select` again to change your offer before confirming."
        )

    @items_group.command(name="confirm")
    async def items_confirm(self, ctx, mode: str = None):
        if ctx.guild is not None:
            await ctx.send("Use `!items confirm` in DMs during an active trade.")
            return

        trade = _trades.get(ctx.author.id)
        if trade is None:
            await ctx.send("You don't have an active trade.")
            return

        is_initiator = ctx.author.id == trade.initiator_id
        my_offer     = trade.initiator_offer if is_initiator else trade.recipient_offer
        my_locked    = trade.initiator_locked if is_initiator else trade.recipient_locked
        is_gift      = mode is not None and mode.lower() == "gift"

        if my_locked:
            await ctx.send("You have already confirmed your offer.")
            return
        if not my_offer:
            await ctx.send("Set your offer first with `!items select`.")
            return

        other_offer = trade.recipient_offer if is_initiator else trade.initiator_offer
        if is_gift and other_offer:
            other_name_for_err = trade.recipient_name if is_initiator else trade.initiator_name
            await ctx.send(
                f"Cannot send as gift: **{other_name_for_err}** has already offered items. "
                "Use `!items confirm` to do a normal trade."
            )
            return

        # Lock this player in
        if is_initiator:
            trade.initiator_locked = True
        else:
            trade.recipient_locked = True

        other_id   = trade.recipient_id if is_initiator else trade.initiator_id
        other_name = trade.recipient_name if is_initiator else trade.initiator_name

        if is_gift:
            # Auto-lock the receiver with an empty offer and execute immediately.
            if is_initiator:
                trade.recipient_locked = True
            else:
                trade.initiator_locked = True
            await ctx.send(
                f"Gift confirmed: **{_offer_str(my_offer)}** → **{other_name}**. Executing..."
            )
            await self._execute_trade(trade)
        elif trade.initiator_locked and trade.recipient_locked:
            # Both confirmed — execute
            await ctx.send("Both players confirmed. Executing trade...")
            await self._execute_trade(trade)
        else:
            await ctx.send(
                f"Offer locked: **{_offer_str(my_offer)}**\n"
                f"Waiting for **{other_name}** to confirm their offer."
            )
            try:
                other_user = await get_or_fetch_user(self.bot, other_id)
                await other_user.send(
                    f"**{ctx.author.display_name}** locked in their offer: "
                    f"**{_offer_str(my_offer)}**.\n"
                    f"Set your items with `!items select`, then `!items confirm` to complete the trade."
                )
            except Exception:
                pass

    @items_group.command(name="cancel")
    async def items_cancel(self, ctx):
        if ctx.guild is not None:
            await ctx.send("Use `!items cancel` in DMs during an active trade.")
            return

        trade = _trades.get(ctx.author.id)
        if trade is None:
            await ctx.send("You don't have an active trade.")
            return

        other_id   = trade.recipient_id if ctx.author.id == trade.initiator_id else trade.initiator_id
        other_name = trade.recipient_name if ctx.author.id == trade.initiator_id else trade.initiator_name

        _trades.pop(trade.initiator_id, None)
        _trades.pop(trade.recipient_id, None)

        await ctx.send("Trade cancelled.")
        try:
            other_user = await get_or_fetch_user(self.bot, other_id)
            await other_user.send(
                f"**{ctx.author.display_name}** cancelled the trade."
            )
        except Exception:
            pass

    # ── Trade execution ───────────────────────────────────────────────────────

    async def _execute_trade(self, trade: Trade) -> None:
        initiator_player = players.get_or_create(trade.initiator_id, trade.initiator_name)
        recipient_player = players.get_or_create(trade.recipient_id, trade.recipient_name)

        # Fetch Discord users for DMs (do this early so we can report failures)
        try:
            init_user = await get_or_fetch_user(self.bot, trade.initiator_id)
            recv_user = await get_or_fetch_user(self.bot, trade.recipient_id)
        except Exception:
            _trades.pop(trade.initiator_id, None)
            _trades.pop(trade.recipient_id, None)
            return

        async def abort(msg_initiator: str, msg_recipient: str) -> None:
            _trades.pop(trade.initiator_id, None)
            _trades.pop(trade.recipient_id, None)
            try:
                await init_user.send(msg_initiator)
                await recv_user.send(msg_recipient)
            except Exception:
                pass

        # Final validation: both players must still have their offered items
        init_errors = _validate_offer(initiator_player, trade.initiator_offer)
        recv_errors = _validate_offer(recipient_player, trade.recipient_offer)

        if init_errors:
            missing = init_errors[0]
            await abort(
                f"Trade failed: {missing} Trade cancelled.",
                f"Trade failed: **{trade.initiator_name}** no longer has the offered items. "
                "Trade cancelled.",
            )
            return

        if recv_errors:
            missing = recv_errors[0]
            await abort(
                f"Trade failed: **{trade.recipient_name}** no longer has the offered items. "
                "Trade cancelled.",
                f"Trade failed: {missing} Trade cancelled.",
            )
            return

        # Remove offered items from each player
        for item_id, amount in trade.initiator_offer:
            for _ in range(amount):
                initiator_player.inventory.remove(item_id)

        for item_id, amount in trade.recipient_offer:
            for _ in range(amount):
                recipient_player.inventory.remove(item_id)

        # Give each player what they received
        for item_id, amount in trade.recipient_offer:
            for _ in range(amount):
                initiator_player.inventory.append(item_id)

        for item_id, amount in trade.initiator_offer:
            for _ in range(amount):
                recipient_player.inventory.append(item_id)

        # Persist both players in parallel, off the event loop. Autosave only
        # covers the command invoker, so the other side needs an explicit save.
        await asyncio.gather(
            save_player_async(players.save, trade.initiator_id),
            save_player_async(players.save, trade.recipient_id),
        )

        _trades.pop(trade.initiator_id, None)
        _trades.pop(trade.recipient_id, None)

        init_gave = _offer_str(trade.initiator_offer)
        recv_gave = _offer_str(trade.recipient_offer)

        try:
            await init_user.send(
                f"Trade complete!\n"
                f"You gave:     {init_gave}\n"
                f"You received: {recv_gave}"
            )
            await recv_user.send(
                f"Trade complete!\n"
                f"You gave:     {recv_gave}\n"
                f"You received: {init_gave}"
            )
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Trading(bot))
