import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import SteamAction, player_actions
from bot.states import SteamForm
from services.steam import (
    get_player_bans,
    get_player_summaries,
    get_steam_level,
    make_session,
    parse_steam_id,
    resolve_vanity,
)
from services.storage import has_online_alert, is_favorite
from utils.formatters import format_bans, format_player, format_profile_extra

router = Router()


async def _show_profile(steamid_raw: str, message: Message, user_id: int):
    async with make_session() as session:
        steamid = await resolve_vanity(session, steamid_raw)
        if not steamid:
            await message.answer("❌ Игрок не найден. Проверь ник или ссылку.")
            return

        players, level, bans_list = await asyncio.gather(
            get_player_summaries(session, [steamid]),
            get_steam_level(session, steamid),
            get_player_bans(session, [steamid]),
        )

        if not players:
            await message.answer("❌ Не удалось получить данные профиля.")
            return

        player = players[0]

    ban = bans_list[0] if bans_list else {}
    avatar = player.get("avatarfull")
    text = format_player(player)

    if player.get("realname"):
        text = f"👤 {player['realname']}\n" + text
    if player.get("loccountrycode"):
        text += f"\n   🌍 {player['loccountrycode']}"

    text += format_profile_extra(player, level)
    text += format_bans(ban)

    fav, alert = await asyncio.gather(
        is_favorite(user_id, steamid),
        has_online_alert(user_id, steamid),
    )
    kb = player_actions(steamid, fav, alert)

    if avatar:
        await message.answer_photo(avatar, caption=text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажи ник или ссылку: /profile ‹ник›")
        return
    await _show_profile(parse_steam_id(args[1]), message, message.from_user.id)


@router.message(SteamForm.waiting_profile)
async def fsm_profile(message: Message, state: FSMContext):
    await state.clear()
    await _show_profile(parse_steam_id(message.text), message, message.from_user.id)


@router.callback_query(SteamAction.filter(F.action == "profile"))
async def cb_profile(callback: CallbackQuery, callback_data: SteamAction):
    await _show_profile(callback_data.steamid, callback.message, callback.from_user.id)
    await callback.answer()
