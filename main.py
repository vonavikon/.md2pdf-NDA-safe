import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, LOG_LEVEL
from bot.handlers import router
from bot.middleware import error_handler

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register error handler
    dp.errors.register(error_handler)

    # Register handlers
    dp.include_router(router)

    logger.info("Bot started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
