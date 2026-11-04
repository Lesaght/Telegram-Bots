import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    LeaderboardAction,
    MenuAction,
    SteamAction,
    back_to_menu,
    back_to_profile,
    cancel_input,
    leaderboard_games_kb,
)
from bot.states import LeaderboardForm
from services.steam import get_friends, get_owned_games, get_player_summaries, make_session, parse_steam_id, resolve_vanity

router = Router()


@router.callback_query(SteamAction.filter(F.action == "leaderboard"))
async def cb_leaderboard_start(callback: CallbackQuery, callback_data: SteamAction):
    steamid = callback_data.steamid
    if callback.message.photo:
        wait_msg = await callback.message.answer("⏳ Загружаю библиотеку...")
    else:
        wait_msg = await callback.message.edit_text("⏳ Загружаю библиотеку...")

    async with make_session() as session:
        games = await get_owned_games(session, steamid)

    if not games:
        await wait_msg.edit_text(
            "❌ Библиотека недоступна (профиль закрыт).",
            reply_markup=back_to_profile(steamid),
        )
        await callback.answer()
        return

    top_games = sorted(games, key=lambda g: g.get("playtime_forever", 0), reverse=True)[:10]

    await wait_msg.edit_text(
        "🏆 <b>Топ друзей в игре</b>\n\nВыбери игру:",
        parse_mode=ParseMode.HTML,
        reply_markup=leaderboard_games_kb(steamid, top_games),
    )
    await callback.answer()


@router.callback_query(MenuAction.filter(F.action == "leaderboard"))
async def cb_menu_leaderboard(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LeaderboardForm.waiting_profile)
    await callback.message.edit_text(
        "🏆 <b>Топ друзей в игре</b>\n\nВведи ник или ссылку профиля, чьих друзей сравнить:",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_input(),
    )
    await callback.answer()


@router.message(LeaderboardForm.waiting_profile)
async def fsm_leaderboard_profile(message: Message, state: FSMContext):
    await state.clear()
    wait = await message.answer("⏳ Загружаю библиотеку...")

    async with make_session() as session:
        steamid = await resolve_vanity(session, parse_steam_id(message.text))
        if not steamid:
            await wait.edit_text("❌ Игрок не найден.", reply_markup=back_to_menu())
            return
        games = await get_owned_games(session, steamid)

    if not games:
        await wait.edit_text("❌ Библиотека недоступна.", reply_markup=back_to_menu())
        return

    top_games = sorted(games, key=lambda g: g.get("playtime_forever", 0), reverse=True)[:10]
    await wait.edit_text(
        "🏆 <b>Топ друзей в игре</b>\n\nВыбери игру:",
        parse_mode=ParseMode.HTML,
        reply_markup=leaderboard_games_kb(steamid, top_games),
    )


@router.callback_query(LeaderboardAction.filter())
async def cb_leaderboard_game(callback: CallbackQuery, callback_data: LeaderboardAction):
    steamid = callback_data.steamid
    appid = int(callback_data.appid)

    wait_msg = await callback.message.edit_text("⏳ Собираю данные друзей...")

    async with make_session() as session:
        friends_raw = await get_friends(session, steamid)
        if not friends_raw:
            await wait_msg.edit_text(
                "❌ Список друзей недоступен (профиль закрыт).",
                reply_markup=back_to_menu(),
            )
            await callback.answer()
            return

        friend_ids = [f["steamid"] for f in friends_raw]

        sem = asyncio.Semaphore(8)

        async def fetch_playtime(fid: str) -> tuple[str, int]:
            async with sem:
                games = await get_owned_games(session, fid)
            for g in games:
                if g.get("appid") == appid:
                    return fid, g.get("playtime_forever", 0)
            return fid, 0

        results = await asyncio.gather(*[fetch_playtime(fid) for fid in friend_ids], return_exceptions=True)

        playtimes = [(fid, pt) for r in results if not isinstance(r, Exception) for fid, pt in [r] if pt > 0]
        playtimes.sort(key=lambda x: x[1], reverse=True)
        top_ids = [fid for fid, _ in playtimes[:10]]

        if not top_ids:
            await wait_msg.edit_text(
                "😔 Никто из друзей не играл в эту игру (или у них закрытые профили).",
                reply_markup=back_to_menu(),
            )
            await callback.answer()
            return

        players = await get_player_summaries(session, top_ids)

    name_map = {p["steamid"]: p.get("personaname", "?") for p in players}
    pt_map = {fid: pt for fid, pt in playtimes}

    lines = ["🏆 <b>Топ друзей по часам в игре:</b>\n"]
    for i, fid in enumerate(top_ids, 1):
        hours = pt_map.get(fid, 0) / 60
        name = name_map.get(fid, fid)
        lines.append(f"{i}. <b>{name}</b> — {hours:.0f} ч")

    await wait_msg.edit_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_menu(),
    )
    await callback.answer()
