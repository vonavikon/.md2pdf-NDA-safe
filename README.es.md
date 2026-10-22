# md2pdf - Bot de Telegram de Markdown a PDF

[EN](README.md) · [RU](README.ru.md) · [中文](README.zh.md) · **Español** · [Français](README.fr.md)

Bot de Telegram que convierte archivos Markdown a PDF, con soporte de tablas, resaltado de código y texto cirílico.

## Cómo funciona

Los archivos no se guardan en el servidor.

### 1. Directorio temporal seguro
```python
with secure_temp_dir() as temp_dir:
    # Files are created here
    ...
    # Context manager exits
    # → shutil.rmtree() deletes EVERYTHING
```

Los archivos se procesan en un directorio `/tmp/md2pdf_xxx/` que se elimina al terminar la conversión o si el proceso falla.

### 2. Limpieza de directorios huérfanos
Si el proceso termina de forma abrupta (`kill -9`), pueden quedar directorios huérfanos en `/tmp/`. `cleanup_old_temp_dirs()` elimina los directorios `md2pdf_*` con más de 5 minutos de antigüedad. Se ejecuta:
- después de cada conversión exitosa
- al iniciar el bot
- periódicamente, como tarea en segundo plano

Notas de despliegue:

- Docker, sin base de datos ni almacenamiento persistente
- Archivos procesados en directorios temporales aislados
- Limpieza automática ante un fallo o al salir

## Inicio rápido

### 1. Crear el bot de Telegram

Habla con [@BotFather](https://t.me/BotFather) y crea un bot nuevo. Guarda el token.

### 2. Ejecutar con Docker

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

### 3. Probar

Busca tu bot en Telegram y envíale un archivo `.md`.

## Configuración

Variables de entorno (archivo `.env`):

| Variable | Valor por defecto | Descripción |
|----------|---------|-------------|
| `BOT_TOKEN` | *obligatorio* | Token del bot de Telegram, entregado por @BotFather |
| `MAX_FILE_SIZE_MB` | `10` | Tamaño máximo del archivo en MB |
| `CONVERSION_TIMEOUT` | `60` | Tiempo límite de conversión en segundos |
| `LOG_LEVEL` | `INFO` | Nivel de registro (DEBUG, INFO, WARNING, ERROR) |

## Ejemplo de .env

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
MAX_FILE_SIZE_MB=10
CONVERSION_TIMEOUT=60
LOG_LEVEL=INFO
```

## Markdown admitido

- Encabezados (`#`, `##`, `###`)
- Negrita (`**text**`), cursiva (`*text*`)
- Listas (ordenadas y sin ordenar)
- Tablas
- Bloques de código con resaltado de sintaxis
- Citas en bloque
- Enlaces e imágenes

## Arquitectura

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

## Stack tecnológico

- Python 3.12
- aiogram 3.4.1 (Telegram Bot API)
- WeasyPrint 60.2 (generación de PDF)
- markdown + Pygments (análisis y resaltado)

## Desarrollo

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

## Licencia

MIT
