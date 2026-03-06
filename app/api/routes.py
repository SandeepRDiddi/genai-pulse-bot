"""
FastAPI REST API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db, Article, Subscriber
from app.scrapers import run_all_scrapers
from app.notifiers import send_digest_to_all

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ArticleOut(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    url: str
    source: str
    category: Optional[str]
    published_at: datetime
    score: int
    authors: Optional[str]

    class Config:
        from_attributes = True


class SubscribeRequest(BaseModel):
    email: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    slack_webhook: Optional[str] = None
    frequency: str = "daily"


class StatsOut(BaseModel):
    total_articles: int
    by_source: dict
    by_category: dict
    last_fetch: Optional[datetime]


# ── Articles ──────────────────────────────────────────────────────────────────

@router.get("/articles", response_model=List[ArticleOut])
async def get_articles(
    source: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get latest articles with optional filtering."""
    since = datetime.utcnow() - timedelta(hours=hours)
    query = select(Article).where(Article.fetched_at >= since)

    if source:
        query = query.where(Article.source == source)
    if category:
        query = query.where(Article.category == category)

    query = query.order_by(desc(Article.score), desc(Article.published_at)).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/articles/{article_id}", response_model=ArticleOut)
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    total = await db.scalar(select(func.count(Article.id)))

    # By source
    source_result = await db.execute(
        select(Article.source, func.count(Article.id)).group_by(Article.source)
    )
    by_source = dict(source_result.all())

    # By category
    cat_result = await db.execute(
        select(Article.category, func.count(Article.id)).group_by(Article.category)
    )
    by_category = dict(cat_result.all())

    # Last fetch
    last = await db.scalar(select(func.max(Article.fetched_at)))

    return StatsOut(
        total_articles=total or 0,
        by_source=by_source,
        by_category=by_category,
        last_fetch=last,
    )


# ── Subscribers ───────────────────────────────────────────────────────────────

@router.post("/subscribe", status_code=201)
async def subscribe(req: SubscribeRequest, db: AsyncSession = Depends(get_db)):
    """Subscribe to digest notifications."""
    if not req.email and not req.telegram_chat_id and not req.slack_webhook:
        raise HTTPException(status_code=400, detail="Provide at least one contact method")

    subscriber = Subscriber(
        email=req.email,
        telegram_chat_id=req.telegram_chat_id,
        slack_webhook=req.slack_webhook,
        frequency=req.frequency,
    )
    db.add(subscriber)
    await db.commit()
    return {"message": "Subscribed successfully! 🎉"}


# ── Admin / Triggers ──────────────────────────────────────────────────────────

@router.post("/admin/fetch")
async def trigger_fetch(background_tasks: BackgroundTasks):
    """Manually trigger a fetch from all sources."""
    background_tasks.add_task(run_all_scrapers)
    return {"message": "Fetch started in background"}


@router.post("/admin/digest")
async def trigger_digest(background_tasks: BackgroundTasks):
    """Manually trigger sending the digest."""
    background_tasks.add_task(send_digest_to_all)
    return {"message": "Digest sending started in background"}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "GenAI Pulse Bot"}
