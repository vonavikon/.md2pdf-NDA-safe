import logging
from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, Document, FSInputFile, ReplyParameters

from config import MAX_FILE_SIZE_MB, CONVERSION_TIMEOUT
from converter import secure_temp_dir
from .file_pipeline import (
    validate_markdown_document,
    build_conversion_paths,
    convert_document_to_pdf,
)
from .errors import InvalidFileFormat, FileTooLarge

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 **Добро пожаловать в Markdown to PDF Bot!**\n\n"
        "Отправьте мне файл `.md` и я конвертирую его в PDF.\n\n"
        "✅ Поддержка: таблицы, подсветка кода, списки, изображения\n"
        "🎨 Оформление в стиле NAUMEN\n"
        "🔒 Файлы не сохраняются на сервере (NDA Safe)\n\n"
        "Используйте /help для дополнительной информации.",
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "**Поддерживаемые возможности:**\n\n"
        "• Заголовки (H1-H6), жирный, курсив\n"
        "• Нумерованные и маркированные списки\n"
        "• Таблицы со стилизацией\n"
        "• Блоки кода с подсветкой синтаксиса\n"
        "• Цитаты\n"
        "• Ссылки и изображения\n"
        "• Кириллица\n\n"
        "**Использование:**\n"
        "• В личке: просто отправьте .md файл\n"
        "• В группах: ответьте на .md файл командой /convert\n\n"
        "**Ограничения:**\n"
        f"• Макс. размер файла: {MAX_FILE_SIZE_MB} МБ\n"
        f"• Макс. время конвертации: {CONVERSION_TIMEOUT} сек\n\n"
        "Используйте /privacy для информации о безопасности.",
        parse_mode="Markdown"
    )


@router.message(Command("privacy"))
async def cmd_privacy(message: Message):
    await message.answer(
        "🔒 **NDA Safe - Гарантия конфиденциальности**\n\n"
        "• Файлы обрабатываются во временной памяти\n"
        "• Все файлы удаляются сразу после конвертации\n"
        "• Данные не сохраняются на сервере\n"
        "• Даже при сбое бота файлы будут очищены\n\n"
        "Ваши документы не оставляют следов.",
        parse_mode="Markdown"
    )


@router.message(F.document, F.chat.type == "private")
async def handle_document(message: Message, bot: Bot):
    document: Document = message.document

    safe_file_name = validate_markdown_document(document, MAX_FILE_SIZE_MB)
    logger.info(f"Processing: {safe_file_name} ({document.file_size or '?'} bytes)")

    status_msg = await message.answer("⏳ Конвертация...")

    try:
        with secure_temp_dir() as temp_dir:
            input_path, output_path = build_conversion_paths(temp_dir, safe_file_name)
            await bot.download(document, destination=input_path)

            await convert_document_to_pdf(
                input_path,
                output_path,
                CONVERSION_TIMEOUT,
            )

            logger.info(f"Converted successfully: {safe_file_name}")

            await message.answer_document(
                document=FSInputFile(output_path, filename=output_path.name),
                caption="✅ PDF готов!\n🔒 Файл не сохранён на сервере."
            )

    finally:
        with suppress(Exception):
            await status_msg.delete()


@router.message(Command("convert"))
async def cmd_convert(message: Message, bot: Bot):
    """Handle /convert command in groups - converts .md file from replied message."""
    logger.info(f"Convert command received from chat {message.chat.id}")

    # Check if this is a reply
    if not message.reply_to_message:
        await message.answer("ℹ️ Ответьте этой командой на .md файл")
        return

    replied = message.reply_to_message

    # Check if replied message has a document
    if not replied.document:
        await message.answer(
            "❌ Это не .md файл",
            reply_parameters=ReplyParameters(message_id=message.message_id)
        )
        return

    document = replied.document

    # Validate document
    try:
        safe_file_name = validate_markdown_document(document, MAX_FILE_SIZE_MB)
    except (InvalidFileFormat, FileTooLarge):
        await message.answer(
            "❌ Ошибка конвертации",
            reply_parameters=ReplyParameters(message_id=message.message_id)
        )
        return

    logger.info(f"Group convert: {safe_file_name} by user {message.from_user.id}")

    try:
        with secure_temp_dir() as temp_dir:
            input_path, output_path = build_conversion_paths(temp_dir, safe_file_name)
            await bot.download(document, destination=input_path)

            await convert_document_to_pdf(
                input_path,
                output_path,
                CONVERSION_TIMEOUT,
            )

            logger.info(f"Group convert success: {safe_file_name}")

            await message.answer_document(
                document=FSInputFile(output_path, filename=output_path.name),
                caption="✅ PDF готов!",
                reply_parameters=ReplyParameters(message_id=message.message_id)
            )

    except Exception:
        await message.answer(
            "❌ Ошибка конвертации",
            reply_parameters=ReplyParameters(message_id=message.message_id)
        )


@router.message(F.text.regexp(r"@md2pdf_nova_bot"))
async def handle_mention(message: Message, bot: Bot):
    """Handle bot mention in groups - converts .md file from replied message."""
    # Check if this is a reply to a document
    if not message.reply_to_message or not message.reply_to_message.document:
        return  # Ignore if not a reply to a document

    replied = message.reply_to_message
    document = replied.document

    # Validate document
    try:
        safe_file_name = validate_markdown_document(document, MAX_FILE_SIZE_MB)
    except (InvalidFileFormat, FileTooLarge):
        await message.answer(
            "❌ Это не .md файл",
            reply_parameters=ReplyParameters(message_id=message.message_id)
        )
        return

    logger.info(f"Mention convert: {safe_file_name} by user {message.from_user.id}")

    try:
        with secure_temp_dir() as temp_dir:
            input_path, output_path = build_conversion_paths(temp_dir, safe_file_name)
            await bot.download(document, destination=input_path)

            await convert_document_to_pdf(
                input_path,
                output_path,
                CONVERSION_TIMEOUT,
            )

            logger.info(f"Mention convert success: {safe_file_name}")

            await message.answer_document(
                document=FSInputFile(output_path, filename=output_path.name),
                caption="✅ PDF готов!",
                reply_parameters=ReplyParameters(message_id=message.message_id)
            )

    except Exception:
        await message.answer(
            "❌ Ошибка конвертации",
            reply_parameters=ReplyParameters(message_id=message.message_id)
        )
