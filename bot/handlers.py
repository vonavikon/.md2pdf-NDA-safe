import asyncio
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, Document

from config import MAX_FILE_SIZE_MB, CONVERSION_TIMEOUT
from converter import secure_temp_dir, convert_md_to_pdf, ConversionError as ConverterConversionError
from .errors import (
    BotError,
    InvalidFileFormat,
    FileTooLarge,
    ConversionError,
    ConversionTimeout,
)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 **Welcome to Markdown to PDF Bot!**\n\n"
        "Send me a `.md` file and I'll convert it to PDF.\n\n"
        "✅ Supports: LaTeX formulas, Mermaid diagrams, images, code highlighting\n"
        "🔒 Your files are not stored on server (NDA Safe)\n\n"
        "Use /help for more info.",
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "**Supported Features:**\n\n"
        "• Headers, lists, tables\n"
        "• LaTeX formulas: `$E=mc^2$` or `$$...$$`\n"
        "• Mermaid diagrams\n"
        "• Images (links and base64)\n"
        "• Code with syntax highlighting\n"
        "• Cyrillic text\n\n"
        "**Limits:**\n"
        f"• Max file size: {MAX_FILE_SIZE_MB} MB\n"
        "• Max conversion time: 60 seconds\n\n"
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

    # Validate file extension
    if not document.file_name or not document.file_name.lower().endswith(".md"):
        raise InvalidFileFormat()

    # Validate file size
    if document.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise FileTooLarge()

    status_msg = await message.answer("⏳ Converting...")

    try:
        with secure_temp_dir() as temp_dir:
            # Download file
            input_path = temp_dir / document.file_name
            await bot.download(document, destination=input_path)

            # Prepare output path
            output_path = temp_dir / input_path.with_suffix(".pdf").name

            # Convert with timeout
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(convert_md_to_pdf, input_path, output_path),
                    timeout=CONVERSION_TIMEOUT
                )
            except asyncio.TimeoutError:
                raise ConversionTimeout()
            except ConverterConversionError as e:
                raise ConversionError() from e

            # Send PDF
            await message.answer_document(
                document=output_path,
                caption="✅ Your PDF is ready!\n🔒 File was not stored on server."
            )

    finally:
        await status_msg.delete()
