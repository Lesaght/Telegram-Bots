import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    InventoryAction,
    InvSearchAction,
    SteamAction,
    back_to_profile,
    cancel_input,
    inv_search_select_kb,
    inventory_result_kb,
    inventory_select_kb,
)
from bot.states import InventorySearchForm
from services.steam import get_inventory, get_item_price, get_player_summaries, make_session

router = Router()

_GAMES: dict[str, tuple[str, int]] = {
    "730": ("CS2", 2),
    "570": ("Dota 2", 2),
    "440": ("TF2", 2),
    "753": ("Карточки Steam", 6),
}

_CARD_TYPES = {
    "Trading Card": "🃏 Карточки",
    "Foil Trading Card": "✨ Фольга",
    "Profile Background": "🖼 Фоны профиля",
    "Emoticon": "😀 Смайлики",
    "Steam Gems": "💎 Камни",
    "Booster Pack": "📦 Бустер",
}


def _format_cards_result(
    items: list[dict],
    total_count: int,
    priced: list[tuple[dict, float]],
    total_value: float,
) -> list[str]:
    by_type: dict[str, list[dict]] = {}
    for it in items:
        raw_type = it.get("type", "")
        label = next((v for k, v in _CARD_TYPES.items() if k in raw_type), "📁 Прочее")
        by_type.setdefault(label, []).append(it)

    lines = [
        "🃏 <b>Карточки Steam</b>\n",
        f"📦 Предметов всего: <b>{total_count}</b>",
        f"💵 Оценочная стоимость: <b>${total_value:,.2f}</b>\n",
    ]

    for label, group in sorted(by_type.items()):
        total_qty = sum(it["count"] for it in group)
        lines.append(f"{label}: <b>{len(group)} уник. ({total_qty} шт.)</b>")

    priced_map = {it["market_hash_name"]: val for it, val in priced}
    valuable = [(it, priced_map[it["market_hash_name"]]) for it in items if it["market_hash_name"] in priced_map]
    valuable.sort(key=lambda x: x[1], reverse=True)

    if valuable:
        lines.append("\n🏆 <b>Ценные предметы:</b>")
        for it, val in valuable[:10]:
            qty = f" × {it['count']}" if it["count"] > 1 else ""
            lines.append(f"• {it['name']}{qty} — <b>${val:,.2f}</b>")

    return lines


@router.callback_query(SteamAction.filter(F.action == "inventory"))
async def cb_inventory_select(callback: CallbackQuery, callback_data: SteamAction):
    steamid = callback_data.steamid
    async with make_session() as session:
        players = await get_player_summaries(session, [steamid])
    name = players[0].get("personaname", steamid) if players else steamid

    text = f"💰 <b>Инвентарь — {name}</b>\n\nВыбери игру:"
    kb = inventory_select_kb(steamid)
    if callback.message.photo:
        await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    await callback.answer()


