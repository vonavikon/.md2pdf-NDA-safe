import asyncio
from pathlib import Path

from aiogram.types import Document

from converter import convert_md_to_pdf, ConversionError as ConverterConversionError

from .errors import InvalidFileFormat, FileTooLarge, ConversionError, ConversionTimeout


def validate_markdown_document(document: Document, max_file_size_mb: int) -> str:
    """
    Validate uploaded Telegram document and return a safe markdown filename.

    Raises:
        InvalidFileFormat: when file is missing or has non-.md extension.
        FileTooLarge: when uploaded file exceeds allowed max size.
    """
    safe_file_name = Path(document.file_name or "").name
    if not safe_file_name or not safe_file_name.lower().endswith(".md"):
        raise InvalidFileFormat()

    if document.file_size is not None:
        max_size_bytes = max_file_size_mb * 1024 * 1024
        if document.file_size > max_size_bytes:
            raise FileTooLarge(max_file_size_mb)

    return safe_file_name


def build_conversion_paths(temp_dir: Path, safe_file_name: str) -> tuple[Path, Path]:
    """
    Build and validate input/output paths inside a temporary directory.

    Raises:
        InvalidFileFormat: when input path escapes the temp directory.
    """
    input_path = temp_dir / safe_file_name
    if input_path.resolve().parent != temp_dir.resolve():
        raise InvalidFileFormat()

    output_path = temp_dir / input_path.with_suffix(".pdf").name
    return input_path, output_path


async def convert_document_to_pdf(
    input_path: Path,
    output_path: Path,
    timeout_seconds: int,
) -> None:
    """
    Convert markdown file to PDF and map converter failures to bot domain errors.
    """
    try:
        await asyncio.wait_for(
            asyncio.to_thread(
                convert_md_to_pdf,
                input_path,
                output_path,
            ),
            timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        raise ConversionTimeout(timeout_seconds)
    except ConverterConversionError as error:
        raise ConversionError(str(error)) from error
