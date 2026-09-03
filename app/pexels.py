import re
import requests

from .config import PEXELS_API_KEY, PEXELS_SEARCH_URL

# Explicit mappings for ingredient names that are ambiguous or commonly
# associated with dishes, people, places, or non-culinary subjects.
QUERY_OVERRIDES = {
    "drumstick": "fresh moringa drumstick pods raw vegetable",
    "drumstick leaf": "fresh moringa leaves raw ingredient",
    "chili": "fresh chilli pepper raw ingredient",
    "chilli": "fresh chilli pepper raw ingredient",
    "green chili": "fresh green chilli pepper raw ingredient",
    "red chili": "fresh red chilli pepper raw ingredient",
    "coriander": "fresh coriander leaves raw herb",
    "cilantro": "fresh coriander leaves raw herb",
    "curry leaf": "fresh curry leaves raw herb",
    "corn": "fresh corn on cob raw vegetable",
}


def _clean(value: str) -> str:
    return re.sub(r"[^\w\s,-]", " ", value or "").strip()


def build_query(name: str) -> str:
    clean = _clean(name)
    override = QUERY_OVERRIDES.get(clean.lower())
    if override:
        return override

    # Keep the search focused on the physical ingredient rather than recipes,
    # prepared dishes, restaurants, cookbooks, or historical documents.
    return f"fresh raw {clean} whole ingredient"


def search_pexels(name: str, per_page: int = 10):
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY is missing. Add it to your .env file.")

    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "IngredientImageFetcher/4.0",
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
