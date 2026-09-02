# Ingredient Image Fetcher

Python utility for downloading ingredient images from Pexels using ingredient data stored in SQLite.

## What it does

- Reads `id` and `name` from the `ingredients` table.
- Builds a food-focused Pexels search query.
- Downloads the selected image locally as `<ingredient_id>.jpg`.
- Skips existing images unless `--force` is used.
- Includes a local Flask viewer for searching by ingredient name or ID.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Pexels API key:

```text
PEXELS_API_KEY=your_pexels_api_key_here
DATABASE_PATH=ifct2017_app.sqlite
IMAGE_DIR=images
```

The SQLite database is intentionally ignored by Git. Keep your local `ifct2017_app.sqlite` in the project root.

## Download images

Test with 10 ingredients first:

```bash
python -m app.fetch_images --limit 10
```

Process all ingredients:

```bash
python -m app.fetch_images
```

Other options:

```bash
python -m app.fetch_images --start-id 100 --limit 50
python -m app.fetch_images --force
```

Images are saved as:

```text
images/<ingredient_id>.jpg
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
├── pexels.py
├── downloader.py
├── fetch_images.py
└── viewer.py
requirements.txt
.env.example
.gitignore
README.md
```

## Important

Do not commit `.env`, your Pexels API key, the SQLite database, or downloaded image files. Review Pexels licensing/API requirements for your intended commercial distribution before publishing the downloaded assets.
