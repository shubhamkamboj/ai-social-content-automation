from __future__ import annotations

import time
from urllib.parse import urlparse

import requests

from src.platforms.base import Publisher, PublishResult


class InstagramPublisher(Publisher):
    """
    Instagram API with Instagram Login.

    Required:
      - INSTAGRAM_ACCESS_TOKEN
      - INSTAGRAM_ACCOUNT_ID
      - INSTAGRAM_GRAPH_BASE_URL (https://graph.instagram.com)
      - INSTAGRAM_API_VERSION (example: v25.0)

    Publishing flow:
      1) POST /{ig-user-id}/media
      2) Poll /{container-id}?fields=status_code
      3) POST /{ig-user-id}/media_publish
      4) GET /{media-id}?fields=permalink
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
        self.api_version = (api_version or "v25.0").strip().strip("/")
        self.base_url = (base_url or "https://graph.instagram.com").strip().rstrip("/")

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
            return "INSTAGRAM_ACCOUNT_ID must be the numeric Instagram professional account ID."

        return None

    def _post_json(self, path: str, params: dict) -> requests.Response:
        return requests.post(
            f"{self.api_root}/{path.lstrip('/')}",
            params=params,
            timeout=90,
        )

    def _get_json(self, path: str, params: dict) -> requests.Response:
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
                message = error.get("message") or "Unknown Instagram API error"
                code = error.get("code")
                subcode = error.get("error_subcode")
                parts = [str(message)]
                if code is not None:
                    parts.append(f"code={code}")
                if subcode is not None:
                    parts.append(f"subcode={subcode}")
                return " | ".join(parts)
            return response.text[:1000]
        except ValueError:
            return response.text[:1000]

    def _wait_for_container(self, container_id: str) -> PublishResult:
        # Meta processing can take a short amount of time. Poll conservatively.
        for attempt in range(12):
            try:
                response = self._get_json(
                    f"{container_id}",
                    {
                        "fields": "status_code,status",
                        "access_token": self.token,
                    },
                )

                if not response.ok:
                    return PublishResult(
                        False,
                        message=(
                            "Instagram container status check failed: "
                            f"HTTP {response.status_code}; {self._error_text(response)}"
                        ),
                    )

                data = response.json()
                status = data.get("status_code") or data.get("status")

                if status in (None, "FINISHED", "PUBLISHED"):
                    return PublishResult(True, message="Container ready for publishing.")

                if status in ("ERROR", "EXPIRED"):
                    return PublishResult(
                        False,
                        message=f"Instagram container processing failed with status={status}.",
                    )

                time.sleep(5)

            except requests.RequestException as exc:
                return PublishResult(False, message=f"Instagram status request failed: {exc}")

        return PublishResult(
            False,
            message="Instagram media container did not reach FINISHED status within the polling window.",
        )

    def publish(self, image_path: str, image_url: str, caption: str) -> PublishResult:
        configuration_error = self.validate_configuration()
        if configuration_error:
            return PublishResult(False, message=configuration_error)

        if not image_url or not image_url.startswith("https://"):
            return PublishResult(
                False,
                message="Instagram requires a publicly reachable HTTPS image_url.",
            )

        try:
            # 1) Create media container
            create_response = self._post_json(
                f"{self.account_id}/media",
                {
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.token,
                },
            )

            if not create_response.ok:
                return PublishResult(
                    False,
                    message=(
                        "Instagram media container creation failed: "
                        f"HTTP {create_response.status_code}; "
                        f"{self._error_text(create_response)}"
                    ),
                )

            create_data = create_response.json()
            container_id = create_data.get("id")
            if not container_id:
                return PublishResult(
                    False,
                    message=f"Instagram did not return a container ID: {create_data}",
                )

            # 2) Wait until the container is ready
            ready = self._wait_for_container(container_id)
            if not ready.success:
                return ready

            # 3) Publish container
            publish_response = self._post_json(
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
                        "Instagram media publish failed: "
                        f"HTTP {publish_response.status_code}; "
                        f"{self._error_text(publish_response)}"
                    ),
                )

            publish_data = publish_response.json()
            media_id = publish_data.get("id")

            if not media_id:
                return PublishResult(
                    False,
                    message=f"Instagram publish returned no media ID: {publish_data}",
                )

            # 4) Retrieve permalink for state.json
            permalink_response = self._get_json(
                f"{media_id}",
                {
                    "fields": "permalink",
                    "access_token": self.token,
                },
            )

            permalink = None
            if permalink_response.ok:
                permalink = permalink_response.json().get("permalink")

            return PublishResult(
                True,
                url=permalink or media_id,
                message="Instagram post published successfully.",
            )

        except requests.RequestException as exc:
            return PublishResult(False, message=f"Instagram request failed: {exc}")
        except ValueError as exc:
            return PublishResult(False, message=f"Instagram returned invalid JSON: {exc}")
        except Exception as exc:
            return PublishResult(False, message=f"Instagram publishing error: {exc}")
