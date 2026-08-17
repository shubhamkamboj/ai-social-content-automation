from __future__ import annotations

import requests
from src.platforms.base import Publisher, PublishResult


class LinkedInPublisher(Publisher):
    """
    Current LinkedIn Images API + Posts API pattern:
    initializeUpload -> upload bytes -> create image post.
    """

    def __init__(self, token: str, author_urn: str, version: str):
        self.token = token
        self.author_urn = author_urn
        self.version = version

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Linkedin-Version": self.version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }

    def publish(self, image_path: str, image_url: str, caption: str) -> PublishResult:
        if not self.token or not self.author_urn:
            return PublishResult(False, message="LinkedIn configuration missing.")

        try:
            init = requests.post(
                "https://api.linkedin.com/rest/images?action=initializeUpload",
                headers=self.headers,
                json={"initializeUploadRequest": {"owner": self.author_urn}},
                timeout=60,
            )
            init.raise_for_status()
            value = init.json()["value"]
            upload_url = value["uploadUrl"]
            image_urn = value["image"]

            with open(image_path, "rb") as f:
                upload_headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/octet-stream",
                }
                uploaded = requests.put(upload_url, headers=upload_headers, data=f, timeout=120)
                uploaded.raise_for_status()

            payload = {
                "author": self.author_urn,
                "commentary": caption,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": [],
                },
                "content": {
                    "media": {
                        "title": "Technical infographic",
                        "id": image_urn,
                        "altText": caption[:300],
                    }
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False,
            }

            post = requests.post(
                "https://api.linkedin.com/rest/posts",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            post.raise_for_status()

            post_id = post.headers.get("x-restli-id") or post.text
            return PublishResult(True, url=post_id, message="LinkedIn published.")

        except requests.HTTPError as exc:
            detail = ""
            try:
                detail = exc.response.text
            except Exception:
                pass
            return PublishResult(False, message=f"LinkedIn HTTP error: {exc}; {detail[:700]}")
        except Exception as exc:
            return PublishResult(False, message=f"LinkedIn error: {exc}")
