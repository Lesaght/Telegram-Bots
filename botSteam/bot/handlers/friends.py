from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import SteamAction, back_to_menu, back_to_profile
from bot.states import SteamForm
from services.steam import get_friends, get_player_summaries, make_session, parse_steam_id, resolve_vanity
from utils.formatters import format_player

router = Router()


async def _show_friends(steamid_raw: str, message: Message):
    wait_msg = await message.answer("⏳ Загружаю список друзей...")

    async with make_session() as session:
        steamid = await resolve_vanity(session, steamid_raw)
        if not steamid:
            await wait_msg.edit_text("❌ Игрок не найден.", reply_markup=back_to_menu())
            return

        friends_raw = await get_friends(session, steamid)
        if not friends_raw:
            await wait_msg.edit_text(
                "❌ Список друзей недоступен (профиль закрыт или нет друзей).",
                reply_markup=back_to_menu(),
            )
            return

        friend_ids = [f["steamid"] for f in friends_raw]
        players: list[dict] = []
        for i in range(0, len(friend_ids), 100):
            batch = await get_player_summaries(session, friend_ids[i: i + 100])
            players.extend(batch)

    players.sort(
        key=lambda p: (
            0 if p.get("gameextrainfo") else 1 if p.get("personastate", 0) > 0 else 2
        )
    )

    online = [p for p in players if p.get("personastate", 0) > 0]
    playing = [p for p in players if p.get("gameextrainfo")]

    header = (
        f"👥 Друзья: {len(players)}\n"
        f"🟢 Онлайн: {len(online)} | 🎮 Играют: {len(playing)}\n\n"
    )

    lines = [format_player(p) for p in players[:30]]
    text = header + "\n\n".join(lines)

    if len(players) > 30:
        text += f"\n\n…и ещё {len(players) - 30} друзей (показаны первые 30)"

    await wait_msg.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=back_to_profile(steamid),
    )


@router.message(Command("friends"))
async def cmd_friends(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажи ник или ссылку: /friends ‹ник›")
        return
    await _show_friends(parse_steam_id(args[1]), message)


@router.message(SteamForm.waiting_friends)
async def fsm_friends(message: Message, state: FSMContext):
    await state.clear()
    await _show_friends(parse_steam_id(message.text), message)


@router.callback_query(SteamAction.filter(F.action == "friends"))
async def cb_friends(callback: CallbackQuery, callback_data: SteamAction):
    await _show_friends(callback_data.steamid, callback.message)
    await callback.answer()
