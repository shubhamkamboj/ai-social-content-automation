from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time
import requests

from src.config import Config
from src.content.caption_generator import generate_captions
from src.content.content_builder import build_content
from src.content.topic_parser import read_topics
from src.infographic.generator import create_infographic
from src.platforms.instagram import InstagramPublisher
from src.platforms.linkedin import LinkedInPublisher
from src.state_manager import StateManager


def wait_for_public_url(url: str, retries: int = 10) -> bool:
    if not url:
        return False
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=20, stream=True)
            if r.ok:
                return True
        except requests.RequestException:
            pass
        time.sleep(4)
    return False


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    config = Config()
    dry_run = args.dry_run or config.dry_run
    limit = args.limit or config.post_limit

    topics = read_topics(config.topics_file)
    state = StateManager(config.state_file)
    state.sync(topics)
    selected = state.next(limit)

    print(f"Topics: {len(topics)} | Selected: {len(selected)} | Dry run: {dry_run}")

    ig = InstagramPublisher(
        config.instagram_access_token,
        config.instagram_account_id,
        config.instagram_graph_base_url,
    )
    li = LinkedInPublisher(
        config.linkedin_access_token,
        config.linkedin_author_urn,
        config.linkedin_version,
    )

    for item in selected:
        tid = item["id"]
        try:
            state.mark(tid, "PROCESSING")
            state.save()

            content = build_content(item)
            captions = generate_captions(content)

            image_path = Path(config.output_dir) / f"{tid}.png"
            create_infographic(item, str(image_path))

            state.mark(tid, "GENERATED", image_path=str(image_path), error=None)
            state.save()

            print(f"[GENERATED] {item['topic']} -> {image_path}")

            if dry_run:
                print(f"[DRY RUN] Instagram caption: {captions['instagram'][:120]}...")
                print(f"[DRY RUN] LinkedIn caption: {captions['linkedin'][:120]}...")
                continue

            if not config.public_base_url:
                raise RuntimeError("PUBLIC_BASE_URL is required for publishing.")

            image_url = f"{config.public_base_url.rstrip('/')}/{image_path.name}"

            if not wait_for_public_url(image_url):
                raise RuntimeError(f"Public image URL is not reachable yet: {image_url}")

            # Instagram
            if config.instagram_enabled:
                if state.data["topics"][tid]["instagram"]["status"] != "PUBLISHED":
                    result = ig.publish(str(image_path), image_url, captions["instagram"])
                    if result.success:
                        state.mark_platform(tid, "instagram", "PUBLISHED", result.url)
                    else:
                        state.mark_platform(tid, "instagram", "FAILED", None, result.message)
                        state.mark(tid, "FAILED", error=result.message)
                        state.save()
                        continue
            else:
                state.mark_platform(tid, "instagram", "DISABLED")

            # LinkedIn
            if config.linkedin_enabled:
                if state.data["topics"][tid]["linkedin"]["status"] != "PUBLISHED":
                    result = li.publish(str(image_path), image_url, captions["linkedin"])
                    if result.success:
                        state.mark_platform(tid, "linkedin", "PUBLISHED", result.url)
                    else:
                        state.mark_platform(tid, "linkedin", "FAILED", None, result.message)
                        state.mark(tid, "FAILED", error=result.message)
                        state.save()
                        continue
            else:
                state.mark_platform(tid, "linkedin", "DISABLED")

            ig_done = state.data["topics"][tid]["instagram"]["status"] in {"PUBLISHED", "DISABLED"}
            li_done = state.data["topics"][tid]["linkedin"]["status"] in {"PUBLISHED", "DISABLED"}

            if ig_done and li_done:
                state.mark(tid, "PUBLISHED", error=None)
                print(f"[PUBLISHED] {item['topic']}")
            else:
                state.mark(tid, "FAILED", error="One or more platforms are not complete.")

            state.save()

        except Exception as exc:
            state.mark(tid, "FAILED", error=str(exc))
            state.save()
            print(f"[FAILED] {item['topic']}: {exc}")

    state.set_last_run()
    state.save()


if __name__ == "__main__":
    main()
