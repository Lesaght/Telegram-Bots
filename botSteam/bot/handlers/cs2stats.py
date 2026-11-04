from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from bot.keyboards.inline import SteamAction, back_to_profile
from services.steam import get_user_cs2_stats, make_session

router = Router()


@router.callback_query(SteamAction.filter(F.action == "cs2stats"))
async def cb_cs2stats(callback: CallbackQuery, callback_data: SteamAction):
    steamid = callback_data.steamid
    if callback.message.photo:
        wait_msg = await callback.message.answer("⏳ Загружаю статистику CS2...")
    else:
        wait_msg = await callback.message.edit_text("⏳ Загружаю статистику CS2...")

    async with make_session() as session:
        stats = await get_user_cs2_stats(session, steamid)

    if not stats:
        await wait_msg.edit_text(
            "❌ Статистика CS2 недоступна (профиль закрыт или CS2 не установлен).",
            reply_markup=back_to_profile(steamid),
        )
        await callback.answer()
        return

    kills = stats.get("total_kills", 0)
    deaths = stats.get("total_deaths", 0)
    wins = stats.get("total_wins", 0)
    matches = stats.get("total_matches_played", 0)
    rounds = stats.get("total_rounds_played", 0)
    mvps = stats.get("total_mvps", 0)
    hs = stats.get("total_kills_headshot", 0)
    shots_fired = stats.get("total_shots_fired", 0)
    shots_hit = stats.get("total_shots_hit", 0)
    time_played = stats.get("total_time_played", 0)

    kd = kills / deaths if deaths else 0
    wr = wins / matches * 100 if matches else 0
    hs_pct = hs / kills * 100 if kills else 0
    acc = shots_hit / shots_fired * 100 if shots_fired else 0
    hours = time_played / 3600

    lines = [
        "📊 <b>Статистика CS2</b>\n",
        f"🎯 Убийств: <b>{kills:,}</b>  |  Смертей: <b>{deaths:,}</b>",
        f"⚖️ K/D: <b>{kd:.2f}</b>",
        f"🏆 Побед: <b>{wins:,}</b> из <b>{matches:,}</b> матчей ({wr:.1f}%)",
        f"🔵 Раундов сыграно: <b>{rounds:,}</b>",
        f"🎖 MVP: <b>{mvps:,}</b>",
        f"💀 Хедшоты: <b>{hs:,}</b> ({hs_pct:.1f}%)",
        f"🎯 Точность: <b>{acc:.1f}%</b>",
        f"⏱ Часов в игре: <b>{hours:,.0f}</b>",
    ]

    await wait_msg.edit_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_profile(steamid),
    )
    await callback.answer()
