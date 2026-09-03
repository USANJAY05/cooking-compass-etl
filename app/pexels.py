import re
import requests

from .config import PEXELS_API_KEY, PEXELS_SEARCH_URL

# Explicit mappings for ambiguous ingredient names.
QUERY_OVERRIDES = {
    "drumstick": "fresh moringa drumstick pods raw vegetable single ingredient",
    "drumstick leaf": "fresh moringa leaves raw herb single ingredient",
    "chili": "fresh chilli pepper raw ingredient single food",
    "chilli": "fresh chilli pepper raw ingredient single food",
    "green chili": "fresh green chilli pepper raw ingredient single food",
    "red chili": "fresh red chilli pepper raw ingredient single food",
    "coriander": "fresh coriander leaves raw herb single ingredient",
    "cilantro": "fresh coriander leaves raw herb single ingredient",
    "curry leaf": "fresh curry leaves raw herb single ingredient",
    "corn": "fresh corn on cob raw vegetable single ingredient",
}

# Search terms that commonly lead to the wrong kind of culinary image.
EXCLUDED_TERMS = {
    "recipe", "recipes", "dish", "dishes", "curry", "salad", "soup",
    "pizza", "burger", "restaurant", "chef", "cookbook", "book",
    "archive", "historical", "painting", "illustration", "document",
    "menu", "packaging", "bottle", "jar", "plate", "platter",
}


def _clean(value: str) -> str:
    return re.sub(r"[^\w\s,-]", " ", value or "").strip()


def build_query(name: str) -> str:
    clean = _clean(name)
    override = QUERY_OVERRIDES.get(clean.lower())
    if override:
        return override

    return f"fresh raw {clean} whole ingredient single food"


def _text_for_photo(photo: dict) -> str:
    parts = [
        photo.get("alt", ""),
        photo.get("photographer", ""),
        photo.get("photographer_url", ""),
    ]
    src = photo.get("src", {})
    parts.extend(str(value) for value in src.values() if value)
    return " ".join(parts).lower()


def _is_relevant_photo(photo: dict) -> bool:
    text = _text_for_photo(photo)
    return not any(term in text for term in EXCLUDED_TERMS)


def search_pexels(name: str, per_page: int = 40):
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY is missing. Add it to your .env file.")

    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "IngredientImageFetcher/5.0",
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

    # Prefer clean ingredient-oriented results instead of blindly taking the
    # first result. Fall back to the first result if filtering removes all
    # candidates so an ingredient is not unnecessarily marked as missing.
    relevant = [photo for photo in photos if _is_relevant_photo(photo)]
    return (relevant or photos)[0] if photos else None


def get_image_url(photo):
    sources = photo.get("src", {})
    return sources.get("large") or sources.get("medium") or sources.get("original")
