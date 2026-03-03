from __future__ import annotations
from typing import Any
from .config import settings
from .embeddings import embed_texts, vector_size
from .vectorstore import get_client, ensure_collection, search as qsearch

def retrieve(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    k = top_k or settings.top_k
    client = get_client(settings.qdrant_url)
    ensure_collection(client, settings.qdrant_collection, vector_size(settings.embed_model))

    qvec = embed_texts(settings.embed_model, [query])[0]
    hits = qsearch(client, settings.qdrant_collection, qvec, limit=k)

    results: list[dict[str, Any]] = []
    for h in hits:
        p = h.payload or {}
        results.append({
            "title": p.get("title",""),
            "url": p.get("url",""),
            "summary": p.get("summary",""),
            "published": p.get("published_iso"),
            "published_ts": p.get("published_ts", 0),
            "source": p.get("source"),
            "score": float(h.score or 0.0),
        })

    # Prefer newer when scores are close
    results.sort(key=lambda x: (round(x["score"], 3), x["published_ts"]), reverse=True)
    return results
