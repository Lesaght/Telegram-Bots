import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    ComparePickAction,
    MenuAction,
    SteamAction,
    back_to_menu,
    cancel_input,
    compare_pick_kb,
)
from bot.states import CompareForm
from services.steam import (
    get_friends,
    get_owned_games,
    get_player_bans,
    get_player_summaries,
    get_steam_level,
    make_session,
    parse_steam_id,
    resolve_vanity,
)
from services.storage import get_favorites

router = Router()

_OP_LABELS = {
    "compare": "⚖️ Сравнение профилей",
    "common_games": "🤝 Общие игры",
    "common_friends": "👥 Общие друзья",
}


async def _resolve(session, raw: str) -> str | None:
    return await resolve_vanity(session, parse_steam_id(raw))


async def _start_compare_flow(callback: CallbackQuery, state: FSMContext, op: str):
    await state.update_data(op=op)
    label = _OP_LABELS.get(op, op)
    favs = await get_favorites(callback.from_user.id)

    if favs:
        kb = compare_pick_kb(op, 1, favs)
        text = f"{label}\n\nВыбери <b>первого</b> игрока из избранного или введи вручную:"
        if callback.message.photo:
            await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)
        else:
            await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await state.set_state(CompareForm.waiting_first)
        text = f"{label}\n\nВведи ник или ссылку <b>первого</b> игрока:"
        if callback.message.photo:
            await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=cancel_input())
        else:
            await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=cancel_input())

    await callback.answer()


@router.callback_query(MenuAction.filter(F.action == "compare"))
async def cb_menu_compare(callback: CallbackQuery, state: FSMContext):
    await _start_compare_flow(callback, state, "compare")


@router.callback_query(MenuAction.filter(F.action == "common_games"))
async def cb_menu_common_games(callback: CallbackQuery, state: FSMContext):
    await _start_compare_flow(callback, state, "common_games")


@router.callback_query(MenuAction.filter(F.action == "common_friends"))
async def cb_menu_common_friends(callback: CallbackQuery, state: FSMContext):
    await _start_compare_flow(callback, state, "common_friends")


@router.callback_query(ComparePickAction.filter())
async def cb_compare_pick(callback: CallbackQuery, callback_data: ComparePickAction, state: FSMContext):
    op = callback_data.op
    slot = callback_data.slot
    steamid = callback_data.steamid
    label = _OP_LABELS.get(op, op)

    if steamid == "":

        if slot == "1":
            await state.update_data(op=op)
            await state.set_state(CompareForm.waiting_first)
            text = f"{label}\n\nВведи ник или ссылку <b>первого</b> игрока:"
        else:
            data = await state.get_data()
            await state.update_data(op=op, first=data.get("first"))
            await state.set_state(CompareForm.waiting_second)
            text = f"{label}\n\nВведи ник или ссылку <b>второго</b> игрока:"
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=cancel_input())
        await callback.answer()
        return

    if slot == "1":
        await state.update_data(op=op, first=steamid)
        favs = await get_favorites(callback.from_user.id)
        first_name = next((f["name"] for f in favs if f["steamid"] == steamid), steamid)
        kb = compare_pick_kb(op, 2, favs)
        await callback.message.edit_text(
            f"{label}\n\n✅ Первый: <b>{first_name}</b>\n\nВыбери <b>второго</b> игрока:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        await callback.answer()
    else:

        data = await state.get_data()
        first_id = data.get("first")
        await state.clear()

        wait = await callback.message.edit_text("⏳ Загружаю данные...")
        async with make_session() as session:
            if op == "compare":
                text = await _do_compare(session, first_id, steamid)
            elif op == "common_games":
                text = await _do_common_games(session, first_id, steamid)
            elif op == "common_friends":
                text = await _do_common_friends(session, first_id, steamid)
            else:
                text = "Неизвестная операция."

        await wait.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=back_to_menu())
        await callback.answer()


