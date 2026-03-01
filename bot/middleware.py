import logging

from aiogram.types import ErrorEvent

from .errors import BotError

logger = logging.getLogger(__name__)


async def error_handler(event: ErrorEvent):
    """
    Global error handler for bot.
    Catches all exceptions and sends user-friendly messages.
    """
    message = event.update.message

    if isinstance(event.exception, BotError):
        logger.exception(f"Bot error: {event.exception.__class__.__name__}: {event.exception}")
        if message:
            await message.answer(event.exception.user_message)
    else:
        logger.exception(f"Unexpected error: {event.exception}")
        if message:
            await message.answer("Internal error. Please try again later.")
