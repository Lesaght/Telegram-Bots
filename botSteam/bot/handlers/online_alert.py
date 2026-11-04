from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from bot.keyboards.inline import OnlineAlertAction, back_to_menu, online_alerts_kb, player_actions
from services.steam import get_player_summaries, make_session
from services.storage import add_online_alert, get_online_alerts, has_online_alert, is_favorite, remove_online_alert

router = Router()


@router.callback_query(OnlineAlertAction.filter())
async def cb_online_alert(callback: CallbackQuery, callback_data: OnlineAlertAction):
    user_id = callback.from_user.id
    steamid = callback_data.steamid

    if await has_online_alert(user_id, steamid):
        await remove_online_alert(user_id, steamid)
        await callback.answer("🔕 Алерт «онлайн» отключён.")
    else:
        async with make_session() as session:
            players = await get_player_summaries(session, [steamid])
        name = players[0].get("personaname", steamid) if players else steamid
        await add_online_alert(user_id, steamid, name)
        await callback.answer("🔔 Уведомлю, когда игрок появится в сети!")

    fav = await is_favorite(user_id, steamid)
    alert = await has_online_alert(user_id, steamid)
    try:
        await callback.message.edit_reply_markup(reply_markup=player_actions(steamid, fav, alert))
    except Exception:
        pass
