import logging

from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

from .errors import BotError

logger = logging.getLogger(__name__)


async def error_handler(event: Message, handler):
    """
    Global error handler for bot.
    Catches all exceptions and sends user-friendly messages.
    """
    try:
        return await handler(event)
    except BotError as e:
        logger.warning(f"Bot error: {e.__class__.__name__}")
        await event.answer(e.user_message)
    except TelegramAPIError as e:
        logger.error(f"Telegram API error: {e}")
        await event.answer("Telegram error. Please try again.")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        await event.answer("Internal error. Please try again later.")
