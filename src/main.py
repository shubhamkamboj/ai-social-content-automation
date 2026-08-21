from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests

from src.config import Config
from src.content.caption_generator import generate_captions
from src.content.content_builder import build_content
from src.content.topic_parser import read_topics
from src.infographic.generator import create_infographic
from src.infographic.reel_generator import generate_reel
from src.platforms.instagram import InstagramPublisher
from src.state_manager import StateManager


def wait_for_public_url(url: str, retries: int = 18) -> bool:
    if not url:
        return False

    for _ in range(retries):
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=20,
            )

            if response.ok:
                return True

            # Some static hosts reject HEAD, so fall back to a tiny GET.
            response = requests.get(
                url,
                headers={"Range": "bytes=0-1023"},
                stream=True,
                timeout=20,
            )

            if response.ok:
                response.close()
                return True

        except requests.RequestException:
            pass

        import time
        time.sleep(5)

    return False


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = Config()

    dry_run = args.dry_run or config.dry_run
    limit = args.limit or config.post_limit

    topics = read_topics(config.topics_file)

    if not topics:
        raise RuntimeError(
            f"No topics found in {config.topics_file}"
        )

    state = StateManager(config.state_file)

    # Word document is the single source of truth.
    state.sync(topics)

    selected = state.next(limit)

    print(
        f"Topics in DOCX: {len(topics)} | "
        f"Selected: {len(selected)} | "
        f"Dry run: {dry_run}"
    )

    instagram = InstagramPublisher(
        config.instagram_access_token,
        config.instagram_account_id,
        config.instagram_graph_base_url,
        getattr(config, "instagram_api_version", "v25.0"),
    )

    for item in selected:
        tid = item["id"]

        try:
            state.mark(tid, "PROCESSING")
            state.save()

            content = build_content(item)
            captions = generate_captions(content)

            # 1. Generate infographic as an intermediate local asset.
            image_path = Path(config.output_dir) / f"{tid}.png"
            create_infographic(item, str(image_path))

            # 2. Convert infographic into an actual MP4 Reel.
            video_path = Path(config.output_dir) / f"{tid}.mp4"
            generate_reel(
                str(image_path),
                str(video_path),
                duration=8,
            )

            state.mark(
                tid,
                "GENERATED",
                image_path=str(image_path),
                video_path=str(video_path),
                error=None,
            )
            state.save()

            print(f"[GENERATED] {item['topic']}")
            print(f"  Image: {image_path}")
            print(f"  Reel : {video_path}")

            if dry_run:
                print("[DRY RUN] No Instagram post will be created.")
                continue

            if not config.instagram_enabled:
                raise RuntimeError(
                    "INSTAGRAM_ENABLED is false."
                )

            if not config.public_base_url:
                raise RuntimeError(
                    "PUBLIC_BASE_URL is required for Reel publishing."
                )

            # Only the MP4 is published. PNG is never sent to Instagram.
            video_url = (
                f"{config.public_base_url.rstrip('/')}/{video_path.name}"
            )

            print(f"[PUBLIC VIDEO] {video_url}")

            if not wait_for_public_url(video_url):
                raise RuntimeError(
                    f"Public Reel video URL is not reachable: {video_url}"
                )

            result = instagram.publish_reel(
                video_url,
                captions["instagram"],
            )

            if not result.success:
                raise RuntimeError(result.message)

            state.mark_platform(
                tid,
                "instagram",
                "PUBLISHED",
                result.url,
                None,
            )

            # LinkedIn remains independent for now.
            state.mark_platform(
                tid,
                "linkedin",
                "DISABLED",
                None,
                None,
            )

            state.mark(
                tid,
                "PUBLISHED",
                error=None,
            )
            state.save()

            print(f"[PUBLISHED REEL] {item['topic']} -> {result.url}")

        except Exception as exc:
            state.mark(
                tid,
                "FAILED",
                error=str(exc),
            )
            state.save()
            print(f"[FAILED] {item['topic']}: {exc}")

    state.set_last_run()
    state.save()


if __name__ == "__main__":
    main()
