from collections import Counter
from discord.ext import commands

from ..services import players
from ..world import items, recipes, weapons, weapon_skills
from ..pvp import engine as pvp_engine
from ..pve import engine as pve_engine
from ._helpers import inventory_str

PAGE_SIZE = 5


class Crafting(commands.Cog):
    @commands.command(name="craft")
    async def craft(self, ctx, *args: str):
        if pvp_engine.in_battle(ctx.author.id):
            await ctx.send("You can't craft while in a PVP arena.")
            return
        if pve_engine.in_battle(ctx.author.id):
            await ctx.send("You can't craft while in a PvE encounter.")
            return

        if not args:
            await ctx.send(
                "Usage:\n"
                "`!craft <ingredient> [xN] ... [count]` — craft from a recipe\n"
                "`!craft upgrade <weapon> <material> [<material> ...]` — upgrade a weapon\n"
                "`!craft attach <weapon> <weapon_skill_id>` — attach a weapon skill (replaces existing)\n"
                "`!craft recipes <page>` — view recipes"
            )
            return

        if args[0].lower() == "upgrade":
            await self._upgrade(ctx, args[1:])
            return

        if args[0].lower() == "attach":
            await self._attach(ctx, args[1:])
            return

        if args[0].lower() == "recipes":
            page = 1
            if len(args) >= 2:
                if not args[1].isdigit():
                    await ctx.send("Page must be a number. Example: `!craft recipes 1`")
                    return
                page = max(1, int(args[1]))

            recipe_items = list(recipes.RECIPES.items())
            total_pages = max(1, (len(recipe_items) + PAGE_SIZE - 1) // PAGE_SIZE)
            if page > total_pages:
                await ctx.send(f"Page {page} doesn't exist. There are {total_pages} page(s).")
                return

            start = (page - 1) * PAGE_SIZE
            chunk = recipe_items[start:start + PAGE_SIZE]
            lines = [f"**Recipes** — page {page}/{total_pages}"]
            for rid, ing in chunk:
                it = items.get(rid)
                name = it.name if it else rid
                ing_str = ", ".join(f"{i} x{q}" for i, q in ing.items())
                lines.append(f"  → **{name}** (`{rid}`): {ing_str}")
            await ctx.send("\n".join(lines))
            return

        tokens = list(args)
        count = 1
        if len(tokens) >= 2 and tokens[-1].isdigit():
            count = max(1, int(tokens.pop()))

        provided: Counter = Counter()
        i = 0
        while i < len(tokens):
            token = tokens[i].lower()
            qty = 1
            if i + 1 < len(tokens):
                nxt = tokens[i + 1].lower()
                if nxt.startswith("x") and nxt[1:].isdigit():
                    qty = int(nxt[1:])
                    i += 1
            provided[token] += qty
            i += 1

        match = next((rid for rid, ing in recipes.RECIPES.items() if Counter(ing) == provided), None)
        if match is None:
            await ctx.send("No recipe matches those ingredients. See `!craft recipes 1` for options.")
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        ok, msg = recipes.craft(player, match, count)
        if ok:
            await ctx.send(f"Crafted **{msg} x{count}**!\nInventory: {inventory_str(player)}")
        else:
            await ctx.send(msg)


    async def _upgrade(self, ctx, args: tuple[str, ...]):
        if not args:
            await ctx.send(
                "Usage: `!craft upgrade <weapon_id> <material> [<material> ...]`\n"
                "Each material consumes one of the upgrade recipe's required items."
            )
            return

        weapon_id = args[0].lower()
        material_tokens = [a.lower() for a in args[1:]]

        weapon = weapons.get(weapon_id)
        if weapon is None:
            await ctx.send(
                f"Unknown weapon `{weapon_id}`. "
                f"Known weapons: {', '.join(sorted(weapons.WEAPONS.keys()))}."
            )
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)

        if weapon_id not in player.inventory and player.equipped_weapon != weapon_id:
            await ctx.send(f"You don't own a **{weapon.name}**.")
            return

        inst = pvp_engine.get_instance(player, weapon_id)
        cur_lvl = inst["level"]
        max_lvl = weapon.upgrade.max_level
        if cur_lvl >= max_lvl:
            await ctx.send(f"**{weapon.name}** is already at max level ({max_lvl}).")
            return

        required = Counter(dict(weapon.upgrade.per_level_materials))
        if not required:
            await ctx.send(f"**{weapon.name}** has no upgrade recipe.")
            return

        provided = Counter(material_tokens)
        # Validate: provided must equal required exactly
        if provided != required:
            req_str = ", ".join(f"{i} x{q}" for i, q in required.items())
            await ctx.send(
                f"Wrong materials. To upgrade **{weapon.name}** L{cur_lvl} → L{cur_lvl+1} you need: {req_str}."
            )
            return

        # Validate inventory has the materials
        have = Counter(player.inventory)
        for item_id, qty in required.items():
            if have[item_id] < qty:
                label = items.get(item_id).name if items.get(item_id) else item_id
                await ctx.send(
                    f"Need {qty}x {label} (you have {have[item_id]})."
                )
                return

        # Consume + level up
        for item_id, qty in required.items():
            for _ in range(qty):
                player.inventory.remove(item_id)
        inst["level"] = cur_lvl + 1

        new_atk_bonus = pvp_engine.total_damage_bonus(player, weapon_id)
        await ctx.send(
            f"**{weapon.name}** upgraded to **L{inst['level']}**!\n"
            f"Attack bonus is now +{new_atk_bonus} "
            f"(+{weapon.upgrade.attack_per_level} per level, "
            f"+{weapon.upgrade.poise_per_level} poise/level)."
        )


    async def _attach(self, ctx, args: tuple[str, ...]):
        if len(args) < 2:
            known = ", ".join(sorted(weapon_skills.SKILLS.keys())) or "(none)"
            await ctx.send(
                "Usage: `!craft attach <weapon_id> <weapon_skill_id>`\n"
                f"Known weapon skills: {known}\n"
                "Only one skill may be attached per weapon. Attaching a new "
                "skill returns the previous one to your inventory."
            )
            return

        weapon_id = args[0].lower()
        skill_id = args[1].lower()

        weapon = weapons.get(weapon_id)
        if weapon is None:
            await ctx.send(f"Unknown weapon `{weapon_id}`.")
            return
        skill = weapon_skills.get(skill_id)
        if skill is None:
            known = ", ".join(sorted(weapon_skills.SKILLS.keys())) or "(none)"
            await ctx.send(f"Unknown weapon skill `{skill_id}`. Known: {known}.")
            return

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)

        if weapon_id not in player.inventory and player.equipped_weapon != weapon_id:
            await ctx.send(f"You don't own a **{weapon.name}**.")
            return
        if skill_id not in player.inventory:
            await ctx.send(f"You don't have a **{skill.name}** to attach.")
            return

        inst = pvp_engine.get_instance(player, weapon_id)
        previous_skill_id = inst.get("skill")

        # Consume the new skill from inventory.
        player.inventory.remove(skill_id)
        # Return the previous skill (if any) to inventory.
        if previous_skill_id and weapon_skills.get(previous_skill_id):
            player.inventory.append(previous_skill_id)

        inst["skill"] = skill_id

        prev_msg = ""
        if previous_skill_id:
            prev = weapon_skills.get(previous_skill_id)
            prev_msg = f" Previous skill **{prev.name if prev else previous_skill_id}** returned to inventory."

        await ctx.send(
            f"**{skill.name}** attached to **{weapon.name}**. "
            f"New attack available: `{skill.attack.id}` ({skill.attack.name}).{prev_msg}"
        )


async def setup(bot):
    await bot.add_cog(Crafting())
