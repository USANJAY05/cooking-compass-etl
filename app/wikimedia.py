import re
import requests

WIKIMEDIA_SEARCH_URL = "https://commons.wikimedia.org/w/api.php"

# Wikimedia contains many historical documents, cookbooks, illustrations, and
# prepared-food photos. These terms help steer search toward clean ingredient
# photography and away from those categories.
QUERY_OVERRIDES = {
    "drumstick": "moringa drumstick pods fresh raw vegetable",
    "drumstick leaf": "moringa leaves fresh raw herb",
    "chili": "fresh chilli pepper raw ingredient",
    "chilli": "fresh chilli pepper raw ingredient",
    "green chili": "fresh green chilli pepper raw ingredient",
    "red chili": "fresh red chilli pepper raw ingredient",
    "coriander": "fresh coriander leaves raw herb",
    "cilantro": "fresh coriander leaves raw herb",
    "curry leaf": "fresh curry leaves raw herb",
    "corn": "fresh corn on cob raw vegetable",
}

# Metadata/title words that are usually poor fits for a clean ingredient image.
EXCLUDED_TERMS = {
    "cookbook",
    "recipe",
    "recipes",
    "archive",
    "archival",
    "historical",
    "history",
    "illustration",
    "drawing",
    "painting",
    "poster",
    "document",
    "book",
    "page",
    "menu",
    "dish",
    "soup",
    "curry",
    "salad",
    "meal",
    "restaurant",
}


def _clean(value: str) -> str:
    return re.sub(r"[^\w\s,-]", " ", value or "").strip()


def build_query(name: str) -> str:
    clean = _clean(name)
    override = QUERY_OVERRIDES.get(clean.lower())
    if override:
        return override

    # Search for the raw physical ingredient, not a prepared dish or document.
    return f"fresh raw {clean} whole ingredient"


def _metadata_text(page) -> str:
    imageinfo = (page.get("imageinfo") or [{}])[0]
    metadata = imageinfo.get("extmetadata") or {}
    parts = [page.get("title", "")]

    for key in ("ObjectName", "ImageDescription", "Categories"):
        value = metadata.get(key, {})
        parts.append(str(value.get("value", "")) if isinstance(value, dict) else str(value))

    return " ".join(parts).lower()


def _is_excluded(page) -> bool:
    text = _metadata_text(page)
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in EXCLUDED_TERMS)


def search_wikimedia(name: str, per_page: int = 10):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": build_query(name),
        "gsrnamespace": 6,
        # Ask for more candidates because we filter out poor matches locally.
        "gsrlimit": min(max(per_page * 3, 1), 50),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1000,
    }
    headers = {
        "User-Agent": "IngredientImageFetcher/2.0 (culinary ingredient image utility)"
    }

    response = requests.get(
        WIKIMEDIA_SEARCH_URL, params=params, headers=headers, timeout=30
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})

    candidates = list(pages.values())
    candidates.sort(key=lambda page: page.get("index", 999999))

    # Prefer clean ingredient candidates. We cannot reliably inspect the actual
    # pixels here, so this filters based on Wikimedia's title/description/
    # category metadata. A later image-content classifier can make this stricter.
    filtered = [page for page in candidates if not _is_excluded(page)]
    return (filtered or candidates)[:per_page][0] if (filtered or candidates) else None


def get_image_url(page):
    imageinfo = (page.get("imageinfo") or [{}])[0]
    return imageinfo.get("thumburl") or imageinfo.get("url")
