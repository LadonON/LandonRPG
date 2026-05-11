"""Help and tutorial commands.

!help                – categorised command reference
!help <category>     – detailed help for one category
!tutorial            – interactive step-by-step tutorial (reaction navigation)
"""
import discord
from discord.ext import commands

from .. import style

# ── Help categories ──────────────────────────────────────────────────────────

CATEGORIES: dict[str, dict] = {
    "start": {
        "label": "Getting Started",
        "summary": "First steps for new adventurers.",
        "commands": [
            ("`!me`",                   "View your character sheet, stats, and location."),
            ("`!inv`",                  "Open your inventory. Shows equipped gear and all items."),
            ("`!equip <item_id>`",      "Equip a weapon, armor, pickaxe, or fishing rod."),
            ("`!inspect <item_id>`",    "Inspect any item for full stat details including attacks."),
            ("`!rest`",                 "Restore HP to full (Village only)."),
            ("`!tutorial`",             "Launch the interactive new-player tutorial."),
        ],
    },
    "explore": {
        "label": "Exploration",
        "summary": "Travel between zones and discover the world.",
        "commands": [
            ("`!warp <zone name>`",     "Travel to a named zone. Unlocked zones bypass level gates."),
            ("`!warp`",                 "List all known zones with their coordinates."),
            ("`!me`",                   "Shows your current zone at the bottom of your sheet."),
        ],
    },
    "combat": {
        "label": "Combat",
        "summary": "Turn-based monster battles with poise and stagger.",
        "commands": [
            ("`!attack [monster_id]`",  "Start a fight. Omit monster to pick a random one from the zone."),
            ("`!<weapon> <attack>`",    "Use a weapon attack on your turn. E.g. `!rusty_sword slash`."),
            ("`!pve arena`",            "Check the current fight status, HP bars, and poise."),
            ("`!pve arena flee`",       "Attempt to flee the battle (not always successful)."),
        ],
    },
    "shop": {
        "label": "Shop & Economy",
        "summary": "Buy, sell, and trade items.",
        "commands": [
            ("`!shop`",                 "Browse the village shop (paginated)."),
            ("`!shop <page>`",          "Jump to a specific shop page."),
            ("`!buy <item_id> [qty]`",  "Purchase items from the shop."),
            ("`!sell <item_id> [qty]`", "Sell items from your inventory for gold."),
            ("`!trade @user <give_id> <recv_id>`", "Trade items directly with another player."),
        ],
    },
    "craft": {
        "label": "Crafting & Upgrades",
        "summary": "Upgrade weapons, attach skills, and craft items.",
        "commands": [
            ("`!craft upgrade <weapon>`",              "Preview the next upgrade level's cost."),
            ("`!craft upgrade <weapon> <level>`",      "Spend materials to upgrade to that level."),
            ("`!craft attach <weapon> <skill_id>`",    "Attach a weapon skill to unlock a new attack."),
            ("`!craft <ingredient> [xN] …`",          "Craft an item from a recipe."),
            ("`!craft recipes [page]`",                "Browse all crafting recipes."),
        ],
    },
    "gather": {
        "label": "Gathering",
        "summary": "Mine ores and fish — passive resource loops.",
        "commands": [
            ("`!mine <resource> [amount]`", "Mine a resource in the current zone (requires pickaxe)."),
            ("`!fish [amount]`",            "Cast a line in zones with a fishing pool (requires rod)."),
            ("`!forage [amount]`",          "Forage seeds and plants in foraging zones."),
        ],
    },
    "farm": {
        "label": "Farming",
        "summary": "Grow crops from seeds and harvest them.",
        "commands": [
            ("`!plant <seed_id>`",  "Plant a seed in an empty plot (Village only)."),
            ("`!plot`",             "Check your growing plots and time until harvest."),
            ("`!harvest`",          "Harvest all ready crops into your inventory."),
            ("`!water <plot>`",     "Water a plot to speed up growth."),
        ],
    },
    "quests": {
        "label": "Quests",
        "summary": "Accept, track, and complete quests for rewards.",
        "commands": [
            ("`!quests`",               "List all available quests in your current zone."),
            ("`!quests all`",           "List every quest in the game."),
            ("`!quest take <quest_id>`","Accept a quest and start tracking its objective."),
            ("`!quest status`",         "Check progress on your active quests."),
            ("`!quest abandon <id>`",   "Drop an active quest without penalty."),
        ],
    },
    "pvp": {
        "label": "PVP",
        "summary": "Challenge other players to duels.",
        "commands": [
            ("`!pvp challenge @user`",  "Challenge another player to an arena duel."),
            ("`!pvp accept`",           "Accept an incoming challenge."),
            ("`!pvp arena`",            "Check the live state of your PVP fight."),
            ("`!<weapon> <attack>`",    "Same combat syntax as PvE — works in PVP too."),
        ],
    },
    "dungeon": {
        "label": "Dungeons",
        "summary": "Multi-room boss dungeons with unique loot.",
        "commands": [
            ("`!dungeon list`",         "See dungeons available in the current zone."),
            ("`!dungeon enter <id>`",   "Enter a dungeon and begin its encounter sequence."),
            ("`!dungeon status`",       "Check your current room, enemies, and progress."),
        ],
    },
}

