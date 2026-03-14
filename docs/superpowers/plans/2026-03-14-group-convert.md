# Group Chat Convert Command Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `/convert` command for converting .md files to PDF in group chats via reply.

**Architecture:** New handler in `bot/handlers.py` that checks for reply with .md document, reuses existing conversion pipeline, sends PDF as reply. Minimal changes, maximum code reuse.

**Tech Stack:** aiogram 3.x, existing converter module

---

## Chunk 1: Test Infrastructure & Handler

### Task 1: Add test for /convert command

**Files:**
- Create: `tests/test_group_convert.py`

- [ ] **Step 1: Write the failing test for /convert with valid .md reply**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, Document, User, Chat

from bot.handlers import cmd_convert


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "C:\Users\const\OneDrive\Рабочий стол\Repos\mdToPdf" && python -m pytest tests/test_group_convert.py -v`
Expected: FAIL - handler not implemented yet

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_group_convert.py
git commit -m "test: add failing test for group /convert command"
```

---

### Task 2: Implement /convert handler

**Files:**
- Modify: `bot/handlers.py`

- [ ] **Step 1: Add imports at top of handlers.py**

Add `ReplyParameters` to aiogram imports:

```python
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, Document, FSInputFile, ReplyParameters
```

- [ ] **Step 2: Add cmd_convert handler after existing handlers**

```python
@router.message(Command("convert"))
async def cmd_convert(message: Message, bot: Bot):
    """Handle /convert command in groups - converts .md file from replied message."""
    # Check if this is a reply
    if not message.reply_to_message:
        return  # Ignore if not a reply

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
```

- [ ] **Step 3: Add missing imports in handlers.py**

Add imports for error types at top:

```python
from .errors import InvalidFileFormat, FileTooLarge
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "C:\Users\const\OneDrive\Рабочий стол\Repos\mdToPdf" && python -m pytest tests/test_group_convert.py -v`
Expected: PASS

- [ ] **Step 5: Commit handler implementation**

```bash
git add bot/handlers.py
git commit -m "feat: add /convert command for group chats"
```

---

### Task 3: Update /help command

**Files:**
- Modify: `bot/handlers.py`

- [ ] **Step 1: Update /help command text**

Replace the `cmd_help` function with updated text:

```python
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
```

- [ ] **Step 2: Commit help update**

```bash
git add bot/handlers.py
git commit -m "docs: update /help with group usage instructions"
```

---

## Chunk 2: Additional Tests & Finalization

### Task 4: Add edge case tests

**Files:**
- Modify: `tests/test_group_convert.py`

- [ ] **Step 1: Add test for /convert without reply**

```python
@pytest.mark.asyncio
async def test_cmd_convert_without_reply(mock_bot):
    """Test /convert command without reply - should be ignored."""
    message = MagicMock(spec=Message)
    message.message_id = 100
    message.reply_to_message = None
    message.answer = AsyncMock()

    await cmd_convert(message, mock_bot)

    message.answer.assert_not_called()
```

- [ ] **Step 2: Add test for /convert reply to non-document**

```python
@pytest.mark.asyncio
async def test_cmd_convert_reply_to_non_document(mock_bot):
    """Test /convert command replying to message without document."""
    message = MagicMock(spec=Message)
    message.message_id = 100
    message.reply_to_message = MagicMock(spec=Message)
    message.reply_to_message.document = None
    message.answer = AsyncMock()

    await cmd_convert(message, mock_bot)

    message.answer.assert_called_once()
    call_args = message.answer.call_args
    assert "❌ Это не .md файл" in call_args[0][0]
```

- [ ] **Step 3: Add test for /convert reply to non-md file**

```python
@pytest.mark.asyncio
async def test_cmd_convert_reply_to_non_md_file(mock_bot):
    """Test /convert command replying to non-.md document."""
    message = MagicMock(spec=Message)
    message.message_id = 100
    message.reply_to_message = MagicMock(spec=Message)
    message.reply_to_message.document = MagicMock(spec=Document)
    message.reply_to_message.document.file_name = "test.pdf"
    message.reply_to_message.document.file_size = 1000
    message.answer = AsyncMock()

    await cmd_convert(message, mock_bot)

    message.answer.assert_called_once()
    call_args = message.answer.call_args
    assert "❌ Ошибка конвертации" in call_args[0][0]
```

- [ ] **Step 4: Run all tests**

Run: `cd "C:\Users\const\OneDrive\Рабочий стол\Repos\mdToPdf" && python -m pytest tests/test_group_convert.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit tests**

```bash
git add tests/test_group_convert.py
git commit -m "test: add edge case tests for group /convert"
```

---

### Task 5: Final verification and push

- [ ] **Step 1: Run all tests in project**

Run: `cd "C:\Users\const\OneDrive\Рабочий стол\Repos\mdToPdf" && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Push changes to remote**

```bash
git push origin main
```

- [ ] **Step 3: Deploy to server**

```bash
scp -r bot/ server-guru:/opt/md2pdf/bot/
ssh server-guru "cd /opt/md2pdf && docker compose restart"
```

---

## Summary

**Files Modified:**
- `bot/handlers.py` — added `/convert` handler, updated imports, updated `/help`

**Files Created:**
- `tests/test_group_convert.py` — tests for group conversion

**Commits:**
1. `test: add failing test for group /convert command`
2. `feat: add /convert command for group chats`
3. `docs: update /help with group usage instructions`
4. `test: add edge case tests for group /convert`
