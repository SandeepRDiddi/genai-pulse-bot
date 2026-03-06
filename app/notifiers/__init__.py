"""
Notifier orchestrator — sends digests across all configured channels.
"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy import select

from app.database import AsyncSessionLocal, Article
from app.notifiers.telegram_notifier import send_telegram_digest
from app.notifiers.slack_notifier import send_slack_digest
from app.notifiers.email_notifier import send_email_digest

logger = logging.getLogger(__name__)


async def send_digest_to_all() -> Dict:
    """Fetch latest articles and send to all configured channels."""
    articles = await _get_recent_articles(hours=24)

    if not articles:
        logger.info("No new articles to send in digest")
        return {"status": "skipped", "reason": "no new articles"}

    results = {}
    results["telegram"] = await send_telegram_digest(articles)
    results["slack"] = await send_slack_digest(articles)
    results["email"] = await send_email_digest(articles)

    # Mark articles as notified
    await _mark_as_notified([a["id"] for a in articles])

    logger.info(f"✅ Digest sent: {results}")
    return {"status": "success", "channels": results, "article_count": len(articles)}


async def send_alert(article_id: str) -> bool:
    """Send immediate alert for a single article."""
    async with AsyncSessionLocal() as session:
        article = await session.get(Article, article_id)
        if not article:
            return False

    article_dict = {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "url": article.url,
        "source": article.source,
    }

    from app.notifiers.telegram_notifier import send_telegram_alert
    return await send_telegram_alert(article_dict)


async def _get_recent_articles(hours: int = 24) -> List[Dict]:
    """Get articles from the last N hours, ordered by score."""
    since = datetime.utcnow() - timedelta(hours=hours)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Article)
            .where(Article.fetched_at >= since)
            .order_by(Article.score.desc(), Article.published_at.desc())
            .limit(20)
        )
        articles = result.scalars().all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "summary": a.summary,
            "url": a.url,
            "source": a.source,
            "category": a.category,
            "score": a.score,
        }
        for a in articles
    ]


async def _mark_as_notified(article_ids: List[str]):
    async with AsyncSessionLocal() as session:
        for article_id in article_ids:
            article = await session.get(Article, article_id)
            if article:
                article.is_notified = True
        await session.commit()
