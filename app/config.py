import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "ifct2017_app.sqlite")))
IMAGE_DIR = Path(os.getenv("IMAGE_DIR", str(BASE_DIR / "images")))
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()
PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)
