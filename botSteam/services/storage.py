import json
import os

import aiofiles

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_FAVORITES_FILE = os.path.join(_DATA_DIR, "favorites.json")
_ONLINE_ALERTS_FILE = os.path.join(_DATA_DIR, "online_alerts.json")
_PRICE_ALERTS_FILE = os.path.join(_DATA_DIR, "price_alerts.json")
_MAX_FAVORITES = 10
_MAX_PRICE_ALERTS = 20


async def _load_file(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    async with aiofiles.open(path, encoding="utf-8") as f:
        return json.loads(await f.read())


async def _save_file(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))


async def get_all_favorites_data() -> dict[str, list[dict]]:
    return await _load_file(_FAVORITES_FILE)


async def get_favorites(user_id: int) -> list[dict]:
    data = await _load_file(_FAVORITES_FILE)
    return data.get(str(user_id), [])


async def is_favorite(user_id: int, steamid: str) -> bool:
    data = await _load_file(_FAVORITES_FILE)
    return any(f["steamid"] == steamid for f in data.get(str(user_id), []))


async def add_favorite(user_id: int, steamid: str, name: str) -> str:
    data = await _load_file(_FAVORITES_FILE)
    key = str(user_id)
    favs = data.get(key, [])
    if any(f["steamid"] == steamid for f in favs):
        return "exists"
    if len(favs) >= _MAX_FAVORITES:
        return "limit"
    favs.append({"steamid": steamid, "name": name})
    data[key] = favs
    await _save_file(_FAVORITES_FILE, data)
    return "added"


async def remove_favorite(user_id: int, steamid: str) -> bool:
    data = await _load_file(_FAVORITES_FILE)
    key = str(user_id)
    favs = data.get(key, [])
    new_favs = [f for f in favs if f["steamid"] != steamid]
    if len(new_favs) == len(favs):
        return False
    data[key] = new_favs
    await _save_file(_FAVORITES_FILE, data)
    return True


async def get_all_online_alerts() -> dict[str, list[dict]]:
    return await _load_file(_ONLINE_ALERTS_FILE)


async def get_online_alerts(user_id: int) -> list[dict]:
    data = await _load_file(_ONLINE_ALERTS_FILE)
    return data.get(str(user_id), [])


async def has_online_alert(user_id: int, steamid: str) -> bool:
    data = await _load_file(_ONLINE_ALERTS_FILE)
    return any(a["steamid"] == steamid for a in data.get(str(user_id), []))


async def add_online_alert(user_id: int, steamid: str, name: str) -> bool:
    data = await _load_file(_ONLINE_ALERTS_FILE)
    key = str(user_id)
    alerts = data.get(key, [])
    if any(a["steamid"] == steamid for a in alerts):
        return False
    alerts.append({"steamid": steamid, "name": name})
    data[key] = alerts
    await _save_file(_ONLINE_ALERTS_FILE, data)
    return True


async def remove_online_alert(user_id: int, steamid: str) -> bool:
    data = await _load_file(_ONLINE_ALERTS_FILE)
    key = str(user_id)
    alerts = data.get(key, [])
    new_alerts = [a for a in alerts if a["steamid"] != steamid]
    if len(new_alerts) == len(alerts):
        return False
    data[key] = new_alerts
    await _save_file(_ONLINE_ALERTS_FILE, data)
    return True


async def get_all_price_alerts() -> dict[str, list[dict]]:
    return await _load_file(_PRICE_ALERTS_FILE)


async def get_price_alerts(user_id: int) -> list[dict]:
    data = await _load_file(_PRICE_ALERTS_FILE)
    return data.get(str(user_id), [])


async def add_price_alert(
    user_id: int, market_hash_name: str, appid: int, game_name: str, target_price: float
) -> str:
    data = await _load_file(_PRICE_ALERTS_FILE)
    key = str(user_id)
    alerts = data.get(key, [])
    if len(alerts) >= _MAX_PRICE_ALERTS:
        return "limit"
    next_id = max((a["id"] for a in alerts), default=0) + 1
    alerts.append({
        "id": next_id,
        "market_hash_name": market_hash_name,
        "appid": appid,
        "game_name": game_name,
        "target_price": target_price,
    })
    data[key] = alerts
    await _save_file(_PRICE_ALERTS_FILE, data)
    return "added"


async def remove_price_alert(user_id: int, alert_id: int) -> bool:
    data = await _load_file(_PRICE_ALERTS_FILE)
    key = str(user_id)
    alerts = data.get(key, [])
    new_alerts = [a for a in alerts if a["id"] != alert_id]
    if len(new_alerts) == len(alerts):
        return False
    data[key] = new_alerts
    await _save_file(_PRICE_ALERTS_FILE, data)
    return True


async def remove_price_alert_global(user_id: int, alert_id: int) -> None:
    """Used by notifier after firing an alert."""
    await remove_price_alert(user_id, alert_id)
