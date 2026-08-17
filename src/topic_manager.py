from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from docx import Document

from models import State, TopicState


def read_topics(path: str) -> list[str]:
    document = Document(path)
    topics: list[str] = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        if text.lower().startswith("instructions:"):
            continue
        # Treat Word headings as metadata rather than topics.
        if paragraph.style and paragraph.style.name.lower().startswith("title"):
            continue
        if paragraph.style and paragraph.style.name.lower().startswith("heading"):
            continue
        topics.append(text)
    return topics


def topic_id(topic: str) -> str:
    return hashlib.sha256(topic.strip().lower().encode("utf-8")).hexdigest()[:16]


def load_state(path: str) -> State:
    file = Path(path)
    if not file.exists():
        return State()
    payload = json.loads(file.read_text(encoding="utf-8"))
    topics = {}
    for key, value in payload.get("topics", {}).items():
        value.setdefault("instagram_status", "PENDING")
        value.setdefault("linkedin_status", "PENDING")
        topics[key] = TopicState(**value)
    return State(topics=topics)


def save_state(path: str, state: State) -> None:
    Path(path).write_text(
        json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sync_topics(topics: Iterable[str], state: State) -> None:
    for topic in topics:
        tid = topic_id(topic)
        if tid not in state.topics:
            state.topics[tid] = TopicState(topic_id=tid, topic=topic)


def pick_next(state: State, limit: int) -> list[TopicState]:
    eligible = [item for item in state.topics.values() if item.status == "PENDING"]
    selected = eligible[:limit]
    for item in selected:
        item.status = "PROCESSING"
        item.attempts += 1
        item.last_error = None
    return selected
