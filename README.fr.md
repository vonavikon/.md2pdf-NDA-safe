# md2pdf - Bot Telegram de Markdown en PDF

[EN](README.md) · [RU](README.ru.md) · [中文](README.zh.md) · [Español](README.es.md) · **Français**

Bot Telegram qui convertit des fichiers Markdown en PDF, avec prise en charge des tableaux, de la coloration syntaxique et de l'alphabet cyrillique.

## Fonctionnement

Les fichiers ne sont pas conservés sur le serveur.

### 1. Répertoire temporaire sécurisé
```python
with secure_temp_dir() as temp_dir:
    # Files are created here
    ...
    # Context manager exits
    # → shutil.rmtree() deletes EVERYTHING
```

Les fichiers sont traités dans un répertoire `/tmp/md2pdf_xxx/`, supprimé après la conversion ou en cas de plantage.

### 2. Nettoyage des répertoires orphelins
Si le processus est tué brutalement (`kill -9`), des répertoires orphelins peuvent rester dans `/tmp/`. `cleanup_old_temp_dirs()` supprime tout répertoire `md2pdf_*` vieux de plus de 5 minutes. Elle s'exécute :
- après chaque conversion réussie
- au démarrage du bot
- périodiquement, en tâche de fond

Remarques de déploiement :

- Docker, sans base de données ni stockage persistant
- Fichiers traités dans des répertoires temporaires isolés
- Nettoyage automatique en cas de plantage ou à la fermeture

## Démarrage rapide

### 1. Créer le bot Telegram

Écrivez à [@BotFather](https://t.me/BotFather) et créez un nouveau bot. Récupérez le token.

### 2. Lancer avec Docker

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

### 3. Tester

Retrouvez votre bot dans Telegram et envoyez-lui un fichier `.md`.

## Configuration

Variables d'environnement (fichier `.env`) :

| Variable | Valeur par défaut | Description |
|----------|---------|-------------|
| `BOT_TOKEN` | *obligatoire* | Token du bot Telegram fourni par @BotFather |
| `MAX_FILE_SIZE_MB` | `10` | Taille maximale du fichier en Mo |
| `CONVERSION_TIMEOUT` | `60` | Délai maximal de conversion en secondes |
| `LOG_LEVEL` | `INFO` | Niveau de journalisation (DEBUG, INFO, WARNING, ERROR) |

## Exemple de .env

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
MAX_FILE_SIZE_MB=10
CONVERSION_TIMEOUT=60
LOG_LEVEL=INFO
```

## Markdown pris en charge

- Titres (`#`, `##`, `###`)
- Gras (`**text**`), italique (`*text*`)
- Listes (ordonnées et non ordonnées)
- Tableaux
- Blocs de code avec coloration syntaxique
- Citations
- Liens et images

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

## Stack technique

- Python 3.12
- aiogram 3.4.1 (Telegram Bot API)
- WeasyPrint 60.2 (rendu PDF)
- markdown + Pygments (analyse et coloration)

## Développement

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

## Licence

MIT
