from __future__ import annotations
import argparse
import asyncio
from .config import settings
from .embeddings import embed_texts, vector_size
from .vectorstore import get_client, ensure_collection, upsert_points
from .providers import rss as rss_provider
from .providers import gdelt as gdelt_provider
from .providers import mediacloud as mc_provider
from .providers.utils import now_iso

def _upsert(items):
    if not items:
        return 0
    client = get_client(settings.qdrant_url)
    ensure_collection(client, settings.qdrant_collection, vector_size(settings.embed_model))

    texts = [f"{it.title}\n\n{it.summary}" for it in items]
    vectors = embed_texts(settings.embed_model, texts)
    ids = [it.id for it in items]
    payloads = [{
        "title": it.title,
        "url": it.url,
        "summary": it.summary,
        "published_iso": it.published_iso,
        "published_ts": it.published_ts,
        "source": it.source,
        "language": it.language,
        "country": it.country,
        "ingested_at": now_iso(),
    } for it in items]

    upsert_points(client, settings.qdrant_collection, ids, vectors, payloads)
    return len(items)

async def run_once_async() -> int:
    total = 0

    # GDELT
    if settings.enable_gdelt:
        try:
            items = await gdelt_provider.fetch(
                base_url=settings.gdelt_base_url,
                query=settings.global_query,
                maxrecords=settings.gdelt_maxrecords,
                mode=settings.gdelt_mode,
                fmt=settings.gdelt_format,
            )
            total += _upsert(items)
            print(f"Ingested {len(items)} items from GDELT")
        except Exception as e:
            print(f"[WARN] GDELT failed: {e}")

    # Media Cloud
    if settings.enable_mediacloud:
        try:
            items = await mc_provider.fetch(
                base_url=settings.mediacloud_base_url,
                api_key=settings.mediacloud_api_key,
                global_query=settings.global_query,
                rows=settings.mediacloud_rows,
            )
            total += _upsert(items)
            print(f"Ingested {len(items)} items from Media Cloud")
        except Exception as e:
            print(f"[WARN] MediaCloud failed: {e}")

    # RSS
    if settings.enable_rss and settings.rss_feeds:
        for feed_url in settings.rss_feeds:
            try:
                items = rss_provider.fetch(feed_url, max_items=settings.max_items_per_feed)
                total += _upsert(items)
                print(f"Ingested {len(items)} items from RSS {feed_url}")
            except Exception as e:
                print(f"[WARN] RSS failed: {feed_url} :: {e}")

    print(f"Done. Upserted ~{total} items (may include updates).")
    return total

def run_once() -> int:
    return asyncio.run(run_once_async())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single ingestion cycle")
    args = parser.parse_args()
    if args.once:
        run_once()
    else:
        run_once()

if __name__ == "__main__":
    main()
