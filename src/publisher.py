from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from adapters.instagram import publish as publish_instagram
from adapters.linkedin import publish as publish_linkedin
from config import settings
from topic_manager import load_state, save_state

ROOT = Path(__file__).resolve().parents[1]


def public_image_url(relative_path: str) -> str:
    if settings.public_image_base_url:
        return f"{settings.public_image_base_url.rstrip('/')}/{relative_path.lstrip('/')}"
    if settings.github_owner and settings.github_repo:
        return f"https://raw.githubusercontent.com/{settings.github_owner}/{settings.github_repo}/{settings.github_branch}/{relative_path.lstrip('/')}"
    raise RuntimeError("Set PUBLIC_IMAGE_BASE_URL or GITHUB_OWNER/GITHUB_REPO")


def wait_for_public_image(url: str) -> None:
    for attempt in range(12):
        try:
            response = requests.head(url, timeout=20, allow_redirects=True)
            if response.status_code < 400:
                return
        except requests.RequestException:
            pass
        time.sleep(5)
    raise RuntimeError(f"Generated image is not publicly reachable: {url}")


def main() -> None:
    state = load_state(settings.state_file)
    processing = [item for item in state.topics.values() if item.status == "PROCESSING"]

    if not processing:
        print("No PROCESSING topics ready for publishing.")
        return

    for item in processing:
        try:
            if not item.image_file or not item.content_file:
                raise RuntimeError("Missing generated image/content metadata")

            content = json.loads((ROOT / item.content_file).read_text(encoding="utf-8"))
            image_url = public_image_url(item.image_file)
            if not settings.dry_run:
                wait_for_public_image(image_url)

            if item.instagram_status != "PUBLISHED":
                if settings.dry_run:
                    item.instagram_url = "DRY_RUN"
                else:
                    item.instagram_url = publish_instagram(image_url, content["instagram_caption"])
                item.instagram_status = "PUBLISHED"

            if item.linkedin_status != "PUBLISHED":
                if settings.dry_run:
                    item.linkedin_url = "DRY_RUN"
                else:
                    item.linkedin_url = publish_linkedin(
                        str(ROOT / item.image_file),
                        content["linkedin_post"],
                        content["alt_text"],
                    )
                item.linkedin_status = "PUBLISHED"

            item.status = "PUBLISHED"
            from datetime import datetime, timezone
            item.published_at = datetime.now(timezone.utc).isoformat()
            item.last_error = None
            print(f"Published: {item.topic}")
        except Exception as exc:
            item.status = "FAILED"
            item.last_error = str(exc)
            print(f"FAILED publishing {item.topic}: {exc}")

    save_state(settings.state_file, state)
    if any(item.status == "FAILED" for item in processing):
        raise SystemExit("One or more topics failed during publishing")


if __name__ == "__main__":
    main()
