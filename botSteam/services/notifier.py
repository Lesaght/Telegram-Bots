import asyncio
import json
import logging
import os

import aiofiles
from aiogram import Bot

from services.steam import get_item_price, get_player_summaries, make_session
from services.storage import (
    get_all_favorites_data,
    get_all_online_alerts,
    get_all_price_alerts,
    remove_price_alert_global,
)

logger = logging.getLogger(__name__)

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_LAST_SEEN_FILE = os.path.join(_DATA_DIR, "last_seen.json")
_LAST_ONLINE_FILE = os.path.join(_DATA_DIR, "last_online.json")
_POLL_INTERVAL = 300


async def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    async with aiofiles.open(path, encoding="utf-8") as f:
        return json.loads(await f.read())


async def _save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))


async def _check_game_notifications(bot: Bot) -> None:
    favorites_data = await get_all_favorites_data()
    if not favorites_data:
        return

    steamid_to_users: dict[str, set[int]] = {}
    steamid_to_name: dict[str, str] = {}
    for uid_str, favs in favorites_data.items():
        for fav in favs:
            sid = fav["steamid"]
            steamid_to_users.setdefault(sid, set()).add(int(uid_str))
            steamid_to_name[sid] = fav["name"]

    if not steamid_to_users:
        return

    all_steamids = list(steamid_to_users.keys())
    last_seen = await _load_json(_LAST_SEEN_FILE)
    new_last_seen = dict(last_seen)

    players: list[dict] = []
    async with make_session() as session:
        for i in range(0, len(all_steamids), 100):
            batch = await get_player_summaries(session, all_steamids[i:i + 100])
            players.extend(batch)

    for player in players:
        steamid = player.get("steamid")
        if not steamid:
            continue
        game: str | None = player.get("gameextrainfo")
        first_seen = steamid not in last_seen
        prev_game: str | None = last_seen.get(steamid)

        if not first_seen and game and game != prev_game:
            name = player.get("personaname") or steamid_to_name.get(steamid, steamid)
            text = (
                f"🎮 <b>{name}</b> переключился на <b>{game}</b>"
                if prev_game else
                f"🎮 <b>{name}</b> начал играть в <b>{game}</b>"
            )
            for user_id in steamid_to_users.get(steamid, set()):
                try:
                    await bot.send_message(user_id, text, parse_mode="HTML")
                except Exception as e:
                    logger.warning("Game notify failed for user %s: %s", user_id, e)

        new_last_seen[steamid] = game

    await _save_json(_LAST_SEEN_FILE, new_last_seen)


async def _check_online_alerts(bot: Bot) -> None:
    alerts_data = await get_all_online_alerts()
    if not alerts_data:
        return

    steamid_to_users: dict[str, set[int]] = {}
    steamid_to_name: dict[str, str] = {}
    for uid_str, alerts in alerts_data.items():
        for a in alerts:
            sid = a["steamid"]
            steamid_to_users.setdefault(sid, set()).add(int(uid_str))
            steamid_to_name[sid] = a["name"]

    if not steamid_to_users:
        return

    all_steamids = list(steamid_to_users.keys())
    last_online = await _load_json(_LAST_ONLINE_FILE)
    new_last_online = dict(last_online)

    players: list[dict] = []
    async with make_session() as session:
        for i in range(0, len(all_steamids), 100):
            batch = await get_player_summaries(session, all_steamids[i:i + 100])
            players.extend(batch)

    for player in players:
        steamid = player.get("steamid")
        if not steamid:
            continue
        state = player.get("personastate", 0)
        prev_state = last_online.get(steamid)

        if prev_state is not None and prev_state == 0 and state > 0:
            name = player.get("personaname") or steamid_to_name.get(steamid, steamid)
            text = f"🟢 <b>{name}</b> появился в сети!"
            for user_id in steamid_to_users.get(steamid, set()):
                try:
                    await bot.send_message(user_id, text, parse_mode="HTML")
                except Exception as e:
                    logger.warning("Online notify failed for user %s: %s", user_id, e)

        new_last_online[steamid] = state

    await _save_json(_LAST_ONLINE_FILE, new_last_online)


async def _check_price_alerts(bot: Bot) -> None:
    alerts_data = await get_all_price_alerts()
    if not alerts_data:
        return

    async with make_session() as session:
        for uid_str, alerts in list(alerts_data.items()):
            user_id = int(uid_str)
            for alert in list(alerts):
                try:
                    price = await get_item_price(session, alert["appid"], alert["market_hash_name"])
                    await asyncio.sleep(0.5)
                except Exception:
                    continue

                if price is None:
                    continue

                if price <= alert["target_price"]:
                    text = (
                        f"📈 <b>Цена упала!</b>\n\n"
                        f"<b>{alert['market_hash_name']}</b> ({alert['game_name']})\n"
                        f"Текущая цена: <b>${price:.2f}</b>\n"
                        f"Ваш порог: <b>${alert['target_price']:.2f}</b>"
                    )
                    try:
                        await bot.send_message(user_id, text, parse_mode="HTML")
                        await remove_price_alert_global(user_id, alert["id"])
                    except Exception as e:
                        logger.warning("Price notify failed for user %s: %s", user_id, e)


async def check_and_notify(bot: Bot) -> None:
    await asyncio.gather(
        _check_game_notifications(bot),
        _check_online_alerts(bot),
        _check_price_alerts(bot),
        return_exceptions=True,
    )


async def start_notifier(bot: Bot) -> None:
    logger.info("Notifier started, polling every %ds", _POLL_INTERVAL)
    while True:
        await asyncio.sleep(_POLL_INTERVAL)
        try:
            await check_and_notify(bot)
        except Exception:
            logger.exception("Error in notifier check")
