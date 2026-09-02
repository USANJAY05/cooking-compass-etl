import re
import requests

from .config import PEXELS_API_KEY, PEXELS_SEARCH_URL

# Phrases chosen to push Pexels toward clean ingredient photography rather
# than finished recipes or restaurant photography.
QUERY_OVERRIDES = {
    "drumstick": "moringa pods fresh ingredient",
    "drumstick leaf": "moringa leaves fresh ingredient",
    "chili": "fresh chilli pepper ingredient",
    "chilli": "fresh chilli pepper ingredient",
    "green chili": "fresh green chilli pepper ingredient",
    "red chili": "fresh red chilli pepper ingredient",
    "coriander": "fresh coriander leaves ingredient",
    "cilantro": "fresh coriander leaves ingredient",
    "curry leaf": "fresh curry leaves ingredient",
}


def _clean(value: str) -> str:
    return re.sub(r"[^\w\s,-]", " ", value or "").strip()


def build_query(name: str) -> str:
    clean = _clean(name)
    override = QUERY_OVERRIDES.get(clean.lower())
    if override:
        return override

    # New query style: "fresh <ingredient> ingredient photography".
    # This avoids the old "food ingredient" wording, which can bias results
    # toward prepared dishes containing the ingredient.
    return f"fresh {clean} ingredient photography"


def search_pexels(name: str, per_page: int = 10):
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY is missing. Add it to your .env file.")

    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "IngredientImageFetcher/3.0",
    }
    params = {
        "query": build_query(name),
        "per_page": min(max(per_page, 1), 80),
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