@router.callback_query(SteamAction.filter(F.action == "compare_with"))
async def cb_compare_with(callback: CallbackQuery, callback_data: SteamAction, state: FSMContext):
    await state.update_data(op="compare", first=callback_data.steamid)
    favs = await get_favorites(callback.from_user.id)

    if favs:
        kb = compare_pick_kb("compare", 2, favs)
        await callback.message.answer(
            "⚖️ <b>Сравнение</b>\n\nВыбери <b>второго</b> игрока из избранного или введи вручную:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
    else:
        await state.set_state(CompareForm.waiting_second)
        await callback.message.answer(
            "⚖️ <b>Сравнение</b>\n\nВведи ник или ссылку <b>второго</b> игрока:",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_input(),
        )
    await callback.answer()


@router.message(CompareForm.waiting_first)
async def fsm_compare_first(message: Message, state: FSMContext):
    data = await state.get_data()
    op = data.get("op", "compare")

    async with make_session() as session:
        steamid = await _resolve(session, message.text)

    if not steamid:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз:", reply_markup=cancel_input())
        return

    await state.update_data(first=steamid)
    label = _OP_LABELS.get(op, op)
    favs = await get_favorites(message.from_user.id)

    if favs:
        await state.set_state(CompareForm.waiting_second)
        kb = compare_pick_kb(op, 2, favs)
        await message.answer(
            f"{label}\n\nТеперь выбери <b>второго</b> игрока из избранного или введи вручную:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
    else:
        await state.set_state(CompareForm.waiting_second)
        await message.answer(
            f"{label}\n\nТеперь введи ник или ссылку <b>второго</b> игрока:",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_input(),
        )


@router.message(CompareForm.waiting_second)
async def fsm_compare_second(message: Message, state: FSMContext):
    data = await state.get_data()
    op = data.get("op", "compare")
    first_id = data.get("first")
    await state.clear()

    wait = await message.answer("⏳ Загружаю данные...")

    async with make_session() as session:
        second_id = await _resolve(session, message.text)
        if not second_id:
            await wait.edit_text("❌ Второй игрок не найден.", reply_markup=back_to_menu())
            return

        if op == "compare":
            text = await _do_compare(session, first_id, second_id)
        elif op == "common_games":
            text = await _do_common_games(session, first_id, second_id)
        elif op == "common_friends":
            text = await _do_common_friends(session, first_id, second_id)
        else:
            text = "Неизвестная операция."

    await wait.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=back_to_menu())


async def _do_compare(session, sid1: str, sid2: str) -> str:
    (p1_list, p2_list), (lvl1, lvl2), (g1, g2), bans = await asyncio.gather(
        asyncio.gather(
            get_player_summaries(session, [sid1]),
            get_player_summaries(session, [sid2]),
        ),
        asyncio.gather(get_steam_level(session, sid1), get_steam_level(session, sid2)),
        asyncio.gather(get_owned_games(session, sid1), get_owned_games(session, sid2)),
        get_player_bans(session, [sid1, sid2]),
    )

    if not p1_list or not p2_list:
        return "❌ Не удалось получить данные одного из профилей."

    p1, p2 = p1_list[0], p2_list[0]
    n1, n2 = p1.get("personaname", "?"), p2.get("personaname", "?")

    total_h1 = sum(g.get("playtime_forever", 0) for g in g1) / 60
    total_h2 = sum(g.get("playtime_forever", 0) for g in g2) / 60

    bans_map = {b["SteamId"]: b for b in bans}
    b1 = bans_map.get(sid1, {})
    b2 = bans_map.get(sid2, {})
    vac1 = "🚫 Да" if b1.get("VACBanned") else "✅ Нет"
    vac2 = "🚫 Да" if b2.get("VACBanned") else "✅ Нет"

    lines = [
        f"⚖️ <b>Сравнение профилей</b>\n",
        f"{'':12} <b>{n1[:10]:<10}</b> <b>{n2[:10]}</b>",
        f"{'🎖 Уровень':<12} {str(lvl1 or '?'):<12} {lvl2 or '?'}",
        f"{'📚 Игр':<12} {len(g1):<12} {len(g2)}",
        f"{'⏱ Часов':<12} {total_h1:<12.0f} {total_h2:.0f}",
        f"{'🌍 Страна':<12} {(p1.get('loccountrycode') or '—'):<12} {p2.get('loccountrycode') or '—'}",
        f"{'🚫 VAC':<12} {vac1:<12} {vac2}",
    ]

    common = {g["appid"] for g in g1} & {g["appid"] for g in g2}
    lines.append(f"\n🤝 Общих игр: <b>{len(common)}</b>")

    return "\n".join(lines)


async def _do_common_games(session, sid1: str, sid2: str) -> str:
    g1, g2 = await asyncio.gather(
        get_owned_games(session, sid1),
        get_owned_games(session, sid2),
    )
    if not g1 or not g2:
        return "❌ Библиотека одного из игроков недоступна (профиль закрыт)."

    map1 = {g["appid"]: g for g in g1}
    map2 = {g["appid"]: g for g in g2}
    common_ids = set(map1) & set(map2)

    if not common_ids:
        return "🤝 <b>Общих игр нет.</b>"

    common = sorted(
        [map1[aid] for aid in common_ids],
        key=lambda g: g.get("playtime_forever", 0),
        reverse=True,
    )

    lines = [f"🤝 <b>Общие игры ({len(common)}):</b>\n"]
    for g in common[:25]:
        h = g.get("playtime_forever", 0) / 60
        lines.append(f"• {g.get('name', g['appid'])} — {h:.0f} ч")
    if len(common) > 25:
        lines.append(f"\n…и ещё {len(common) - 25} игр")
    return "\n".join(lines)


async def _do_common_friends(session, sid1: str, sid2: str) -> str:
    f1, f2 = await asyncio.gather(
        get_friends(session, sid1),
        get_friends(session, sid2),
    )
    if not f1 or not f2:
        return "❌ Список друзей одного из игроков недоступен (профиль закрыт)."

    ids1 = {f["steamid"] for f in f1}
    ids2 = {f["steamid"] for f in f2}
    common_ids = list(ids1 & ids2)

    if not common_ids:
        return "👥 <b>Общих друзей нет.</b>"

    players: list[dict] = []
    for i in range(0, len(common_ids), 100):
        batch = await get_player_summaries(session, common_ids[i:i + 100])
        players.extend(batch)

    lines = [f"👥 <b>Общие друзья ({len(common_ids)}):</b>\n"]
    for p in players[:25]:
        lines.append(f"• <a href='{p.get('profileurl', '')}'>{p.get('personaname', '?')}</a>")
    if len(common_ids) > 25:
        lines.append(f"\n…и ещё {len(common_ids) - 25}")
    return "\n".join(lines)
