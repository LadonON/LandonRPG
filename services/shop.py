from ..world import items

SHOP_ZONE = "village"

SHOP_INVENTORY: list[str] = [
    "small_potion",
    "large_potion",
    "rusty_sword",
    "iron_sword",
    "leather_armor",
    "iron_armor",
]
BUY_MARKUP = 2  # buy at 2x the sell value


def sell_price(item_id: str) -> int:
    item = items.get(item_id)
    return item.value if item else 0


def buy_price(item_id: str) -> int:
    item = items.get(item_id)
    return item.value * BUY_MARKUP if item else 0


def sell_items(player, requested: list[str]) -> tuple[list[tuple[str, int]], list[str]]:
    sold: list[tuple[str, int]] = []
    missing: list[str] = []
    for raw in requested:
        item_id = raw.lower()
        gold = sell_price(item_id)
        if gold > 0 and item_id in player.inventory:
            player.inventory.remove(item_id)
            player.gold += gold
            sold.append((item_id, gold))
        else:
            missing.append(item_id)
    return sold, missing


def sell_all(player) -> list[tuple[str, int]]:
    sold: list[tuple[str, int]] = []
    remaining: list[str] = []
    for item_id in player.inventory:
        gold = sell_price(item_id)
        if gold > 0:
            player.gold += gold
            sold.append((item_id, gold))
        else:
            remaining.append(item_id)
    player.inventory = remaining
    return sold


def buy(player, item_id: str) -> tuple[bool, str]:
    item_id = item_id.lower()
    if item_id not in SHOP_INVENTORY:
        return False, f"The shop doesn't sell `{item_id}`."
    cost = buy_price(item_id)
    if player.gold < cost:
        return False, f"Need {cost}g, have {player.gold}g."
    player.gold -= cost
    player.inventory.append(item_id)
    return True, f"Bought {items.get(item_id).name} for {cost}g."
