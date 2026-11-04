import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import user_handlers, moderator_handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token)


async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(user_handlers.router)
    dp.include_router(moderator_handlers.router)

    logger.info("Starting bot...")

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
