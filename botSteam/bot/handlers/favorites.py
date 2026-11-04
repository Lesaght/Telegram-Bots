from aiogram import Router
from aiogram.types import CallbackQuery

from bot.keyboards.inline import FavoriteAction, player_actions
from services.steam import get_player_summaries, make_session
from services.storage import add_favorite, is_favorite, remove_favorite

router = Router()


@router.callback_query(FavoriteAction.filter())
async def cb_favorite(callback: CallbackQuery, callback_data: FavoriteAction):
    user_id = callback.from_user.id
    steamid = callback_data.steamid

    if callback_data.action == "add":
        async with make_session() as session:
            players = await get_player_summaries(session, [steamid])
        name = players[0].get("personaname", steamid) if players else steamid
        result = await add_favorite(user_id, steamid, name)
        if result == "added":
            await callback.answer("⭐ Добавлено в избранное!")
        elif result == "exists":
            await callback.answer("Уже есть в избранном.")
        else:
            await callback.answer(f"Достигнут лимит избранного (10 профилей).")

    elif callback_data.action == "remove":
        removed = await remove_favorite(user_id, steamid)
        await callback.answer("🗑 Убрано из избранного." if removed else "Не найдено в избранном.")

    fav = await is_favorite(user_id, steamid)
    try:
        await callback.message.edit_reply_markup(reply_markup=player_actions(steamid, fav))
    except Exception:
        pass
