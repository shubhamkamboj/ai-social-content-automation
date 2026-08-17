from __future__ import annotations

import hashlib


def safe_filename(topic: str) -> str:
    digest = hashlib.sha256(topic.encode("utf-8")).hexdigest()[:12]
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in topic).strip("-")
    slug = "-".join(filter(None, slug.split("-")))[:60]
    return f"{slug}-{digest}.png"