@router.callback_query(InventoryAction.filter())
async def cb_inventory(callback: CallbackQuery, callback_data: InventoryAction):
    steamid = callback_data.steamid
    appid_str = callback_data.appid
    game_name, contextid = _GAMES.get(appid_str, ("Неизвестно", 2))
    appid = int(appid_str)

    if callback.message.photo:
        wait_msg = await callback.message.answer(f"⏳ Загружаю инвентарь {game_name}...")
    else:
        wait_msg = await callback.message.edit_text(f"⏳ Загружаю инвентарь {game_name}...")

    async with make_session() as session:
        items, total_count = await get_inventory(session, steamid, appid, contextid)

        if not items:
            await wait_msg.edit_text(
                f"❌ Инвентарь {game_name} недоступен (профиль закрыт или пуст).",
                reply_markup=back_to_profile(steamid),
            )
            await callback.answer()
            return

        marketable = [it for it in items if it["marketable"]]
        await wait_msg.edit_text(f"⏳ Загружаю цены ({len(marketable)} уникальных предметов)...")

        sem = asyncio.Semaphore(5)

        async def fetch(item: dict) -> tuple[dict, float | None]:
            async with sem:
                price = await get_item_price(session, appid, item["market_hash_name"])
                await asyncio.sleep(0.3)
            return item, price

        results = await asyncio.gather(*[fetch(it) for it in marketable], return_exceptions=True)

    priced: list[tuple[dict, float]] = []
    for res in results:
        if isinstance(res, Exception):
            continue
        item, price = res
        if price is not None:
            priced.append((item, price * item["count"]))

    priced.sort(key=lambda x: x[1], reverse=True)
    total_value = sum(v for _, v in priced)

    if appid_str == "753":
        lines = _format_cards_result(items, total_count, priced, total_value)
    else:
        lines = [
            f"💰 <b>Инвентарь {game_name}</b>\n",
            f"📦 Предметов всего: <b>{total_count}</b>",
            f"🏷 Торгуемых (уник.): <b>{len(marketable)}</b>",
            f"💵 Оценочная стоимость: <b>${total_value:,.2f}</b>",
        ]
        if priced:
            lines.append("\n🏆 <b>Топ по стоимости:</b>")
            for item, value in priced[:10]:
                qty = f" × {item['count']}" if item["count"] > 1 else ""
                lines.append(f"• {item['name']}{qty} — <b>${value:,.2f}</b>")
        if len(marketable) - len(priced) > 0:
            lines.append(f"\n<i>Ещё {len(marketable) - len(priced)} предметов без цены не учтено</i>")

    await wait_msg.edit_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=inventory_result_kb(steamid),
    )
    await callback.answer()


@router.callback_query(SteamAction.filter(F.action == "inv_search"))
async def cb_inv_search_select(callback: CallbackQuery, callback_data: SteamAction):
    steamid = callback_data.steamid
    text = "🔍 <b>Поиск в инвентаре</b>\n\nВыбери игру:"
    kb = inv_search_select_kb(steamid)
    if callback.message.photo:
        await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    await callback.answer()


@router.callback_query(InvSearchAction.filter())
async def cb_inv_search_game(callback: CallbackQuery, callback_data: InvSearchAction, state: FSMContext):
    await state.set_state(InventorySearchForm.waiting_query)
    await state.update_data(steamid=callback_data.steamid, appid=callback_data.appid)
    game_name = _GAMES.get(callback_data.appid, ("Игра", 2))[0]
    await callback.message.edit_text(
        f"🔍 Поиск в инвентаре <b>{game_name}</b>\n\nВведи название предмета (или его часть):",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_input(),
    )
    await callback.answer()


@router.message(InventorySearchForm.waiting_query)
async def fsm_inv_search(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    steamid = data["steamid"]
    appid_str = data["appid"]
    game_name, contextid = _GAMES.get(appid_str, ("Игра", 2))
    appid = int(appid_str)
    query = message.text.strip().lower()

    wait = await message.answer(f"⏳ Ищу «{message.text.strip()}» в инвентаре {game_name}...")

    async with make_session() as session:
        items, _ = await get_inventory(session, steamid, appid, contextid)

    if not items:
        await wait.edit_text(
            f"❌ Инвентарь {game_name} недоступен или пуст.",
            reply_markup=back_to_profile(steamid),
        )
        return

    found = [it for it in items if query in it["name"].lower() or query in it["market_hash_name"].lower()]

    if not found:
        await wait.edit_text(
            f"🔍 По запросу «{message.text.strip()}» ничего не найдено.",
            reply_markup=back_to_profile(steamid),
        )
        return

    lines = [f"🔍 <b>Найдено {len(found)} предмет(ов):</b>\n"]
    for it in found[:20]:
        qty = f" × {it['count']}" if it["count"] > 1 else ""
        tradeable = "" if it["marketable"] else " <i>(не торгуемый)</i>"
        lines.append(f"• {it['name']}{qty}{tradeable}")
    if len(found) > 20:
        lines.append(f"\n…и ещё {len(found) - 20}")

    await wait.edit_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_profile(steamid),
    )
