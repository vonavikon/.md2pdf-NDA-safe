# md2pdf - Telegram-бот для конвертации Markdown в PDF

[EN](README.md) · **RU** · [中文](README.zh.md) · [Español](README.es.md) · [Français](README.fr.md)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-0%2F75_clean-brightgreen)](https://www.virustotal.com/gui/file/39320341cefc43910022fbcddb2a455c045e7f6020107e4df7d2c20b2ab8fa1d)


Telegram-бот для конвертации Markdown-файлов в PDF с поддержкой таблиц, подсветки кода и кириллицы.

## Как это работает

Файлы не хранятся на сервере.

### 1. Защищённый временный каталог
```python
with secure_temp_dir() as temp_dir:
    # Files are created here
    ...
    # Context manager exits
    # → shutil.rmtree() deletes EVERYTHING
```

Файлы обрабатываются в каталоге `/tmp/md2pdf_xxx/`, который удаляется после конвертации или при падении процесса.

### 2. Очистка потерянных каталогов
Если процесс убить жёстко (`kill -9`), в `/tmp/` могут остаться потерянные каталоги. `cleanup_old_temp_dirs()` удаляет любые каталоги `md2pdf_*` старше 5 минут. Функция вызывается:
- после каждой успешной конвертации
- при запуске бота
- периодически, как фоновая задача

Примечания по развёртыванию:

- Docker, без базы данных и постоянного хранилища
- Файлы обрабатываются в изолированных временных каталогах
- Автоматическая очистка при падении или выходе

## Быстрый старт

### 1. Создайте бота в Telegram

Напишите [@BotFather](https://t.me/BotFather) и создайте нового бота. Получите токен.

### 2. Запуск через Docker

```bash
# Clone repository
git clone https://github.com/vonavikon/.md2pdf-NDA-safe.git
cd .md2pdf-NDA-safe

# Create .env file
echo "BOT_TOKEN=your_token_from_botfather" > .env

# Build and run
docker build -t md2pdf .
docker run -d --name md2pdf-bot --env-file .env md2pdf
```

### 3. Проверка

Найдите своего бота в Telegram и отправьте ему файл `.md`.

## Конфигурация

Переменные окружения (файл `.env`):

| Переменная | По умолчанию | Описание |
|----------|---------|-------------|
| `BOT_TOKEN` | *обязательно* | Токен Telegram-бота от @BotFather |
| `MAX_FILE_SIZE_MB` | `10` | Максимальный размер файла в МБ |
| `CONVERSION_TIMEOUT` | `60` | Таймаут конвертации в секундах |
| `LOG_LEVEL` | `INFO` | Уровень логирования (DEBUG, INFO, WARNING, ERROR) |

## Пример .env

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
MAX_FILE_SIZE_MB=10
CONVERSION_TIMEOUT=60
LOG_LEVEL=INFO
```

## Поддерживаемый Markdown

- Заголовки (`#`, `##`, `###`)
- Жирный (`**text**`), курсив (`*text*`)
- Списки (нумерованные и маркированные)
- Таблицы
- Блоки кода с подсветкой синтаксиса
- Цитаты
- Ссылки и изображения

## Архитектура

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

## Технологии

- Python 3.12
- aiogram 3.4.1 (Telegram Bot API)
- WeasyPrint 60.2 (рендеринг PDF)
- markdown + Pygments (парсинг и подсветка)

## Разработка

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

## Лицензия

MIT
