"""Single source of truth for the bot's Discord output style.

Per CLAUDE.md: never hardcode hex colors, status emoji, or footer strings in
command files. Import the constants and builders from here.

Builders (`success`, `error`, `warning`, `info`, `lookup`, `brand`,
`celebration`) all return a `discord.Embed` with the canonical color, status
emoji, footer, and native `timestamp` set. Pass fields via `add_fields` so the
4-fields-on-first-paint rule stays a one-line check at the call site.
"""
from __future__ import annotations

import discord


# ── Colors ──────────────────────────────────────────────────────────────────
# Use these by intent, not by command. Rebrand by editing this file only.
COLOR_SUCCESS = 0x22C55E
COLOR_ERROR   = 0xEF4444
COLOR_WARNING = 0xF59E0B
COLOR_INFO    = 0x3B82F6
COLOR_BRAND   = 0x5865F2


# ── Status emoji ────────────────────────────────────────────────────────────
EMOJI_SUCCESS     = "✅"
EMOJI_ERROR       = "❌"
EMOJI_WARNING     = "⚠️"
EMOJI_INFO        = "ℹ️"
EMOJI_LOOKUP      = "🔍"
EMOJI_PENDING     = "⏳"
EMOJI_CELEBRATION = "🎉"


# ── Branding ────────────────────────────────────────────────────────────────
BOT_NAME = "LandonRPG"


# ── Helpers ─────────────────────────────────────────────────────────────────

def _truncate(s: str, limit: int) -> str:
    return s if s is None or len(s) <= limit else s[: limit - 1] + "…"


def _build(
    *,
    emoji: str,
    color: int,
    title: str,
    description: str | None = None,
    footer_context: str | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        # Title leads with one status emoji and stays under the mobile-truncation cliff.
        title=_truncate(f"{emoji} {title}", 50),
        description=_truncate(description, 300) if description else None,
        color=color,
        timestamp=discord.utils.utcnow(),
    )
    footer = BOT_NAME + (f" • {footer_context}" if footer_context else "")
    embed.set_footer(text=footer)
    return embed


def add_fields(embed: discord.Embed, fields: list[tuple[str, str, bool]]) -> discord.Embed:
    """Add multiple fields. Each tuple is (name, value, inline).

    Per CLAUDE.md: keep ≤ 4 fields on first paint. `inline=True` only when
    value ≤ 20 chars. Caller is responsible for that check.
    """
    for name, value, inline in fields:
        embed.add_field(name=name, value=value or "—", inline=inline)
    return embed


# ── Builders by intent ──────────────────────────────────────────────────────

def success(title: str, description: str | None = None, *, footer_context: str | None = None) -> discord.Embed:
    return _build(emoji=EMOJI_SUCCESS, color=COLOR_SUCCESS, title=title,
                  description=description, footer_context=footer_context)


def error(title: str, fix: str | None = None, *, footer_context: str | None = None) -> discord.Embed:
    """Error embed: one-line problem in the title, optional one-line fix in the description.

    Mirrors the canonical error format from CLAUDE.md.
    """
    return _build(emoji=EMOJI_ERROR, color=COLOR_ERROR, title=title,
                  description=fix, footer_context=footer_context)


def warning(title: str, description: str | None = None, *, footer_context: str | None = None) -> discord.Embed:
    return _build(emoji=EMOJI_WARNING, color=COLOR_WARNING, title=title,
                  description=description, footer_context=footer_context)


def info(title: str, description: str | None = None, *, footer_context: str | None = None) -> discord.Embed:
    return _build(emoji=EMOJI_INFO, color=COLOR_INFO, title=title,
                  description=description, footer_context=footer_context)


def lookup(title: str, description: str | None = None, *, footer_context: str | None = None) -> discord.Embed:
    return _build(emoji=EMOJI_LOOKUP, color=COLOR_INFO, title=title,
                  description=description, footer_context=footer_context)


def brand(title: str, description: str | None = None, *, footer_context: str | None = None) -> discord.Embed:
    return _build(emoji="", color=COLOR_BRAND, title=title.lstrip(),
                  description=description, footer_context=footer_context)


def celebration(title: str, description: str | None = None, *, footer_context: str | None = None) -> discord.Embed:
    return _build(emoji=EMOJI_CELEBRATION, color=COLOR_SUCCESS, title=title,
                  description=description, footer_context=footer_context)