CATEGORY_KEYS = list(CATEGORIES.keys())

OVERVIEW_LINES = "\n".join(
    f"**{v['label']}** — `!help {k}`"
    for k, v in CATEGORIES.items()
)


# ── Tutorial steps ───────────────────────────────────────────────────────────

TUTORIAL_STEPS: list[dict] = [
    {
        "title": "Welcome to LandonRPG!",
        "body": (
            "You're an adventurer in a persistent world full of monsters, loot, and secrets.\n\n"
            "This tutorial covers everything you need to get started. "
            "Use the buttons below to move between steps."
        ),
    },
    {
        "title": "Step 1 — Your Character",
        "body": (
            "Run **`!me`** right now to open your character sheet.\n\n"
            "It shows:\n"
            "• **HP** — how much damage you can take before dying\n"
            "• **Level / XP** — your overall power, earned from all activities\n"
            "• **Skill levels** — Combat, Foraging, Mining, Fishing, Farming — each levels independently\n"
            "• **Location** — which zone you're currently in\n\n"
            "You start at Level 1 in the **Village**. Everything grows as you play."
        ),
    },
    {
        "title": "Step 2 — Inventory & Gear",
        "body": (
            "Run **`!inv`** to open your inventory.\n\n"
            "You start with a **Rusty Sword**. Before you can fight, you need to equip it:\n"
            "```\n!equip rusty_sword\n```\n"
            "To see a weapon's attacks and stats before equipping:\n"
            "```\n!inspect rusty_sword\n```\n"
            "There are five item slots: **Weapon**, **Armor**, **Pickaxe**, and **Fishing Rod**."
        ),
    },
    {
        "title": "Step 3 — Exploring the World",
        "body": (
            "The world is a grid of zones. You start in the **Village** (safe, no monsters).\n\n"
            "Travel with **`!warp`**:\n"
            "```\n!warp Whispering Forest\n```\n"
            "Run `!warp` alone to see every zone and its coordinates.\n\n"
            "Higher zones require minimum **Combat Level** to enter. "
            "Completing quests can unlock zones early."
        ),
    },
    {
        "title": "Step 4 — Fighting Monsters",
        "body": (
            "In any combat zone, start a fight with **`!attack`**:\n"
            "```\n!attack\n```\n"
            "You'll see the monster's HP, Poise, and your own HP. "
            "Combat is **turn-based** — you go first, then the monster.\n\n"
            "To attack, pick your weapon and one of its attacks:\n"
            "```\n!rusty_sword slash\n```\n"
            "Use **`!pve arena`** at any time to see the fight status."
        ),
    },
    {
        "title": "Step 5 — Poise & Stagger",
        "body": (
            "Every monster has a **Poise** bar alongside its HP.\n\n"
            "Every attack deals **poise damage** in addition to regular damage. "
            "When poise hits 0, the monster is **staggered** — it loses its next turn and "
            "your poise damage resets.\n\n"
            "Different attacks have different **poise break** values. "
            "Heavy, slow attacks tend to break poise faster — experiment to find your rhythm.\n\n"
            "Use **`!inspect <weapon_id>`** to see each attack's poise break value."
        ),
    },
    {
        "title": "Step 6 — Leveling & Progression",
        "body": (
            "Killing monsters rewards:\n"
            "• **XP** — levels up your character\n"
            "• **Combat XP** — levels up your Combat skill specifically\n"
            "• **Loot** — bones, teeth, pelts, and more\n\n"
            "Higher Combat level unlocks tougher zones and better weapons in the shop. "
            "Run **`!me`** to track your progress.\n\n"
            "Loot can be sold at the shop (**`!sell <item_id>`**) for gold."
        ),
    },
    {
        "title": "Step 7 — The Shop",
        "body": (
            "In the **Village**, run **`!shop`** to browse items for sale.\n"
            "Use `!shop <page>` to flip through pages.\n\n"
            "Buy with:\n```\n!buy <item_id>\n```\n"
            "Sell loot with:\n```\n!sell bone\n!sell tooth 5\n```\n"
            "Better weapons become available as your Combat level rises. "
            "Check the shop regularly after leveling up."
        ),
    },
    {
        "title": "Step 8 — Quests",
        "body": (
            "Quests give you goals and reward gold, XP, and sometimes **zone unlocks**.\n\n"
            "List quests in your zone:\n```\n!quests\n```\n"
            "Accept one:\n```\n!quest take q001\n```\n"
            "Check your progress:\n```\n!quest status\n```\n"
            "Quest objectives are things like: kill N monsters, collect an item, "
            "reach a skill level, or visit a zone.\n\n"
            "Completing **Trial quests** unlocks the next zone permanently."
        ),
    },
    {
        "title": "Step 9 — Upgrading Weapons",
        "body": (
            "Instead of always buying new weapons, you can **upgrade** existing ones.\n\n"
            "Preview the next upgrade cost:\n```\n!craft upgrade rusty_sword\n```\n"
            "Then spend the materials:\n```\n!craft upgrade rusty_sword 2\n```\n"
            "Upgrade costs **increase with every level** — each step is more expensive than the last.\n\n"
            "Each weapon tier has a **level cap**. Upgrade to close the power gap, "
            "then buy the next tier weapon and repeat."
        ),
    },
    {
        "title": "Step 10 — Weapon Skills",
        "body": (
            "**Weapon skills** are special attacks you can attach to any weapon.\n\n"
            "Buy a skill from the shop, then attach it:\n"
            "```\n!craft attach rusty_sword precise_strike_skill\n```\n"
            "This adds a new attack to that weapon. Only one skill per weapon.\n"
            "Attaching a new skill returns the old one to your inventory.\n\n"
            "Use **`!inspect <skill_id>`** to see the skill's damage, to-hit bonus, and poise break."
        ),
    },
    {
        "title": "Step 11 — Gathering",
        "body": (
            "Beyond combat, you can gather resources:\n\n"
            "**Mining** (equip a pickaxe first):\n```\n!mine copper_ore\n!mine copper_ore 5\n```\n"
            "**Fishing** (equip a fishing rod first):\n```\n!fish\n!fish 3\n```\n"
            "**Foraging** (no tool needed):\n```\n!forage\n```\n"
            "Each activity levels its own skill. Higher skill levels unlock better resources, "
            "better fishing spots, and rarer forage drops."
        ),
    },
    {
        "title": "Step 12 — Farming",
        "body": (
            "Farming is a passive income loop. Buy seeds from the shop, plant them in the Village:\n"
            "```\n!plant blueberry_seed\n```\n"
            "Check your growing plots:\n```\n!plot\n```\n"
            "Once grown, harvest everything:\n```\n!harvest\n```\n"
            "Crops can be sold for gold or used in crafting recipes. "
            "Higher Farming levels unlock more plot slots and rarer seeds."
        ),
    },
    {
        "title": "You're Ready to Adventure!",
        "body": (
            "That covers the core loops. Here's your quick-start checklist:\n\n"
            "1. `!equip rusty_sword`\n"
            "2. `!warp Whispering Forest`\n"
            "3. `!attack` → `!rusty_sword slash`\n"
            "4. `!sell` loot → `!shop` → buy better gear\n"
            "5. `!quests` → complete a Trial quest → unlock the next zone\n\n"
            "For a full command reference run **`!help`** anytime.\n"
            "Good luck, adventurer."
        ),
    },
]

