from __future__ import annotations

import time
import requests
from urllib.parse import quote

from src.platforms.base import Publisher, PublishResult


class InstagramPublisher(Publisher):
    """
    Instagram Graph API media-container flow.

    Configure the exact current Graph API base URL in INSTAGRAM_GRAPH_BASE_URL,
    for example a Meta Graph API version endpoint appropriate to your app.
    """

    def __init__(self, token: str, account_id: str, base_url: str):
        self.token = token
        self.account_id = account_id
        self.base_url = base_url.rstrip("/")

    def publish(self, image_path: str, image_url: str, caption: str) -> PublishResult:
        if not all([self.token, self.account_id, self.base_url]):
            return PublishResult(False, message="Instagram configuration missing.")

        media_url = f"{self.base_url}/{self.account_id}/media"
        publish_url = f"{self.base_url}/{self.account_id}/media_publish"

        try:
            r = requests.post(
                media_url,
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.token,
                },
                timeout=60,
            )
            r.raise_for_status()
            creation_id = r.json()["id"]

            # The container may need a short processing period.
            for _ in range(8):
                time.sleep(5)
                status = requests.get(
                    f"{self.base_url}/{creation_id}",
                    params={"fields": "status_code", "access_token": self.token},
                    timeout=30,
                )
                if status.ok:
                    status_code = status.json().get("status_code")
                    if status_code in (None, "FINISHED"):
                        break
                    if status_code in ("ERROR", "EXPIRED"):
                        return PublishResult(False, message=f"Instagram media status: {status_code}")

            pub = requests.post(
                publish_url,
                params={
                    "creation_id": creation_id,
                    "access_token": self.token,
                },
                timeout=60,
            )
            pub.raise_for_status()
            media_id = pub.json()["id"]

            permalink = None
            info = requests.get(
                f"{self.base_url}/{media_id}",
                params={"fields": "permalink", "access_token": self.token},
                timeout=30,
            )
            if info.ok:
                permalink = info.json().get("permalink")

            return PublishResult(True, url=permalink or media_id, message="Instagram published.")

        except requests.HTTPError as exc:
            detail = ""
            try:
                detail = exc.response.text
            except Exception:
                pass
            return PublishResult(False, message=f"Instagram HTTP error: {exc}; {detail[:700]}")
        except Exception as exc:
            return PublishResult(False, message=f"Instagram error: {exc}")
