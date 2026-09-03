# Ingredient Image Fetcher

Python utility for downloading ingredient images from multiple image providers using ingredient data stored in SQLite.

## Supported providers

- `wikimedia` — default; uses Wikimedia Commons and requires no API key.
- `pexels` — requires a Pexels API key.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure the provider:

```text
DEFAULT_PROVIDER=wikimedia
PEXELS_API_KEY=your_pexels_api_key_here
DATABASE_PATH=ifct2017_app.sqlite
IMAGE_DIR=images
```

`DEFAULT_PROVIDER` accepts `wikimedia` or `pexels`. If it is omitted, the application defaults to `wikimedia`.

The SQLite database is intentionally ignored by Git. Keep your local `ifct2017_app.sqlite` in the project root.

## Download images

The configured provider is used by default:

```bash
python -m app.fetch_images --limit 10
```

You can temporarily override the configured provider from the command line:

```bash
python -m app.fetch_images --provider wikimedia --limit 10
python -m app.fetch_images --provider pexels --limit 10
```

Process all ingredients:

```bash
python -m app.fetch_images
```

Use `--force` to replace existing images for the selected provider:

```bash
python -m app.fetch_images --force
```

Other options:

```bash
python -m app.fetch_images --start-id 100 --limit 50
python -m app.fetch_images --force --delay 0.5
```

Images are stored separately by provider:

```text
images/
├── wikimedia/
│   └── <ingredient_id>.jpg
└── pexels/
    └── <ingredient_id>.jpg
```

## Run the image viewer

```bash
python -m app.viewer
```

Open `http://127.0.0.1:5000` and search by ingredient name or ID.

## Project structure

```text
app/
├── __init__.py
├── config.py
├── db.py
├── downloader.py
├── fetch_images.py
├── pexels.py
├── providers.py
├── viewer.py
└── wikimedia.py
requirements.txt
.env.example
.gitignore
README.md
```

## Important

Do not commit `.env`, your Pexels API key, the SQLite database, or downloaded image files. Review each provider's licensing and attribution requirements before publishing downloaded assets in a commercial app. Wikimedia Commons images can have different licenses and attribution requirements per file.

Google Custom Search was previously implemented as a provider but has been removed because the Custom Search JSON API is no longer available to new customers.