TUTORIAL_TIMEOUT = 120   # seconds of inactivity before the tutorial closes


def _tutorial_embed(step_index: int) -> discord.Embed:
    step = TUTORIAL_STEPS[step_index]
    total = len(TUTORIAL_STEPS)
    embed = style.brand(
        step["title"],
        step["body"],
        footer_context=f"Step {step_index + 1} of {total}",
    )
    return embed


class TutorialView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=TUTORIAL_TIMEOUT)
        self.author_id = author_id
        self.step = 0
        self.total = len(TUTORIAL_STEPS)
        self._sync_buttons()

    def _sync_buttons(self):
        self.prev_btn.disabled = self.step == 0
        self.next_btn.disabled = self.step == self.total - 1

    async def _guard(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This tutorial belongs to someone else.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._guard(interaction):
            return
        self.step = max(self.step - 1, 0)
        self._sync_buttons()
        await interaction.response.edit_message(embed=_tutorial_embed(self.step), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._guard(interaction):
            return
        self.step = min(self.step + 1, self.total - 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=_tutorial_embed(self.step), view=self)

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._guard(interaction):
            return
        self.stop()
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="*Tutorial closed. Run `!tutorial` to restart or `!help` for command reference.*",
            embed=None,
            view=self,
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(
                content="*Tutorial timed out. Run `!tutorial` to restart.*",
                embed=None,
                view=self,
            )


def _help_overview_embed() -> discord.Embed:
    embed = style.lookup(
        "LandonRPG Help",
        "A persistent text-based RPG with combat, crafting, gathering, and more.\n\n"
        + OVERVIEW_LINES,
        footer_context="!help <category> for details  •  !tutorial to learn interactively",
    )
    return embed


def _category_embed(key: str) -> discord.Embed:
    cat = CATEGORIES[key]
    embed = style.lookup(
        cat["label"],
        cat["summary"],
        footer_context="!help for all categories",
    )
    for cmd, desc in cat["commands"]:
        embed.add_field(name=cmd, value=desc, inline=False)
    return embed


# ── Cog ─────────────────────────────────────────────────────────────────────

class Help(commands.Cog):

    @commands.command(name="help", aliases=["commands"])
    async def help_cmd(self, ctx, *, topic: str = None):
        if topic is None:
            await ctx.send(embed=_help_overview_embed())
            return

        topic = topic.lower().strip()

        if topic in ("tutorial", "tut", "guide"):
            await self._run_tutorial(ctx)
            return

        # Fuzzy match: full key or label substring
        match = None
        for key, cat in CATEGORIES.items():
            if topic == key or topic in cat["label"].lower():
                match = key
                break

        if match is None:
            keys = ", ".join(f"`{k}`" for k in CATEGORY_KEYS)
            await ctx.send(embed=style.error(
                f"Unknown help topic `{topic}`.",
                f"Available categories: {keys}\nOr run `!help tutorial`."
            ))
            return

        await ctx.send(embed=_category_embed(match))

    @commands.command(name="tutorial", aliases=["tut", "guide"])
    async def tutorial_cmd(self, ctx):
        await self._run_tutorial(ctx)

    async def _run_tutorial(self, ctx):
        view = TutorialView(ctx.author.id)
        view.message = await ctx.send(embed=_tutorial_embed(0), view=view)


async def setup(bot):
    # Remove the built-in help command so our !help doesn't conflict.
    bot.remove_command("help")
    await bot.add_cog(Help())
