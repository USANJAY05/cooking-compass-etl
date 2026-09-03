from .google_images import get_image_url as get_google_image_url
from .google_images import search_google_images
from .pexels import get_image_url as get_pexels_image_url
from .pexels import search_pexels
from .wikimedia import get_image_url as get_wikimedia_image_url
from .wikimedia import search_wikimedia

PROVIDERS = {
    "google": (search_google_images, get_google_image_url),
    "pexels": (search_pexels, get_pexels_image_url),
    "wikimedia": (search_wikimedia, get_wikimedia_image_url),
}


def get_provider(name: str):
    try:
        return PROVIDERS[name.lower()]
    except KeyError as exc:
        choices = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unknown provider '{name}'. Choose from: {choices}") from exc
