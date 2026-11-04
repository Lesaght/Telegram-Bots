from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import SteamAction, back_to_menu, back_to_profile
from bot.states import SteamForm
from services.steam import get_player_summaries, get_recently_played, make_session, parse_steam_id, resolve_vanity

router = Router()


async def _show_recent(steamid_raw: str, message: Message):
    async with make_session() as session:
        steamid = await resolve_vanity(session, steamid_raw)
        if not steamid:
            await message.answer("❌ Игрок не найден.", reply_markup=back_to_menu())
            return

        games = await get_recently_played(session, steamid)
        players = await get_player_summaries(session, [steamid])

    if not games:
        await message.answer(
            "🎮 Нет недавних игр (или профиль закрыт).",
            reply_markup=back_to_profile(steamid),
        )
        return

    name = players[0].get("personaname", "Игрок") if players else "Игрок"
    lines = [f"🎮 Недавние игры <b>{name}</b>:\n"]
    for g in games:
        hours_2w = g.get("playtime_2weeks", 0) / 60
        hours_total = g.get("playtime_forever", 0) / 60
        lines.append(
            f"• <b>{g['name']}</b>\n"
            f"  За 2 недели: {hours_2w:.1f} ч | Всего: {hours_total:.1f} ч"
        )

    await message.answer(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_profile(steamid),
    )


@router.message(Command("recent"))
async def cmd_recent(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажи ник или ссылку: /recent ‹ник›")
        return
    await _show_recent(parse_steam_id(args[1]), message)


@router.message(SteamForm.waiting_recent)
async def fsm_recent(message: Message, state: FSMContext):
    await state.clear()
    await _show_recent(parse_steam_id(message.text), message)


@router.callback_query(SteamAction.filter(F.action == "recent"))
async def cb_recent(callback: CallbackQuery, callback_data: SteamAction):
    await _show_recent(callback_data.steamid, callback.message)
    await callback.answer()
