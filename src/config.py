from __future__ import annotations

import os
from dataclasses import dataclass


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    topics_file: str = os.getenv("TOPICS_FILE", "topics/topics.docx")
    state_file: str = os.getenv("STATE_FILE", "state.json")
    daily_limit: int = int(os.getenv("DAILY_POST_LIMIT", "4"))
    dry_run: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    github_owner: str = os.getenv("GITHUB_OWNER", "")
    github_repo: str = os.getenv("GITHUB_REPO", "")
    github_branch: str = os.getenv("GITHUB_BRANCH", "main")
    public_image_base_url: str = os.getenv("PUBLIC_IMAGE_BASE_URL", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6")
    openai_image_model: str = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    instagram_api_version: str = os.getenv("INSTAGRAM_API_VERSION", "v24.0")
    instagram_user_id: str = os.getenv("INSTAGRAM_USER_ID", "")
    linkedin_version: str = os.getenv("LINKEDIN_VERSION", "202601")
    linkedin_author_urn: str = os.getenv("LINKEDIN_AUTHOR_URN", "")


settings = Settings()
