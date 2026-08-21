from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateManager:
    """
    Persistent state for social-post automation.

    IMPORTANT:
    topics.docx is the single source of truth.

    On every run:
      1. sync() adds current DOCX topics that are not in state.
      2. sync() removes stale topics that no longer exist in DOCX.
      3. next() can therefore ONLY return topics currently present in DOCX.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {
                "version": 3,
                "topics": {},
                "last_run": None,
            }

        try:
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))

            if not isinstance(data, dict):
                raise ValueError("state.json root must be an object")

            data.setdefault("version", 3)
            data.setdefault("topics", {})
            data.setdefault("last_run", None)

            if not isinstance(data["topics"], dict):
                data["topics"] = {}

            return data

        except (json.JSONDecodeError, OSError, ValueError) as exc:
            # Never continue with corrupt state because that can cause
            # unexpected duplicate/stale publishing.
            raise RuntimeError(
                f"state.json is invalid or unreadable: {exc}"
            ) from exc

    @staticmethod
    def topic_id(topic: str) -> str:
        """
        Stable ID based on normalized topic text.
        """
        normalized = " ".join(topic.strip().split()).casefold()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write to avoid partially-written JSON.
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        tmp.replace(self.path)

    @staticmethod
    def _normalize_topic(topic: str) -> str:
        return " ".join(topic.strip().split())

    def sync(self, items: list[dict]) -> None:
        """
        Make DOCX the single source of truth.

        Topics currently in the Word file are retained/added.
        Topics that existed in state.json but are NOT in the current
        Word file are removed from active state.
        """

        current: dict[str, dict] = {}

        for item in items:
            topic = self._normalize_topic(item.get("topic", ""))
            if not topic:
                continue

            tid = self.topic_id(topic)
            previous = self.data["topics"].get(tid)

            if previous:
                # Keep publishing history for an existing current topic.
                previous["topic"] = topic
                previous["category"] = item.get(
                    "category",
                    previous.get("category", "generic"),
                )
                previous["updated_at"] = now()

                current[tid] = previous

            else:
                current[tid] = {
                    "id": tid,
                    "topic": topic,
                    "category": item.get("category", "generic"),
                    "status": "PENDING",
                    "attempts": 0,
                    "created_at": now(),
                    "updated_at": now(),
                    "image_path": None,
                    "instagram": {
                        "status": "PENDING",
                        "url": None,
                        "error": None,
                    },
                    "linkedin": {
                        "status": "PENDING",
                        "url": None,
                        "error": None,
                    },
                    "error": None,
                }

        # Replace state topics with ONLY current DOCX topics.
        # This permanently prevents deleted/old topics from being selected.
        self.data["topics"] = current
        self.data["version"] = 3
        self.data["updated_at"] = now()

    def next(self, limit: int) -> list[dict]:
        """
        Return only current DOCX topics that are not fully published.
        """

        if limit <= 0:
            return []

        values = list(self.data["topics"].values())

        # Stable document insertion/order proxy.
        values.sort(
            key=lambda item: (
                item.get("created_at", ""),
                item.get("topic", "").casefold(),
            )
        )

        pending = [
            item
            for item in values
            if item.get("status") != "PUBLISHED"
        ]

        return pending[:limit]

    def mark(
        self,
        tid: str,
        status: str,
        **updates,
    ) -> None:
        if tid not in self.data["topics"]:
            raise KeyError(
                f"Cannot update unknown topic id {tid}. "
                "The topic may no longer exist in topics.docx."
            )

        item = self.data["topics"][tid]
        item["status"] = status
        item["updated_at"] = now()

        if status == "PROCESSING":
            item["attempts"] = int(item.get("attempts", 0)) + 1

        item.update(updates)

    def mark_platform(
        self,
        tid: str,
        platform: str,
        status: str,
        url: str | None = None,
        error: str | None = None,
    ) -> None:
        if tid not in self.data["topics"]:
            raise KeyError(f"Unknown topic id: {tid}")

        if platform not in {"instagram", "linkedin"}:
            raise ValueError(f"Unsupported platform: {platform}")

        self.data["topics"][tid][platform] = {
            "status": status,
            "url": url,
            "error": error,
        }
        self.data["topics"][tid]["updated_at"] = now()

    def set_last_run(self) -> None:
        self.data["last_run"] = now()
        self.data["updated_at"] = now()

    def active_topic_names(self) -> set[str]:
        """
        Useful for debugging and workflow logs.
        """
        return {
            self._normalize_topic(item.get("topic", "")).casefold()
            for item in self.data["topics"].values()
            if item.get("topic")
        }
