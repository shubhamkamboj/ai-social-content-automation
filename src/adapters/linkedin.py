from __future__ import annotations

import requests

from config import settings


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Linkedin-Version": settings.linkedin_version,
        "X-Restli-Protocol-Version": "2.0.0",
    }


def publish(image_file: str, caption: str, alt_text: str) -> str:
    token = __import__("os").getenv("LINKEDIN_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("LINKEDIN_ACCESS_TOKEN is required")
    if not settings.linkedin_author_urn:
        raise RuntimeError("LINKEDIN_AUTHOR_URN is required")

    init = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=_headers(token),
        json={"initializeUploadRequest": {"owner": settings.linkedin_author_urn}},
        timeout=60,
    )
    init.raise_for_status()
    payload = init.json()["value"]
    upload_url = payload["uploadUrl"]
    image_urn = payload["image"]

    with open(image_file, "rb") as handle:
        upload = requests.put(
            upload_url,
            headers={"Content-Type": "application/octet-stream"},
            data=handle,
            timeout=120,
        )
    upload.raise_for_status()

    post = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=_headers(token),
        json={
            "author": settings.linkedin_author_urn,
            "commentary": caption,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {"media": {"altText": alt_text, "id": image_urn}},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        },
        timeout=60,
    )
    post.raise_for_status()
    post_id = post.headers.get("x-restli-id") or post.json().get("id")
    return f"https://www.linkedin.com/feed/update/{post_id}/"
