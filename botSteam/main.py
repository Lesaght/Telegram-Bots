import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import (
    compare,
    cs2stats,
    favorites,
    friends,
    games,
    inventory,
    leaderboard,
    online_alert,
    price_tracker,
    profile,
    recent,
    start,
)
from config import TELEGRAM_TOKEN
from services.notifier import start_notifier

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start.router,
        profile.router,
        friends.router,
        recent.router,
        favorites.router,
        games.router,
        inventory.router,
        cs2stats.router,
        compare.router,
        leaderboard.router,
        price_tracker.router,
        online_alert.router,
    )

    asyncio.create_task(start_notifier(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
