import re
import requests

WIKIMEDIA_SEARCH_URL = "https://commons.wikimedia.org/w/api.php"


def build_query(name: str) -> str:
    clean = re.sub(r"[^\w\s,-]", " ", name or "").strip()
    return f"{clean} ingredient"


def search_wikimedia(name: str, per_page: int = 10):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": build_query(name),
        "gsrnamespace": 6,
        "gsrlimit": min(max(per_page, 1), 50),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1000,
    }
    headers = {
        "User-Agent": "IngredientImageFetcher/1.0 (culinary ingredient image utility)"
    }

    response = requests.get(
        WIKIMEDIA_SEARCH_URL, params=params, headers=headers, timeout=30
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})

    # MediaWiki returns page IDs as dictionary keys, so normalize to a list.
    candidates = list(pages.values())
    candidates.sort(key=lambda page: page.get("index", 999999))
    return candidates[0] if candidates else None


def get_image_url(page):
    imageinfo = (page.get("imageinfo") or [{}])[0]
    return imageinfo.get("thumburl") or imageinfo.get("url")
