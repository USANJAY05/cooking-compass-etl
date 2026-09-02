import argparse
import time
from pathlib import Path

from .config import IMAGE_DIR
from .db import get_ingredients
from .downloader import download_image
from .pexels import search_pexels, get_image_url


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download one Pexels image for each ingredient."
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start-id", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--delay", type=float, default=0.4)
    return parser.parse_args()


def main():
    args = parse_args()
    ingredients = get_ingredients()

    if args.start_id is not None:
        ingredients = [
            item for item in ingredients if int(item["id"]) >= args.start_id
        ]
    if args.limit is not None:
        ingredients = ingredients[: args.limit]

    total = len(ingredients)
    print(f"Processing {total} ingredients...")
    print(f"Images directory: {IMAGE_DIR}")

    success = skipped = failed = 0

    for index, ingredient in enumerate(ingredients, start=1):
        ingredient_id = ingredient["id"]
        name = ingredient["name"]
        destination = Path(IMAGE_DIR) / f"{ingredient_id}.jpg"
        print(f"[{index}/{total}] {ingredient_id} - {name}")

        if destination.exists() and not args.force:
            print("  -> skipped (already exists)")
            skipped += 1
            continue

        try:
            photo = search_pexels(name)
            if not photo:
                print("  -> no Pexels result")
                failed += 1
                continue

            image_url = get_image_url(photo)
            if not image_url:
                print("  -> no usable image URL")
                failed += 1
                continue

            download_image(image_url, destination)
            print(
                f"  -> saved {destination.name} | photographer: "
                f"{photo.get('photographer', 'unknown')}"
            )
            success += 1
        except Exception as exc:
            print(f"  -> ERROR: {exc}")
            failed += 1

        time.sleep(max(args.delay, 0))

    print("\nDone.")
    print(f"Downloaded: {success}")
    print(f"Skipped:    {skipped}")
    print(f"Failed:     {failed}")


if __name__ == "__main__":
    main()
