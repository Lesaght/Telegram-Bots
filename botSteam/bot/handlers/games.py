import random

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from bot.keyboards.inline import SteamAction, back_to_profile, games_result_kb
from services.steam import get_owned_games, make_session

router = Router()


@router.callback_query(SteamAction.filter(F.action == "games"))
async def cb_games(callback: CallbackQuery, callback_data: SteamAction):
    steamid = callback_data.steamid
    if callback.message.photo:
        wait_msg = await callback.message.answer("⏳ Загружаю список игр...")
    else:
        wait_msg = await callback.message.edit_text("⏳ Загружаю список игр...")

    async with make_session() as session:
        games = await get_owned_games(session, steamid)

    if not games:
        await wait_msg.edit_text(
            "❌ Список игр недоступен (профиль закрыт или библиотека пуста).",
            reply_markup=back_to_profile(steamid),
        )
        await callback.answer()
        return

    games_sorted = sorted(games, key=lambda g: g.get("playtime_forever", 0), reverse=True)
    total = len(games)
    top = games_sorted[:15]

    lines = [f"🕹 <b>Библиотека:</b> {total} игр\n"]
    for i, g in enumerate(top, 1):
        hours = g.get("playtime_forever", 0) / 60
        name = g.get("name", f"App {g.get('appid')}")
        time_str = f"{hours:.0f} ч" if hours >= 1 else "< 1 ч"
        lines.append(f"{i}. <b>{name}</b> — {time_str}")

    if total > 15:
        lines.append(f"\n…и ещё {total - 15} игр")

    await wait_msg.edit_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=games_result_kb(steamid),
    )
    await callback.answer()


@router.callback_query(SteamAction.filter(F.action == "random_game"))
async def cb_random_game(callback: CallbackQuery, callback_data: SteamAction):
    steamid = callback_data.steamid
    if callback.message.photo:
        wait_msg = await callback.message.answer("🎲 Выбираю случайную игру...")
    else:
        wait_msg = await callback.message.edit_text("🎲 Выбираю случайную игру...")

    async with make_session() as session:
        games = await get_owned_games(session, steamid)

    if not games:
        await wait_msg.edit_text(
            "❌ Библиотека недоступна.",
            reply_markup=back_to_profile(steamid),
        )
        await callback.answer()
        return

    game = random.choice(games)
    name = game.get("name", f"App {game.get('appid')}")
    hours = game.get("playtime_forever", 0) / 60
    appid = game.get("appid")

    store_url = f"https://store.steampowered.com/app/{appid}"
    lines = [
        "🎲 <b>Случайная игра из библиотеки:</b>\n",
        f"🎮 <b>{name}</b>",
        f"⏱ Наиграно: <b>{hours:.0f} ч</b>" if hours >= 1 else "⏱ Наиграно: <b>< 1 ч</b>",
        f"🔗 <a href='{store_url}'>Steam Store</a>",
    ]

    await wait_msg.edit_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_profile(steamid),
        disable_web_page_preview=True,
    )
    await callback.answer()
