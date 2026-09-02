import re
import requests

from .config import PEXELS_API_KEY, PEXELS_SEARCH_URL

# Pexels often interprets common ingredient names as dishes, people, or unrelated
# objects. Keep a small override map for known ambiguous culinary terms.
QUERY_OVERRIDES = {
    "drumstick": "moringa pods vegetable",
    "drumstick leaf": "moringa leaves",
    "chili": "fresh chilli pepper",
    "chilli": "fresh chilli pepper",
    "green chili": "fresh green chilli pepper",
    "red chili": "fresh red chilli pepper",
    "coriander": "fresh coriander leaves",
    "cilantro": "fresh coriander leaves",
    "curry leaf": "fresh curry leaves",
}

# Terms that commonly indicate a prepared dish, packaging, people, or other
# content that is undesirable for a raw-ingredient catalogue.
NEGATIVE_TERMS = {
    "recipe", "dish", "curry", "soup", "salad", "pizza", "cake", "bread",
    "meal", "restaurant", "chef", "person", "people", "hand", "hands",
    "plate", "bowl", "packaging", "package", "bottle", "can", "logo",
    "menu", "cooking", "cooked", "fried", "stew", "sandwich",
}


def _clean(value: str) -> str:
    return re.sub(r"[^\w\s,-]", " ", value or "").strip().lower()


def build_query(name: str) -> str:
    clean = _clean(name)
    return QUERY_OVERRIDES.get(clean, f"fresh {clean} raw ingredient")


def _text(photo) -> str:
    parts = [
        photo.get("alt", ""),
        photo.get("url", ""),
        photo.get("photographer", ""),
    ]
    parts.extend(photo.get("tags", []) if isinstance(photo.get("tags"), list) else [])
    return " ".join(str(part) for part in parts).lower()


def _score_photo(photo, ingredient_name: str) -> int:
    text = _text(photo)
    name = _clean(ingredient_name)
    query = build_query(ingredient_name)
    score = 0

    # Strong preference for the ingredient being mentioned in searchable metadata.
    for token in set(re.findall(r"[a-z]+", query)):
        if len(token) >= 4 and token in text:
            score += 4

    for token in set(re.findall(r"[a-z]+", name)):
        if len(token) >= 4 and token in text:
            score += 6

    for term in NEGATIVE_TERMS:
        if term in text:
            score -= 8

    width = photo.get("width") or 0
    height = photo.get("height") or 0
    if width >= 1000 and height >= 1000:
        score += 3

    # Prefer images that are reasonably square because the app will crop them
    # into ingredient cards.
    if width and height:
        ratio = min(width, height) / max(width, height)
        if ratio >= 0.8:
            score += 3
        elif ratio < 0.55:
            score -= 2

    return score


def search_pexels(name: str, per_page: int = 40):
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY is missing. Add it to your .env file.")

    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "IngredientImageFetcher/2.0",
    }
    params = {
        "query": build_query(name),
        "per_page": min(max(per_page, 1), 80),
        "orientation": "square",
        "size": "large",
    }

    response = requests.get(
        PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30
    )
    response.raise_for_status()
    photos = response.json().get("photos", [])
    if not photos:
        return None

    # Do not blindly use Pexels' first result. Score the returned candidates and
    # choose the one that best fits a clean culinary ingredient catalogue.
    return max(photos, key=lambda photo: _score_photo(photo, name))


def get_image_url(photo):
    sources = photo.get("src", {})
    return sources.get("large2x") or sources.get("large") or sources.get("original") or sources.get("medium")
