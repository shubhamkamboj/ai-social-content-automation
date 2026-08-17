from __future__ import annotations

import time
import requests

from config import settings


def publish(image_url: str, caption: str) -> str:
    token = __import__("os").getenv("INSTAGRAM_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN is required")
    if not settings.instagram_user_id:
        raise RuntimeError("INSTAGRAM_USER_ID is required")

    base = f"https://graph.facebook.com/{settings.instagram_api_version}"
    response = requests.post(
        f"{base}/{settings.instagram_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=60,
    )
    response.raise_for_status()
    creation_id = response.json()["id"]

    for _ in range(12):
        status = requests.get(
            f"{base}/{creation_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=60,
        )
        status.raise_for_status()
        status_code = status.json().get("status_code")
        if status_code == "FINISHED":
            break
        if status_code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Instagram media container failed: {status.json()}")
        time.sleep(5)

    publish_response = requests.post(
        f"{base}/{settings.instagram_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    publish_response.raise_for_status()
    media_id = publish_response.json()["id"]
    return f"https://www.instagram.com/p/{media_id}/"
