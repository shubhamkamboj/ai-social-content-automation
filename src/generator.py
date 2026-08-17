from __future__ import annotations

import json
from pathlib import Path

from ai_content import generate_copy, generate_image
from topic_manager import pick_next, load_state, save_state, read_topics, sync_topics
from config import settings
from main import safe_filename

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
CONTENT = ROOT / "content"


def main() -> None:
    state = load_state(settings.state_file)
    topics = read_topics(settings.topics_file)
    sync_topics(topics, state)

    selected = pick_next(state, settings.daily_limit)
    if not selected:
        print("No PENDING topics found.")
        save_state(settings.state_file, state)
        return

    GENERATED.mkdir(exist_ok=True)
    CONTENT.mkdir(exist_ok=True)

    for item in selected:
        try:
            copy = generate_copy(item.topic)
            image_name = safe_filename(item.topic)
            image_path = GENERATED / image_name
            content_path = CONTENT / f"{item.topic_id}.json"
            if settings.dry_run:
                image_path.write_bytes(b"DRY_RUN_PLACEHOLDER")
            else:
                generate_image(item.topic, str(image_path))

            content_path.write_text(
                json.dumps({"topic_id": item.topic_id, "topic": item.topic, **copy}, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            item.image_file = f"generated/{image_name}"
            item.content_file = f"content/{content_path.name}"
            item.instagram_status = "PENDING"
            item.linkedin_status = "PENDING"
            print(f"Prepared: {item.topic}")
        except Exception as exc:
            item.status = "FAILED"
            item.last_error = str(exc)
            print(f"FAILED generating {item.topic}: {exc}")

    save_state(settings.state_file, state)

    if any(item.status == "FAILED" for item in selected):
        raise SystemExit("One or more topics failed during generation")


if __name__ == "__main__":
    main()
