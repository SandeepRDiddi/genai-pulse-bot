from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
import feedparser
from .utils import DocItem, clean_text, make_id, iso_to_ts

def _to_iso(dt_struct) -> Optional[str]:
    try:
        if not dt_struct:
            return None
        dt = datetime(*dt_struct[:6], tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00","Z")
    except Exception:
        return None

def fetch(url: str, max_items: int = 25) -> list[DocItem]:
    d = feedparser.parse(url)
    out: list[DocItem] = []
    for e in d.entries[:max_items]:
        link = getattr(e, "link", None) or getattr(e, "id", None) or ""
        title = (getattr(e, "title", "") or "").strip() or "(untitled)"
        summary = clean_text(getattr(e, "summary", "") or getattr(e, "description", ""))
        published_iso = _to_iso(getattr(e, "published_parsed", None) or getattr(e, "updated_parsed", None))
        out.append(DocItem(
            id=make_id(link, title),
            title=title,
            url=link,
            summary=summary,
            published_iso=published_iso,
            published_ts=iso_to_ts(published_iso),
            source=f"rss:{url}",
        ))
    return out
