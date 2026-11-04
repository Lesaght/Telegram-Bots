from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class SteamAction(CallbackData, prefix="steam"):
    action: str
    steamid: str


class MenuAction(CallbackData, prefix="menu"):
    action: str


class FavoriteAction(CallbackData, prefix="fav"):
    action: str
    steamid: str


class InventoryAction(CallbackData, prefix="inv"):
    steamid: str
    appid: str


class OnlineAlertAction(CallbackData, prefix="oa"):
    steamid: str


class LeaderboardAction(CallbackData, prefix="lb"):
    steamid: str
    appid: str


class InvSearchAction(CallbackData, prefix="is"):
    steamid: str
    appid: str


class PriceTrackerAction(CallbackData, prefix="pt"):
    action: str
    alert_id: str = "0"


class PriceGameAction(CallbackData, prefix="ptg"):
    appid: str
    name: str


class ComparePickAction(CallbackData, prefix="cp"):
    op: str
    slot: str
    steamid: str


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Найти профиль", callback_data=MenuAction(action="profile"))
    builder.button(text="⭐ Избранное", callback_data=MenuAction(action="favorites"))
    builder.button(text="⚖️ Сравнить профили", callback_data=MenuAction(action="compare"))
    builder.button(text="🤝 Общие игры", callback_data=MenuAction(action="common_games"))
    builder.button(text="👥 Общие друзья", callback_data=MenuAction(action="common_friends"))
    builder.button(text="🏆 Топ друзей", callback_data=MenuAction(action="leaderboard"))
    builder.button(text="📈 Трекер цен", callback_data=MenuAction(action="price_tracker"))
    builder.button(text="🔔 Онлайн-алерты", callback_data=MenuAction(action="online_alerts"))
    builder.button(text="❓ Помощь", callback_data=MenuAction(action="help"))
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def player_actions(steamid: str, is_fav: bool = False, has_alert: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Друзья", callback_data=SteamAction(action="friends", steamid=steamid))
    builder.button(text="🎮 Недавние игры", callback_data=SteamAction(action="recent", steamid=steamid))
    builder.button(text="🕹 Игры", callback_data=SteamAction(action="games", steamid=steamid))
    builder.button(text="💰 Инвентарь", callback_data=SteamAction(action="inventory", steamid=steamid))
    builder.button(text="📊 CS2 стата", callback_data=SteamAction(action="cs2stats", steamid=steamid))
    builder.button(text="🏆 Топ друзей", callback_data=SteamAction(action="leaderboard", steamid=steamid))
    fav_text = "🗑 Убрать из избр." if is_fav else "⭐ В избранное"
    fav_data = FavoriteAction(action="remove" if is_fav else "add", steamid=steamid)
    alert_text = "🔕 Убрать алерт" if has_alert else "🔔 Алерт онлайн"
    builder.button(text=fav_text, callback_data=fav_data)
    builder.button(text=alert_text, callback_data=OnlineAlertAction(steamid=steamid))
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def inventory_select_kb(steamid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔫 CS2", callback_data=InventoryAction(steamid=steamid, appid="730"))
    builder.button(text="🗡 Dota 2", callback_data=InventoryAction(steamid=steamid, appid="570"))
    builder.button(text="🎩 TF2", callback_data=InventoryAction(steamid=steamid, appid="440"))
    builder.button(text="🃏 Карточки", callback_data=InventoryAction(steamid=steamid, appid="753"))
    builder.button(text="👤 Назад к профилю", callback_data=SteamAction(action="profile", steamid=steamid))
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def inv_search_select_kb(steamid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔫 CS2", callback_data=InvSearchAction(steamid=steamid, appid="730"))
    builder.button(text="🗡 Dota 2", callback_data=InvSearchAction(steamid=steamid, appid="570"))
    builder.button(text="🎩 TF2", callback_data=InvSearchAction(steamid=steamid, appid="440"))
    builder.button(text="🃏 Карточки", callback_data=InvSearchAction(steamid=steamid, appid="753"))
    builder.button(text="👤 Назад", callback_data=SteamAction(action="profile", steamid=steamid))
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def compare_pick_kb(
    op: str, slot: int, favs: list[dict], label: str = ""
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if label:

        pass
    for fav in favs[:10]:
        builder.button(
            text=f"👤 {fav['name']}",
            callback_data=ComparePickAction(op=op, slot=str(slot), steamid=fav["steamid"]),
        )
    builder.button(
        text="✏️ Ввести вручную",
        callback_data=ComparePickAction(op=op, slot=str(slot), steamid=""),
    )
    builder.button(text="❌ Отмена", callback_data=MenuAction(action="home"))
    builder.adjust(1)
    return builder.as_markup()


def leaderboard_games_kb(steamid: str, games: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for g in games[:10]:
        appid = str(g.get("appid", ""))
        name = g.get("name", appid)[:30]
        builder.button(text=name, callback_data=LeaderboardAction(steamid=steamid, appid=appid))
    builder.button(text="👤 Назад", callback_data=SteamAction(action="profile", steamid=steamid))
    builder.adjust(1)
    return builder.as_markup()


def price_tracker_kb(alerts: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for a in alerts:
        label = f"🗑 {a['market_hash_name'][:25]} (${a['target_price']:.2f})"
        builder.button(text=label, callback_data=PriceTrackerAction(action="delete", alert_id=str(a["id"])))
    builder.button(text="➕ Добавить алерт", callback_data=PriceTrackerAction(action="add"))
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    builder.adjust(1)
    return builder.as_markup()


def price_game_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔫 CS2", callback_data=PriceGameAction(appid="730", name="CS2"))
    builder.button(text="🗡 Dota 2", callback_data=PriceGameAction(appid="570", name="Dota 2"))
    builder.button(text="🎩 TF2", callback_data=PriceGameAction(appid="440", name="TF2"))
    builder.button(text="❌ Отмена", callback_data=MenuAction(action="home"))
    builder.adjust(3, 1)
    return builder.as_markup()


def online_alerts_kb(alerts: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for a in alerts:
        builder.button(
            text=f"🔕 {a['name']}",
            callback_data=OnlineAlertAction(steamid=a["steamid"]),
        )
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    builder.adjust(1)
    return builder.as_markup()


def games_result_kb(steamid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Случайная игра", callback_data=SteamAction(action="random_game", steamid=steamid))
    builder.button(text="👤 Профиль", callback_data=SteamAction(action="profile", steamid=steamid))
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    builder.adjust(1)
    return builder.as_markup()


def inventory_result_kb(steamid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Найти предмет", callback_data=SteamAction(action="inv_search", steamid=steamid))
    builder.button(text="👤 Профиль", callback_data=SteamAction(action="profile", steamid=steamid))
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    builder.adjust(1)
    return builder.as_markup()


def back_to_profile(steamid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Профиль", callback_data=SteamAction(action="profile", steamid=steamid))
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    builder.adjust(2)
    return builder.as_markup()


def back_to_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    return builder.as_markup()


def cancel_input() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data=MenuAction(action="home"))
    return builder.as_markup()


def favorites_list_kb(favs: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for fav in favs:
        builder.button(
            text=f"👤 {fav['name']}",
            callback_data=SteamAction(action="profile", steamid=fav["steamid"]),
        )
    builder.button(text="🏠 Главное меню", callback_data=MenuAction(action="home"))
    builder.adjust(1)
    return builder.as_markup()
