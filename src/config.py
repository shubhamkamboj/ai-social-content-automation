from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Config:
    topics_file: str = os.getenv("TOPICS_FILE", "topics/topics.docx")
    state_file: str = os.getenv("STATE_FILE", "state.json")
    output_dir: str = os.getenv("OUTPUT_DIR", "generated")
    post_limit: int = int(os.getenv("POST_LIMIT", "4"))
    dry_run: bool = env_bool("DRY_RUN", True)

    instagram_enabled: bool = env_bool("INSTAGRAM_ENABLED", False)
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_account_id: str = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    instagram_graph_base_url: str = os.getenv("INSTAGRAM_GRAPH_BASE_URL", "")

    linkedin_enabled: bool = env_bool("LINKEDIN_ENABLED", False)
    linkedin_access_token: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    linkedin_author_urn: str = os.getenv("LINKEDIN_AUTHOR_URN", "")
    linkedin_version: str = os.getenv("LINKEDIN_VERSION", "202606")

    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "")
