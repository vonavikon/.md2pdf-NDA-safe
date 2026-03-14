# Group Chat Convert Command

**Date:** 2026-03-14
**Status:** Approved
**Author:** Claude + User

## Summary

Add support for Markdown to PDF conversion in Telegram groups via `/convert` command. Users can reply to any message containing a `.md` file with `/convert` to get a PDF back.

## Requirements

1. Bot responds to `/convert` command when replied to a message with `.md` file
2. PDF is sent as a reply to the command (preserves conversation context)
3. All group participants can use the command (no restrictions)
4. Short error message on failure: "❌ Ошибка конвертации"
5. Maintains existing security policy (NDA Safe) — no file storage, temp files cleaned up

## Design

### Handler: `cmd_convert`

New handler in `bot/handlers.py`:

```python
@router.message(Command("convert"))
async def cmd_convert(message: Message, bot: Bot):
    # 1. Check if message is a reply
    # 2. Check if replied message has .md document
    # 3. Validate and convert (reuse existing logic)
    # 4. Send PDF as reply to the command
```

### Data Flow

```
/convert command (reply)
    ↓
Is reply? → No → Ignore
    ↓ Yes
Replied has .md document? → No → Reply "❌ Это не .md файл"
    ↓ Yes
Validate document (size, format)
    ↓
Convert (reuse secure_temp_dir + convert_document_to_pdf)
    ↓
Success → Send PDF reply to command
Error → Reply "❌ Ошибка конвертации"
```

### Code Changes

**File: `bot/handlers.py`**

1. Add import: `ReplyParameters` from aiogram
2. Extract document validation into helper function `_validate_and_get_document()`
3. Add new handler `cmd_convert()` (~30-40 lines)
4. Update `/help` command text to mention group usage

**No changes to:**
- `converter/` module
- `config.py`
- `main.py`
- Security model (`secure_temp_dir`)

### Security

- Reuses existing `secure_temp_dir` context manager
- Files processed in temp directory, auto-cleaned after conversion
- No data stored on server
- Same file size limits apply (MAX_FILE_SIZE_MB)

### Error Handling

| Error | Response |
|-------|----------|
| No reply | Ignore (no response) |
| Replied message has no .md | "❌ Это не .md файл" |
| File too large | "❌ Ошибка конвертации" |
| Conversion failed | "❌ Ошибка конвертации" |

## Implementation Notes

- Use `message.reply_to_message` to get the replied message
- Use `ReplyParameters(message_id=message.message_id)` for reply context
- Reuse `validate_markdown_document()` from `file_pipeline.py`
- Reuse `convert_document_to_pdf()` from `file_pipeline.py`
