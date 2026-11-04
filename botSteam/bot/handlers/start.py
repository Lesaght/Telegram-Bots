from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    MenuAction,
    back_to_menu,
    cancel_input,
    favorites_list_kb,
    main_menu,
    online_alerts_kb,
)
from bot.states import SteamForm
from services.storage import get_favorites, get_online_alerts

router = Router()

WELCOME_TEXT = (
    "👋 Привет! Я <b>Steam-бот</b>.\n\n"
    "Показываю профили, статистику, инвентарь и многое другое.\n"
    "Выбери действие:"
)

HELP_TEXT = (
    "❓ <b>Как пользоваться ботом:</b>\n\n"
    "Нажми кнопку в меню или используй команды:\n\n"
    "• /profile ‹ник› — профиль игрока\n"
    "• /friends ‹ник› — список друзей\n"
    "• /recent ‹ник› — недавние игры\n\n"
    "<b>Примеры:</b>\n"
    "<code>/profile valve</code>\n"
    "<code>/profile https://steamcommunity.com/id/valve</code>"
)


_OWN_ACTIONS = frozenset({"home", "help", "profile", "friends", "recent", "favorites", "online_alerts"})


async def _send(msg, text: str, **kwargs):
    """edit_text if text message, answer if photo/other."""
    if msg.photo or not msg.text:
        await msg.answer(text, **kwargs)
    else:
        await msg.edit_text(text, **kwargs)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, parse_mode=ParseMode.HTML, reply_markup=main_menu())


@router.callback_query(MenuAction.filter(F.action.in_(_OWN_ACTIONS)))
async def menu_callback(callback: CallbackQuery, callback_data: MenuAction, state: FSMContext):
    action = callback_data.action
    msg = callback.message

    if action == "home":
        await state.clear()
        await _send(msg, WELCOME_TEXT, parse_mode=ParseMode.HTML, reply_markup=main_menu())

    elif action == "help":
        await _send(msg, HELP_TEXT, parse_mode=ParseMode.HTML, reply_markup=back_to_menu())

    elif action == "profile":
        await state.set_state(SteamForm.waiting_profile)
        await _send(msg, "🔍 Введи ник или ссылку на профиль Steam:", reply_markup=cancel_input())

    elif action == "friends":
        await state.set_state(SteamForm.waiting_friends)
        await _send(msg, "👥 Введи ник или ссылку для просмотра друзей:", reply_markup=cancel_input())

    elif action == "recent":
        await state.set_state(SteamForm.waiting_recent)
        await _send(msg, "🎮 Введи ник или ссылку для просмотра недавних игр:", reply_markup=cancel_input())

    elif action == "favorites":
        favs = await get_favorites(callback.from_user.id)
        if not favs:
            await _send(msg, "⭐ <b>Избранное пусто.</b>\n\nНайди профиль и нажми «⭐ В избранное».",
                        parse_mode=ParseMode.HTML, reply_markup=back_to_menu())
        else:
            await _send(msg, f"⭐ <b>Избранные профили ({len(favs)}):</b>",
                        parse_mode=ParseMode.HTML, reply_markup=favorites_list_kb(favs))

    elif action == "online_alerts":
        alerts = await get_online_alerts(callback.from_user.id)
        if not alerts:
            await _send(msg,
                        "🔔 <b>Онлайн-алерты</b>\n\nНет активных алертов.\n\n"
                        "Открой профиль игрока и нажми «🔔 Алерт онлайн».",
                        parse_mode=ParseMode.HTML, reply_markup=back_to_menu())
        else:
            await _send(msg,
                        f"🔔 <b>Онлайн-алерты ({len(alerts)}):</b>\n\nНажми на игрока чтобы снять алерт.",
                        parse_mode=ParseMode.HTML, reply_markup=online_alerts_kb(alerts))

    await callback.answer()
