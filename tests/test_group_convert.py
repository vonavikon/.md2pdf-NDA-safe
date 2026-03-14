import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, Document, User, Chat


@pytest.fixture
def mock_bot():
    return AsyncMock()


@pytest.fixture
def mock_message():
    message = MagicMock(spec=Message)
    message.message_id = 100
    message.chat = MagicMock(spec=Chat)
    message.chat.id = -1001234567890  # Group chat ID
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 123456789
    message.reply_to_message = MagicMock(spec=Message)
    message.reply_to_message.document = MagicMock(spec=Document)
    message.reply_to_message.document.file_name = "test.md"
    message.reply_to_message.document.file_size = 1000
    message.reply_to_message.document.file_id = "test_file_id"
    message.answer = AsyncMock()
    message.answer_document = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_cmd_convert_valid_md_file(mock_message, mock_bot):
    """Test /convert command with valid .md file reply."""
    with patch("bot.handlers.secure_temp_dir") as mock_temp_dir, \
         patch("bot.handlers.validate_markdown_document") as mock_validate, \
         patch("bot.handlers.build_conversion_paths") as mock_paths, \
         patch("bot.handlers.convert_document_to_pdf") as mock_convert:

        mock_validate.return_value = "test.md"
        mock_temp_dir.return_value.__enter__ = MagicMock()
        mock_temp_dir.return_value.__exit__ = MagicMock(return_value=False)

        from pathlib import Path
        mock_input = MagicMock(spec=Path)
        mock_output = MagicMock(spec=Path)
        mock_output.name = "test.pdf"
        mock_paths.return_value = (mock_input, mock_output)

        await cmd_convert(mock_message, mock_bot)

        mock_validate.assert_called_once()
        mock_convert.assert_called_once()
        mock_message.answer_document.assert_called_once()