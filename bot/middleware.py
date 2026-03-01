import logging

from aiogram.types import ErrorEvent

from .errors import BotError, InvalidFileFormat, FileTooLarge, ConversionError, ConversionTimeout

logger = logging.getLogger(__name__)


async def error_handler(event: ErrorEvent):
    """
    Global error handler for bot.
    Catches all exceptions and sends user-friendly messages.
    """
    message = event.update.message
    exception = event.exception

    if isinstance(exception, BotError):
        logger.warning(f"Bot error: {exception.__class__.__name__}: {exception}")
        if message:
            await message.answer(exception.user_message)
    else:
        logger.exception(f"Unexpected error: {exception}")
        if message:
            await message.answer("Внутренняя ошибка. Попробуйте позже.")
