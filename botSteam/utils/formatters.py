from datetime import datetime, timezone


def _fmt_ts(ts: int) -> str:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%-d %b %Y")


def _relative(ts: int) -> str:
    diff = int(datetime.now(tz=timezone.utc).timestamp()) - ts
    if diff < 60:
        return "только что"
    if diff < 3600:
        return f"{diff // 60} мин. назад"
    if diff < 86400:
        return f"{diff // 3600} ч. назад"
    if diff < 86400 * 30:
        return f"{diff // 86400} дн. назад"
    return _fmt_ts(ts)


def status_emoji(state: int) -> str:
    states = {0: "⚫", 1: "🟢", 2: "🟡", 3: "🔴", 4: "🔵", 5: "🟣", 6: "📵"}
    return states.get(state, "⚫")


def status_text(state: int) -> str:
    states = {
        0: "Не в сети",
        1: "В сети",
        2: "Занят",
        3: "Отошёл",
        4: "Сплю",
        5: "Хочу играть",
        6: "Хочу торговать",
    }
    return states.get(state, "Неизвестно")


def format_player(player: dict) -> str:
    name = player.get("personaname", "?")
    state = player.get("personastate", 0)
    game = player.get("gameextrainfo")
    profile_url = player.get("profileurl", "")

    line = f"{status_emoji(state)} <b>{name}</b> — {status_text(state)}"
    if game:
        line += f"\n   🎮 Играет в: <i>{game}</i>"
    if profile_url:
        line += f"\n   🔗 <a href='{profile_url}'>Профиль</a>"
    return line


def format_profile_extra(player: dict, level: int | None) -> str:
    parts = []

    if level is not None:
        parts.append(f"🎖 Уровень Steam: <b>{level}</b>")

    created = player.get("timecreated")
    if created:
        parts.append(f"📅 Аккаунт с: <b>{_fmt_ts(created)}</b>")


    if player.get("personastate", 0) == 0:
        lastlogoff = player.get("lastlogoff")
        if lastlogoff:
            parts.append(f"🕐 Был в сети: <b>{_relative(lastlogoff)}</b>")

    if not parts:
        return ""
    return "\n\n" + "\n".join(parts)


def format_bans(ban: dict) -> str:
    if not ban:
        return ""
    parts = []
    if ban.get("VACBanned"):
        n = ban.get("NumberOfVACBans", 1)
        days = ban.get("DaysSinceLastBan", 0)
        parts.append(f"🚫 VAC-бан: <b>{n} шт.</b> (последний {days} дн. назад)")
    if ban.get("NumberOfGameBans", 0) > 0:
        parts.append(f"🚫 Game-банов: <b>{ban['NumberOfGameBans']}</b>")
    if ban.get("CommunityBanned"):
        parts.append("🚫 Community-бан")
    if ban.get("EconomyBan", "none") != "none":
        parts.append(f"🚫 Trade-бан: {ban['EconomyBan']}")
    if not parts:
        return ""
    return "\n" + "\n".join(parts)
