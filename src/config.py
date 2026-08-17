from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1","true","yes","y","on"}

@dataclass(frozen=True)
class Config:
    topics_file: str = os.getenv("TOPICS_FILE", "topics/topics.docx")
    state_file: str = os.getenv("STATE_FILE", "state.json")
    output_dir: str = os.getenv("OUTPUT_DIR", "generated")
    post_limit: int = int(os.getenv("POST_LIMIT", "4"))
    dry_run: bool = _bool("DRY_RUN", True)
    instagram_enabled: bool = _bool("INSTAGRAM_ENABLED", False)
    linkedin_enabled: bool = _bool("LINKEDIN_ENABLED", False)
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_account_id: str = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    linkedin_access_token: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    linkedin_author_id: str = os.getenv("LINKEDIN_AUTHOR_ID", "")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "")
