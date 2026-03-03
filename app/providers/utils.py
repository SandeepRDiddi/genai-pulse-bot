from __future__ import annotations
import hashlib, re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

def clean_text(t: str) -> str:
    t = re.sub(r"<[^>]+>", " ", t or "")
    t = re.sub(r"\s+", " ", t).strip()
    return t

def make_id(url: str, title: str) -> str:
    raw = f"{url}::{title}".encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()

def iso_to_ts(iso: Optional[str]) -> int:
    if not iso:
        return 0
    try:
        return int(datetime.fromisoformat(iso.replace("Z","+00:00")).timestamp())
    except Exception:
        return 0

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@dataclass
class DocItem:
    id: str
    title: str
    url: str
    summary: str
    published_iso: Optional[str]
    published_ts: int
    source: str
    language: Optional[str] = None
    country: Optional[str] = None
