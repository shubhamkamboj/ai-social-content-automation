from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

class StateManager:
    def __init__(self, path: str):
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {"version": 2, "topics": {}, "last_run": None}
        return json.loads(self.path.read_text(encoding="utf-8"))

    @staticmethod
    def topic_id(topic: str) -> str:
        return hashlib.sha256(topic.strip().casefold().encode()).hexdigest()[:16]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)

    def sync(self, items: list[dict]):
        for item in items:
            tid = self.topic_id(item["topic"])
            existing = self.data["topics"].get(tid)
            if not existing:
                self.data["topics"][tid] = {
                    "id": tid,
                    "topic": item["topic"],
                    "category": item.get("category", "generic"),
                    "status": "PENDING",
                    "attempts": 0,
                    "created_at": now(),
                    "updated_at": now(),
                    "image_path": None,
                    "instagram": {"status": "PENDING", "url": None, "error": None},
                    "linkedin": {"status": "PENDING", "url": None, "error": None},
                    "error": None,
                }

    def _needs_work(self, item: dict) -> bool:
        if item["status"] == "PUBLISHED":
            return False
        return True

    def next(self, limit: int) -> list[dict]:
        values = list(self.data["topics"].values())
        values.sort(key=lambda x: (x["created_at"], x["topic"].casefold()))
        return [x for x in values if self._needs_work(x)][:limit]

    def mark(self, tid: str, status: str, **updates):
        item = self.data["topics"][tid]
        item["status"] = status
        item["updated_at"] = now()
        if status == "PROCESSING":
            item["attempts"] = int(item.get("attempts", 0)) + 1
        item.update(updates)

    def mark_platform(self, tid: str, platform: str, status: str, url=None, error=None):
        self.data["topics"][tid][platform] = {
            "status": status,
            "url": url,
            "error": error,
        }
        item = self.data["topics"][tid]
        enabled = [
            item["instagram"]["status"] != "DISABLED",
            item["linkedin"]["status"] != "DISABLED",
        ]
        published = [
            item["instagram"]["status"] == "PUBLISHED",
            item["linkedin"]["status"] == "PUBLISHED",
        ]
        # The caller decides which platforms are enabled; this helper only updates state.
        item["updated_at"] = now()

    def set_last_run(self):
        self.data["last_run"] = now()
