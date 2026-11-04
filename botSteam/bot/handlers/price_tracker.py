from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    MenuAction,
    PriceGameAction,
    PriceTrackerAction,
    back_to_menu,
    cancel_input,
    price_game_kb,
    price_tracker_kb,
)
from bot.states import PriceTrackerForm
from services.storage import add_price_alert, get_price_alerts, remove_price_alert

router = Router()


async def _show_tracker(message, user_id: int, edit: bool = True):
    alerts = await get_price_alerts(user_id)
    text = (
        f"📈 <b>Трекер цен</b>\n\nАктивных алертов: <b>{len(alerts)}</b>\n\n"
        "Нажми на алерт чтобы удалить его, или добавь новый."
        if alerts else
        "📈 <b>Трекер цен</b>\n\nАлертов нет. Добавь первый!"
    )
    kb = price_tracker_kb(alerts)
    if edit:
        await message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)


@router.callback_query(MenuAction.filter(F.action == "price_tracker"))
async def cb_price_tracker(callback: CallbackQuery):
    await _show_tracker(callback.message, callback.from_user.id)
    await callback.answer()


@router.callback_query(PriceTrackerAction.filter(F.action == "delete"))
async def cb_pt_delete(callback: CallbackQuery, callback_data: PriceTrackerAction):
    await remove_price_alert(callback.from_user.id, int(callback_data.alert_id))
    await _show_tracker(callback.message, callback.from_user.id)
    await callback.answer("🗑 Алерт удалён.")


@router.callback_query(PriceTrackerAction.filter(F.action == "add"))
async def cb_pt_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📈 <b>Добавить алерт</b>\n\nВыбери игру:",
        parse_mode=ParseMode.HTML,
        reply_markup=price_game_kb(),
    )
    await callback.answer()


@router.callback_query(PriceGameAction.filter())
async def cb_pt_game(callback: CallbackQuery, callback_data: PriceGameAction, state: FSMContext):
    await state.set_state(PriceTrackerForm.waiting_item)
    await state.update_data(appid=callback_data.appid, game_name=callback_data.name)
    await callback.message.edit_text(
        f"📈 Трекер цен → <b>{callback_data.name}</b>\n\n"
        "Введи точное название предмета (market_hash_name):\n"
        "<i>Например: AK-47 | Redline (Field-Tested)</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_input(),
    )
    await callback.answer()


@router.message(PriceTrackerForm.waiting_item)
async def fsm_pt_item(message: Message, state: FSMContext):
    await state.update_data(item=message.text.strip())
    await state.set_state(PriceTrackerForm.waiting_price)
    await message.answer(
        "💵 Введи целевую цену в USD (например: <code>5.50</code>).\n"
        "Получишь уведомление, когда цена упадёт до этой суммы или ниже.",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_input(),
    )


@router.message(PriceTrackerForm.waiting_price)
async def fsm_pt_price(message: Message, state: FSMContext):
    try:
        target = float(message.text.strip().replace(",", "."))
        if target <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи корректную цену (число больше 0):", reply_markup=cancel_input())
        return

    data = await state.get_data()
    await state.clear()

    result = await add_price_alert(
        message.from_user.id,
        data["item"],
        int(data["appid"]),
        data["game_name"],
        target,
    )

    if result == "limit":
        await message.answer("❌ Достигнут лимит алертов (20).", reply_markup=back_to_menu())
        return

    await message.answer(
        f"✅ Алерт создан!\n\n"
        f"<b>{data['item']}</b> ({data['game_name']})\n"
        f"Уведомлю когда цена ≤ <b>${target:.2f}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_menu(),
    )
