from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, Document, FSInputFile

from config import MAX_FILE_SIZE_MB, CONVERSION_TIMEOUT
from converter import secure_temp_dir
from .errors import InvalidFileFormat
from .file_pipeline import (
    validate_markdown_document,
    build_conversion_paths,
    convert_document_to_pdf,
)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 **Welcome to Markdown to PDF Bot!**\n\n"
        "Send me a `.md` file and I'll convert it to PDF.\n\n"
        "✅ Supports: tables, code highlighting, lists, images\n"
        "🎨 Styled with NAUMEN branding\n"
        "🔒 Your files are not stored on server (NDA Safe)\n\n"
        "Use /help for more info.",
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "**Supported Features:**\n\n"
        "• Headers (H1-H6), bold, italic\n"
        "• Ordered and unordered lists\n"
        "• Tables with styling\n"
        "• Code blocks with syntax highlighting\n"
        "• Blockquotes\n"
        "• Links and images\n"
        "• Cyrillic text\n\n"
        "**Limits:**\n"
        f"• Max file size: {MAX_FILE_SIZE_MB} MB\n"
        f"• Max conversion time: {CONVERSION_TIMEOUT} seconds\n\n"
        "Use /privacy for security info.",
        parse_mode="Markdown"
    )


@router.message(Command("privacy"))
async def cmd_privacy(message: Message):
    await message.answer(
        "🔒 **NDA Safe - Your Privacy Guaranteed**\n\n"
        "• Files are processed in temporary memory\n"
        "• All files are deleted immediately after conversion\n"
        "• No data is stored on the server\n"
        "• Even if the bot crashes, files are cleaned up\n\n"
        "Your documents never leave a trace.",
        parse_mode="Markdown"
    )


@router.message(F.document)
async def handle_document(message: Message, bot: Bot):
    document: Document = message.document
    if document is None:
        raise InvalidFileFormat()

    safe_file_name = validate_markdown_document(document, MAX_FILE_SIZE_MB)

    status_msg = await message.answer("⏳ Converting...")

    try:
        with secure_temp_dir() as temp_dir:
            input_path, output_path = build_conversion_paths(temp_dir, safe_file_name)
            await bot.download(document, destination=input_path)


            await convert_document_to_pdf(
                input_path,
                output_path,
                CONVERSION_TIMEOUT,
            )

            # Send PDF
            await message.answer_document(
                document=FSInputFile(output_path, filename=output_path.name),
                caption="✅ Your PDF is ready!\n🔒 File was not stored on server."
            )

    finally:
        with suppress(Exception):
            await status_msg.delete()
