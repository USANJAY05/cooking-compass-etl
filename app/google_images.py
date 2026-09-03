import re
import requests

from .config import GOOGLE_CSE_ID, GOOGLE_SEARCH_API_KEY

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

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
    return QUERY_OVERRIDES.get(
        clean.lower(), f"fresh raw {clean} whole ingredient single food"
    )


def _text_for_item(item: dict) -> str:
    image = item.get("image", {})
    return " ".join(
        str(value)
        for value in (
            item.get("title", ""),
            item.get("snippet", ""),
            item.get("displayLink", ""),
            image.get("contextLink", ""),
        )
        if value
    ).lower()


def _is_relevant_item(item: dict) -> bool:
    text = _text_for_item(item)
    return not any(term in text for term in EXCLUDED_TERMS)


def search_google_images(name: str, per_page: int = 10):
    if not GOOGLE_SEARCH_API_KEY:
        raise RuntimeError(
            "GOOGLE_SEARCH_API_KEY is missing. Add it to your .env file."
        )
    if not GOOGLE_CSE_ID:
        raise RuntimeError("GOOGLE_CSE_ID is missing. Add it to your .env file.")

    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": build_query(name),
        "searchType": "image",
        "imgType": "photo",
        "safe": "active",
        "filter": "1",
        "num": min(max(per_page, 1), 10),
        "gl": "in",
        "lr": "lang_en",
    }

    response = requests.get(GOOGLE_SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    items = response.json().get("items", [])

    relevant = [item for item in items if _is_relevant_item(item)]
    return (relevant or items)[0] if items else None


def get_image_url(item):
    image = item.get("image", {})
    return image.get("thumbnailLink") or item.get("link")
