from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class TopicState:
    topic_id: str
    topic: str
    status: str = "PENDING"
    attempts: int = 0
    last_error: Optional[str] = None
    image_file: Optional[str] = None
    content_file: Optional[str] = None
    instagram_status: str = "PENDING"
    linkedin_status: str = "PENDING"
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    published_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class State:
    topics: dict[str, TopicState] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"topics": {k: v.to_dict() for k, v in self.topics.items()}}
