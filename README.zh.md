# md2pdf - Telegram Markdown 转 PDF 机器人

[EN](README.md) · [RU](README.ru.md) · **中文** · [Español](README.es.md) · [Français](README.fr.md)

Telegram 机器人，把 Markdown 文件转换为 PDF，支持表格、代码高亮和西里尔文字。

## 工作原理

文件不会存储在服务器上。

### 1. 安全的临时目录
```python
with secure_temp_dir() as temp_dir:
    # Files are created here
    ...
    # Context manager exits
    # → shutil.rmtree() deletes EVERYTHING
```

文件在 `/tmp/md2pdf_xxx/` 目录中处理，转换完成后或进程崩溃时该目录会被删除。

### 2. 清理残留目录
如果进程被强制终止（`kill -9`），`/tmp/` 中可能会留下残留目录。`cleanup_old_temp_dirs()` 会删除所有存在时间超过 5 分钟的 `md2pdf_*` 目录。该函数在以下时机运行：
- 每次成功转换后
- 机器人启动时
- 作为后台任务定期运行

部署说明：

- Docker 部署，无数据库或持久化存储
- 文件在隔离的临时目录中处理
- 崩溃或退出时自动清理

## 快速开始

### 1. 创建 Telegram 机器人

找 [@BotFather](https://t.me/BotFather) 创建一个新机器人，拿到 token。

### 2. 用 Docker 运行

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

### 3. 测试

在 Telegram 中找到你的机器人，发送一个 `.md` 文件。

## 配置

环境变量（`.env` 文件）：

| 变量 | 默认值 | 说明 |
|----------|---------|-------------|
| `BOT_TOKEN` | *必填* | 来自 @BotFather 的 Telegram 机器人 token |
| `MAX_FILE_SIZE_MB` | `10` | 文件大小上限（MB） |
| `CONVERSION_TIMEOUT` | `60` | 转换超时（秒） |
| `LOG_LEVEL` | `INFO` | 日志级别（DEBUG、INFO、WARNING、ERROR） |

## .env 示例

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
MAX_FILE_SIZE_MB=10
CONVERSION_TIMEOUT=60
LOG_LEVEL=INFO
```

## 支持的 Markdown 语法

- 标题（`#`、`##`、`###`）
- 粗体（`**text**`）、斜体（`*text*`）
- 列表（有序和无序）
- 表格
- 带语法高亮的代码块
- 引用块
- 链接和图片

## 架构

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

## 技术栈

- Python 3.12
- aiogram 3.4.1 (Telegram Bot API)
- WeasyPrint 60.2（PDF 渲染）
- markdown + Pygments（解析和高亮）

## 开发

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

## 许可证

MIT
