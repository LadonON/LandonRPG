from collections import Counter
from discord.ext import commands

from ..services import players
from ..world import items, recipes, weapons, weapon_skills, pickaxes
from ..world import upgrade_scaling
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
                "`!craft upgrade <weapon_or_pickaxe>` — preview the next-level cost\n"
                "`!craft upgrade <weapon_or_pickaxe> <level>` — advance to that level (must be current + 1)\n"
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
                "Usage:\n"
                "`!craft upgrade <weapon_or_pickaxe_id>` — preview the next level's cost\n"
                "`!craft upgrade <weapon_or_pickaxe_id> <level>` — consume materials and advance to that level"
            )
            return

        target_id = args[0].lower()

        # Dispatch to whichever subsystem owns this id.
        weapon = weapons.get(target_id)
        pickaxe = pickaxes.get(target_id)
        if weapon is None and pickaxe is None:
            await ctx.send(
                f"Unknown weapon or pickaxe `{target_id}`. "
                f"Weapons: {', '.join(sorted(weapons.WEAPONS.keys()))}. "
                f"Pickaxes: {', '.join(sorted(pickaxes.PICKAXES.keys()))}."
            )
            return

        is_pickaxe = pickaxe is not None
        cfg = pickaxe if is_pickaxe else weapon
        target_name = cfg.name
        upgrade = cfg.upgrade

        player = players.get_or_create(ctx.author.id, ctx.author.display_name)
        equipped_slot = player.equipped_pickaxe if is_pickaxe else player.equipped_weapon
        if target_id not in player.inventory and equipped_slot != target_id:
            await ctx.send(f"You don't own a **{target_name}**.")
            return

        inst = (pickaxes.get_instance(player, target_id) if is_pickaxe
                else pvp_engine.get_instance(player, target_id))
        cur_lvl = inst["level"]
        max_lvl = upgrade.max_level
        if cur_lvl >= max_lvl:
            await ctx.send(f"**{target_name}** is already at max level ({max_lvl}).")
            return

        if not upgrade.per_level_materials:
            await ctx.send(f"**{target_name}** has no upgrade recipe.")
            return

        # ── Preview mode (no level arg) ──────────────────────────────────────
        if len(args) < 2:
            target_level = cur_lvl + 1
            tier = upgrade_scaling.tier_for(target_level)
            required = upgrade_scaling.required_for(upgrade.per_level_materials, target_level)
            have = Counter(player.inventory)
            lines = []
            for item_id, qty in required.items():
                label = items.get(item_id).name if items.get(item_id) else item_id
                lines.append(f"  {label} (`{item_id}`) — need {qty}, have {have.get(item_id, 0)}")
            await ctx.send(
                f"**{target_name}** L{cur_lvl} → L{target_level} ({tier.label} tier):\n"
                + "\n".join(lines)
                + f"\nRun: `!craft upgrade {target_id} {target_level}`"
            )
            return

        # ── Upgrade mode (level arg given) ───────────────────────────────────
        try:
            target_level = int(args[1])
        except ValueError:
            await ctx.send(
                f"Second argument must be a level number. Example: `!craft upgrade {target_id} {cur_lvl + 1}`."
            )
            return

        # Sequential constraint: each upgrade step advances by exactly one level.
        if target_level != cur_lvl + 1:
            await ctx.send(
                f"**{target_name}** must be L{target_level - 1} to upgrade to L{target_level} "
                f"(currently L{cur_lvl}). Run `!craft upgrade {target_id} {cur_lvl + 1}` instead."
            )
            return
        if target_level > max_lvl:
            await ctx.send(f"**{target_name}** caps at L{max_lvl}.")
            return

        tier = upgrade_scaling.tier_for(target_level)
        required = upgrade_scaling.required_for(upgrade.per_level_materials, target_level)

        # Validate inventory has the materials
        have = Counter(player.inventory)
        for item_id, qty in required.items():
            if have[item_id] < qty:
                label = items.get(item_id).name if items.get(item_id) else item_id
                req_str = ", ".join(f"{i} x{q}" for i, q in required.items())
                await ctx.send(
                    f"Need {qty}x {label} (you have {have[item_id]}). "
                    f"Full cost for L{cur_lvl} → L{target_level} ({tier.label}): {req_str}."
                )
                return

        # Consume + level up
        for item_id, qty in required.items():
            for _ in range(qty):
                player.inventory.remove(item_id)
        inst["level"] = target_level

        if is_pickaxe:
            new_eff = pickaxes.effective_pickaxe_level(player, target_id)
            await ctx.send(
                f"**{target_name}** upgraded to **L{inst['level']}**!\n"
                f"Effective pickaxe level is now **{new_eff}** "
                f"(+{upgrade.level_per_step}/upgrade step)."
            )
        else:
            new_atk_bonus = pvp_engine.total_damage_bonus(player, target_id)
            await ctx.send(
                f"**{target_name}** upgraded to **L{inst['level']}**!\n"
                f"Attack bonus is now +{new_atk_bonus} "
                f"(+{upgrade.attack_per_level} per level, "
                f"+{upgrade.poise_per_level} poise/level)."
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
