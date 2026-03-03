from __future__ import annotations
from typing import Any
import httpx
from dateutil import parser as dtparser
from .utils import DocItem, clean_text, make_id, iso_to_ts

def _parse_iso(s: str | None) -> str | None:
    if not s:
        return None
    try:
        return dtparser.parse(s).astimezone(dtparser.tz.UTC).isoformat().replace("+00:00","Z")
    except Exception:
        return None

def _safe_text_query(global_query: str) -> str:
    # MediaCloud uses a Solr-ish query. Keep it simple and safe:
    # convert common boolean tokens to a "text:" query.
    # Example output: text:("generative ai" OR genai OR llm)
    g = " ".join(global_query.strip().split())
    return f'text:({g})'

async def fetch(base_url: str, api_key: str, global_query: str, rows: int = 50) -> list[DocItem]:
    if not api_key:
        return []

    # docs show stories_public/list supports paging and q=... plus key=...
    url = base_url.rstrip("/") + "/stories_public/list"
    params = {
        "key": api_key,
        "q": _safe_text_query(global_query),
        "rows": str(rows),
        "sort": "processed_stories_id desc",
        "all_fields": "0",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data: Any = r.json()

    out: list[DocItem] = []
    # API returns list of story objects
    if isinstance(data, dict) and "stories" in data:
        stories = data["stories"]
    else:
        stories = data if isinstance(data, list) else []

    for s in stories:
        link = s.get("url") or s.get("guid") or ""
        title = (s.get("title") or "").strip() or "(untitled)"
        published_iso = _parse_iso(s.get("publish_date") or s.get("publication_date") or s.get("processed_date"))
        summary = clean_text(s.get("description") or s.get("text") or s.get("excerpt") or "")
        out.append(DocItem(
            id=make_id(link, title),
            title=title,
            url=link,
            summary=summary,
            published_iso=published_iso,
            published_ts=iso_to_ts(published_iso),
            source="mediacloud",
            language=s.get("language"),
            country=s.get("country"),
        ))
    return out
