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

async def fetch(base_url: str, query: str, maxrecords: int = 50, mode: str = "ArtList", fmt: str = "json") -> list[DocItem]:
    params = {
        "query": query,
        "mode": mode,
        "format": fmt,
        "maxrecords": str(maxrecords),
        "sort": "HybridRel",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(base_url, params=params)
        r.raise_for_status()
        data: dict[str, Any] = r.json()

    articles = data.get("articles") or []
    out: list[DocItem] = []
    for a in articles:
        url = a.get("url") or ""
        title = (a.get("title") or "").strip() or "(untitled)"
        # GDELT sometimes provides 'seendate' or 'datetime'
        published_iso = _parse_iso(a.get("seendate") or a.get("datetime") or a.get("sourceCollectionDate"))
        summary = clean_text(a.get("snippet") or a.get("summary") or "")
        out.append(DocItem(
            id=make_id(url, title),
            title=title,
            url=url,
            summary=summary,
            published_iso=published_iso,
            published_ts=iso_to_ts(published_iso),
            source="gdelt",
            language=a.get("language"),
            country=a.get("sourceCountry") or a.get("sourcecountry"),
        ))
    return out
