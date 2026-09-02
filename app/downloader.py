from pathlib import Path
import requests


def download_image(url: str, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_suffix(destination.suffix + ".part")

    with requests.get(
        url,
        stream=True,
        timeout=60,
        headers={"User-Agent": "IngredientImageFetcher/1.0"},
    ) as response:
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            raise ValueError(
                f"URL did not return an image. Content-Type: {content_type}"
            )

        with temp_path.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 64):
                if chunk:
                    output.write(chunk)

    temp_path.replace(destination)
