# md2pdf - Telegram Markdown to PDF Bot

Telegram bot that converts Markdown files to PDF with support for tables, code highlighting, and Cyrillic text.

## NDA Safe - How It works

Your files are **never stored on the server**. Here's how:

### 1. Secure Temporary Directory
```python
with secure_temp_dir() as temp_dir:
    # Files are created here
    ...
    # Context manager exits
    # → shutil.rmtree() deletes EVERYTHING
```

Files are processed in `/tmp/md2pdf_xxx/` directory which is automatically removed after the conversion completes, even if the bot crashes.

### 2. Orphaned Directory Cleanup
If the process crashes hard (killed -9), orphaned directories may remain in `/tmp/`. To prevent data leaks, we `cleanup_old_temp_dirs()` scans for and removes any `md2pdf_*` directories older than 5 minutes. This runs:
- After each successful conversion
- When the bot starts up
- Periodically as a background task

**This is a production-ready deployment:**

- Uses Docker for easy deployment
- No database or persistent storage
- Files processed in isolated temporary directories
- Automatic cleanup on crash or exit

## Quick Start

### 1. Create Telegram Bot

Talk to [@BotFather](https://t.me/BotFather) and create a new bot. Get the token.

### 2. Run with Docker

```bash
# Clone repository
git clone https://github.com/vonavikon/.md2pdf.git
cd .md2pdf

# Create .env file
echo "BOT_TOKEN=your_token_from_botfather" > .env

# Build and run
docker build -t md2pdf .
docker run -d --name md2pdf-bot --env-file .env md2pdf
```

### 3. Test

Find your bot in Telegram and send a `.md` file.

## Configuration

Environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_TOKEN` | *required* | Telegram bot token from @BotFather |
| `MAX_FILE_SIZE_MB` | `10` | Maximum file size in MB |
| `CONVERSION_TIMEOUT` | `60` | Conversion timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Example .env

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
MAX_FILE_SIZE_MB=10
CONVERSION_TIMEOUT=60
LOG_LEVEL=INFO
```

## Supported Markdown

- Headers (`#`, `##`, `###`)
- Bold (`**text**`), Italic (`*text*`)
- Lists (ordered and unordered)
- Tables
- Code blocks with syntax highlighting
- Blockquotes
- Links and images

## Architecture

```
Telegram User (.md file)
        │
        ▼
   bot/handlers.py      ← Command handlers
        │
        ▼
 bot/file_pipeline.py   ← Validation & conversion
        │
        ▼
 converter/md2pdf.py    ← Markdown → HTML → PDF
        │
        ▼
    PDF response
```

## Tech Stack

- Python 3.12
- aiogram 3.4.1 (Telegram Bot API)
- WeasyPrint 60.2 (PDF rendering)
- markdown + Pygments (parsing & highlighting)

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

## License

MIT
