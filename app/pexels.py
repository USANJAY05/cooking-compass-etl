import re
import requests
from .config import PEXELS_API_KEY, PEXELS_SEARCH_URL


def build_query(name: str) -> str:
    clean = re.sub(r"[^\w\s,-]", " ", name).strip()
    return f"{clean} food ingredient"


def search_pexels(name: str, per_page: int = 10):
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY is missing. Add it to your .env file.")

    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "IngredientImageFetcher/1.0",
    }
    params = {
        "query": build_query(name),
        "per_page": per_page,
        "orientation": "square",
        "size": "medium",
    }

    response = requests.get(
        PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30
    )
    response.raise_for_status()
    photos = response.json().get("photos", [])
    return photos[0] if photos else None


def get_image_url(photo):
    sources = photo.get("src", {})
    return sources.get("large") or sources.get("medium") or sources.get("original")
