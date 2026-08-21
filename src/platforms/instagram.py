from __future__ import annotations

import time
from urllib.parse import urlparse

import requests

from src.platforms.base import Publisher, PublishResult


class InstagramPublisher(Publisher):
    """
    Instagram API with Instagram Login.

    IMPORTANT:
    This publisher ONLY creates REELS.
    It never sends image_url to the Instagram media endpoint.

    Required:
      - INSTAGRAM_ACCESS_TOKEN
      - INSTAGRAM_ACCOUNT_ID
      - INSTAGRAM_GRAPH_BASE_URL (normally https://graph.instagram.com)
      - INSTAGRAM_API_VERSION (configurable, default v25.0)
    """

    def __init__(
        self,
        token: str,
        account_id: str,
        base_url: str,
        api_version: str = "v25.0",
    ):
        self.token = (token or "").strip()
        self.account_id = (account_id or "").strip()
        self.base_url = (
            base_url or "https://graph.instagram.com"
        ).strip().rstrip("/")
        self.api_version = (api_version or "v25.0").strip().strip("/")

    @property
    def api_root(self) -> str:
        return f"{self.base_url}/{self.api_version}"

    def validate_configuration(self) -> str | None:
        missing = []

        if not self.token:
            missing.append("INSTAGRAM_ACCESS_TOKEN")
        if not self.account_id:
            missing.append("INSTAGRAM_ACCOUNT_ID")
        if not self.base_url:
            missing.append("INSTAGRAM_GRAPH_BASE_URL")

        if missing:
            return "Missing Instagram configuration: " + ", ".join(missing)

        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            return "INSTAGRAM_GRAPH_BASE_URL must be a valid HTTPS URL."

        if not self.account_id.isdigit():
            return "INSTAGRAM_ACCOUNT_ID must be numeric."

        return None

    def _post(self, path: str, params: dict) -> requests.Response:
        return requests.post(
            f"{self.api_root}/{path.lstrip('/')}",
            params=params,
            timeout=90,
        )

    def _get(self, path: str, params: dict) -> requests.Response:
        return requests.get(
            f"{self.api_root}/{path.lstrip('/')}",
            params=params,
            timeout=60,
        )

    @staticmethod
    def _error_text(response: requests.Response) -> str:
        try:
            payload = response.json()
            error = payload.get("error") or {}
            if error:
                parts = [str(error.get("message", "Unknown Instagram API error"))]
                if error.get("code") is not None:
                    parts.append(f"code={error['code']}")
                if error.get("error_subcode") is not None:
                    parts.append(f"subcode={error['error_subcode']}")
                return " | ".join(parts)
            return response.text[:1200]
        except ValueError:
            return response.text[:1200]

    def _wait_for_container(self, container_id: str) -> PublishResult:
        for _ in range(20):
            response = self._get(
                container_id,
                {
                    "fields": "status_code,status",
                    "access_token": self.token,
                },
            )

            if not response.ok:
                return PublishResult(
                    False,
                    message=(
                        "Instagram Reel status check failed: "
                        f"HTTP {response.status_code}; "
                        f"{self._error_text(response)}"
                    ),
                )

            payload = response.json()
            status = payload.get("status_code") or payload.get("status")
            print(f"Instagram Reel container status: {status}")

            if status == "FINISHED":
                return PublishResult(True, message="Instagram Reel is ready.")

            if status in {"ERROR", "EXPIRED"}:
                return PublishResult(
                    False,
                    message=f"Instagram Reel container failed: {status}",
                )

            time.sleep(6)

        return PublishResult(
            False,
            message="Instagram Reel container did not become FINISHED in time.",
        )

    def publish_reel(self, video_url: str, caption: str) -> PublishResult:
        configuration_error = self.validate_configuration()
        if configuration_error:
            return PublishResult(False, message=configuration_error)

        if not video_url.startswith("https://"):
            return PublishResult(
                False,
                message="Instagram requires a publicly reachable HTTPS video_url.",
            )

        # Never publish images. This request explicitly creates a REEL.
        create_response = self._post(
            f"{self.account_id}/media",
            {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": self.token,
            },
        )

        if not create_response.ok:
            return PublishResult(
                False,
                message=(
                    "Instagram Reel container creation failed: "
                    f"HTTP {create_response.status_code}; "
                    f"{self._error_text(create_response)}"
                ),
            )

        container_id = create_response.json().get("id")
        if not container_id:
            return PublishResult(
                False,
                message=f"Instagram returned no Reel container ID: {create_response.text}",
            )

        ready = self._wait_for_container(container_id)
        if not ready.success:
            return ready

        publish_response = self._post(
            f"{self.account_id}/media_publish",
            {
                "creation_id": container_id,
                "access_token": self.token,
            },
        )

        if not publish_response.ok:
            return PublishResult(
                False,
                message=(
                    "Instagram Reel publish failed: "
                    f"HTTP {publish_response.status_code}; "
                    f"{self._error_text(publish_response)}"
                ),
            )

        media_id = publish_response.json().get("id")
        if not media_id:
            return PublishResult(
                False,
                message=f"Instagram returned no Reel media ID: {publish_response.text}",
            )

        permalink_response = self._get(
            media_id,
            {
                "fields": "permalink,media_type",
                "access_token": self.token,
            },
        )

        permalink = None
        if permalink_response.ok:
            payload = permalink_response.json()
            permalink = payload.get("permalink")
            media_type = payload.get("media_type")
            if media_type and media_type != "VIDEO":
                return PublishResult(
                    False,
                    message=f"Instagram published media type was {media_type}, expected VIDEO/REEL.",
                )

        return PublishResult(
            True,
            url=permalink or media_id,
            message="Instagram Reel published successfully.",
        )

    def publish(self, image_path: str, image_url: str, caption: str) -> PublishResult:
        # Deliberately disabled so the project can never accidentally publish
        # a normal image post.
        return PublishResult(
            False,
            message=(
                "Normal Instagram image publishing is disabled. "
                "Use publish_reel(video_url, caption) only."
            ),
        )
