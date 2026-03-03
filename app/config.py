from __future__ import annotations
import json, os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _get(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return v

def _get_int(name: str, default: str) -> int:
    return int(_get(name, default))

def _get_bool(name: str, default: str = "0") -> bool:
    return _get(name, default).strip() not in ("0", "false", "False", "")

@dataclass(frozen=True)
class Settings:
    app_name: str = _get("APP_NAME", "GenAI Global Trends Bot")

    qdrant_url: str = _get("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = _get("QDRANT_COLLECTION", "genai_global")

    embed_model: str = _get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    llm_base_url: str = _get("LLM_BASE_URL", "http://localhost:11434/v1")
    llm_api_key: str = _get("LLM_API_KEY", "ollama")
    llm_model: str = _get("LLM_MODEL", "llama3.1")

    top_k: int = _get_int("TOP_K", "8")

    enable_gdelt: bool = _get_bool("ENABLE_GDELT", "1")
    enable_mediacloud: bool = _get_bool("ENABLE_MEDIACLOUD", "1")
    enable_rss: bool = _get_bool("ENABLE_RSS", "1")

    global_query: str = _get("GLOBAL_QUERY", "generative ai OR genai OR llm")

    gdelt_base_url: str = _get("GDELT_BASE_URL", "https://api.gdeltproject.org/api/v2/doc/doc")
    gdelt_mode: str = _get("GDELT_MODE", "ArtList")
    gdelt_format: str = _get("GDELT_FORMAT", "json")
    gdelt_maxrecords: int = _get_int("GDELT_MAXRECORDS", "75")

    mediacloud_base_url: str = _get("MEDIACLOUD_BASE_URL", "https://api.mediacloud.org/api/v2")
    mediacloud_api_key: str = _get("MEDIACLOUD_API_KEY", "")
    mediacloud_rows: int = _get_int("MEDIACLOUD_ROWS", "50")

    rss_feeds: list[str] = json.loads(_get("RSS_FEEDS_JSON", "[]"))
    max_items_per_feed: int = _get_int("MAX_ITEMS_PER_FEED", "25")

settings = Settings()
