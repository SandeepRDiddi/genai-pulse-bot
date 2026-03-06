"""
Scraper orchestrator — runs all scrapers and saves results to DB.
"""

import logging
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.scrapers.arxiv_scraper import fetch_arxiv_papers
from app.scrapers.huggingface_scraper import fetch_huggingface_releases
from app.scrapers.reddit_scraper import fetch_reddit_posts
from app.scrapers.technews_scraper import fetch_tech_news
from app.database import Article, AsyncSessionLocal
from app.config import settings

logger = logging.getLogger(__name__)


async def run_all_scrapers() -> int:
    """Run all scrapers and persist new articles. Returns count of new articles."""
    logger.info("🔄 Running all scrapers...")

    all_articles = []
    all_articles.extend(fetch_arxiv_papers(settings.ARXIV_MAX_RESULTS))
    all_articles.extend(fetch_huggingface_releases(settings.HUGGINGFACE_MAX_RESULTS))
    all_articles.extend(fetch_reddit_posts(settings.REDDIT_MAX_RESULTS))
    all_articles.extend(fetch_tech_news())

    new_count = await _save_articles(all_articles)
    logger.info(f"✅ Scraping complete. {new_count} new articles saved.")
    return new_count


async def _save_articles(articles: List[Dict]) -> int:
    """Save new articles to the database, skip duplicates."""
    new_count = 0

    async with AsyncSessionLocal() as session:
        for article_data in articles:
            # Check if already exists
            existing = await session.get(Article, article_data["id"])
            if existing:
                continue

            article = Article(
                id=article_data["id"],
                title=article_data["title"],
                summary=article_data.get("summary", ""),
                url=article_data["url"],
                source=article_data["source"],
                category=article_data.get("category", "General AI"),
                published_at=article_data.get("published_at", datetime.utcnow()),
                fetched_at=datetime.utcnow(),
                score=article_data.get("score", 0),
                authors=article_data.get("authors", ""),
                is_notified=False,
            )
            session.add(article)
            new_count += 1

        await session.commit()

    return new_count
