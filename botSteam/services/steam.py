import ssl

import aiohttp
import certifi
from config import STEAM_API, STEAM_API_KEY


def make_session() -> aiohttp.ClientSession:
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_ctx)
    return aiohttp.ClientSession(connector=connector)


def parse_steam_id(text: str) -> str:
    text = text.strip()
    if "steamcommunity.com" in text:
        parts = text.rstrip("/").split("/")
        if "profiles" in parts:
            idx = parts.index("profiles")
            return parts[idx + 1] if idx + 1 < len(parts) else text
        if "id" in parts:
            idx = parts.index("id")
            return parts[idx + 1] if idx + 1 < len(parts) else text
    return text


async def resolve_vanity(session: aiohttp.ClientSession, vanity: str) -> str | None:
    if vanity.isdigit() and len(vanity) == 17:
        return vanity
    url = f"{STEAM_API}/ISteamUser/ResolveVanityURL/v1/"
    async with session.get(url, params={"key": STEAM_API_KEY, "vanityurl": vanity}) as r:
        data = await r.json()
    response = data.get("response", {})
    if response.get("success") == 1:
        return response["steamid"]
    return None


async def get_player_summaries(session: aiohttp.ClientSession, steamids: list[str]) -> list[dict]:
    url = f"{STEAM_API}/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": STEAM_API_KEY, "steamids": ",".join(steamids)}
    async with session.get(url, params=params) as r:
        data = await r.json()
    return data.get("response", {}).get("players", [])


async def get_friends(session: aiohttp.ClientSession, steamid: str) -> list[dict]:
    url = f"{STEAM_API}/ISteamUser/GetFriendList/v1/"
    params = {"key": STEAM_API_KEY, "steamid": steamid, "relationship": "friend"}
    async with session.get(url, params=params) as r:
        if r.status != 200:
            return []
        data = await r.json()
    return data.get("friendslist", {}).get("friends", [])


async def get_recently_played(session: aiohttp.ClientSession, steamid: str) -> list[dict]:
    url = f"{STEAM_API}/IPlayerService/GetRecentlyPlayedGames/v1/"
    params = {"key": STEAM_API_KEY, "steamid": steamid, "count": 5}
    async with session.get(url, params=params) as r:
        if r.status != 200:
            return []
        data = await r.json()
    return data.get("response", {}).get("games", [])


async def get_player_bans(session: aiohttp.ClientSession, steamids: list[str]) -> list[dict]:
    url = f"{STEAM_API}/ISteamUser/GetPlayerBans/v1/"
    async with session.get(url, params={"key": STEAM_API_KEY, "steamids": ",".join(steamids)}) as r:
        if r.status != 200:
            return []
        data = await r.json()
    return data.get("players", [])


async def get_user_cs2_stats(session: aiohttp.ClientSession, steamid: str) -> dict[str, int]:
    url = f"{STEAM_API}/ISteamUserStats/GetUserStatsForGame/v2/"
    params = {"key": STEAM_API_KEY, "steamid": steamid, "appid": 730}
    async with session.get(url, params=params) as r:
        if r.status != 200:
            return {}
        data = await r.json()
    stats = data.get("playerstats", {}).get("stats", [])
    return {s["name"]: s["value"] for s in stats}


async def get_steam_level(session: aiohttp.ClientSession, steamid: str) -> int | None:
    url = f"{STEAM_API}/IPlayerService/GetSteamLevel/v1/"
    async with session.get(url, params={"key": STEAM_API_KEY, "steamid": steamid}) as r:
        if r.status != 200:
            return None
        data = await r.json()
    return data.get("response", {}).get("player_level")


async def get_owned_games(session: aiohttp.ClientSession, steamid: str) -> list[dict]:
    url = f"{STEAM_API}/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steamid,
        "include_appinfo": 1,
        "include_played_free_games": 1,
    }
    async with session.get(url, params=params) as r:
        if r.status != 200:
            return []
        data = await r.json()
    return data.get("response", {}).get("games", [])


async def get_inventory(
    session: aiohttp.ClientSession, steamid: str, appid: int, contextid: int = 2
) -> tuple[list[dict], int]:
    """Returns (items, total_count).
    Each item: {name, market_hash_name, count, marketable}
    """
    url = f"https://steamcommunity.com/inventory/{steamid}/{appid}/{contextid}"
    async with session.get(url, params={"l": "english", "count": 5000}) as r:
        if r.status != 200:
            return [], 0
        data = await r.json()

    if not data or not data.get("success"):
        return [], 0

    total = data.get("total_inventory_count", 0)

    desc_map: dict[tuple, dict] = {}
    for desc in data.get("descriptions", []):
        key = (desc.get("classid"), desc.get("instanceid", "0"))
        desc_map[key] = desc

    item_counts: dict[str, dict] = {}
    for asset in data.get("assets", []):
        key = (asset.get("classid"), asset.get("instanceid", "0"))
        desc = desc_map.get(key, {})
        mhn = desc.get("market_hash_name")
        if not mhn:
            continue
        if mhn not in item_counts:
            item_counts[mhn] = {
                "name": desc.get("name", mhn),
                "market_hash_name": mhn,
                "count": 0,
                "marketable": desc.get("marketable", 0) == 1,
                "type": desc.get("type", ""),
            }
        item_counts[mhn]["count"] += int(asset.get("amount", 1))

    return list(item_counts.values()), total


async def get_item_price(
    session: aiohttp.ClientSession, appid: int, market_hash_name: str
) -> float | None:
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {"appid": appid, "currency": 1, "market_hash_name": market_hash_name}
    try:
        async with session.get(url, params=params) as r:
            if r.status != 200:
                return None
            data = await r.json()
    except Exception:
        return None

    if not data.get("success"):
        return None

    price_str = data.get("median_price") or data.get("lowest_price")
    if not price_str:
        return None
    try:
        return float(price_str.replace("$", "").replace(",", "").strip())
    except ValueError:
        return None
