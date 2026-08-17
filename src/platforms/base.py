from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PublishResult:
    success: bool
    url: str | None = None
    message: str = ""

class Publisher:
    def publish(self, image_path: str, image_url: str, caption: str) -> PublishResult:
        raise NotImplementedError
