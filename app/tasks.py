"""
Celery task queue for scheduled scraping and notifications.
"""

from celery import Celery
from celery.schedules import crontab
import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "genai_pulse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # Fetch new content every 6 hours
        "fetch-all-sources": {
            "task": "app.tasks.fetch_all_sources",
            "schedule": crontab(minute=0, hour="*/6"),
        },
        # Send daily digest at 9am UTC
        "send-daily-digest": {
            "task": "app.tasks.send_daily_digest",
            "schedule": crontab(minute=0, hour=9),
        },
    },
)


def run_async(coro):
    """Helper to run async functions in Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.fetch_all_sources", bind=True, max_retries=3)
def fetch_all_sources(self):
    """Fetch latest AI content from all sources."""
    try:
        from app.scrapers import run_all_scrapers
        new_count = run_async(run_all_scrapers())
        logger.info(f"✅ Fetched {new_count} new articles")
        return {"status": "success", "new_articles": new_count}
    except Exception as exc:
        logger.error(f"❌ Fetch failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * 5)


@celery_app.task(name="app.tasks.send_daily_digest", bind=True, max_retries=2)
def send_daily_digest(self):
    """Send daily digest to all active subscribers."""
    try:
        from app.notifiers import send_digest_to_all
        result = run_async(send_digest_to_all())
        return result
    except Exception as exc:
        logger.error(f"❌ Digest failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * 10)


@celery_app.task(name="app.tasks.send_immediate_alert")
def send_immediate_alert(article_id: str):
    """Send immediate alert for a high-importance article."""
    from app.notifiers import send_alert
    run_async(send_alert(article_id))
