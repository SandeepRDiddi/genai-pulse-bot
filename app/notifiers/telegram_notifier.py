"""
Telegram notifier — sends GenAI updates to a Telegram channel or group.
Requires: TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID in .env
"""

import httpx
import logging
from typing import List, Dict

from app.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


async def send_telegram_digest(articles: List[Dict]) -> bool:
    """Send a digest of top articles to the Telegram channel."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHANNEL_ID:
        logger.warning("Telegram not configured — skipping")
        return False

    message = _format_digest(articles)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN, method="sendMessage"),
                json={
                    "chat_id": settings.TELEGRAM_CHANNEL_ID,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.info("✅ Telegram digest sent")
            return True

    except Exception as e:
        logger.error(f"❌ Telegram send failed: {e}")
        return False


async def send_telegram_alert(article: Dict) -> bool:
    """Send a single high-priority article alert."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHANNEL_ID:
        return False

    source_emoji = {"arxiv": "📄", "huggingface": "🤗", "reddit": "💬", "technews": "📰"}.get(
        article.get("source", ""), "🔔"
    )

    message = (
        f"{source_emoji} <b>{article['title']}</b>\n\n"
        f"{article.get('summary', '')[:300]}...\n\n"
        f"🔗 <a href='{article['url']}'>Read more</a>"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN, method="sendMessage"),
                json={
                    "chat_id": settings.TELEGRAM_CHANNEL_ID,
                    "text": message,
                    "parse_mode": "HTML",
                },
                timeout=10,
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"❌ Telegram alert failed: {e}")
        return False


def _format_digest(articles: List[Dict]) -> str:
    """Format articles into a Telegram-friendly digest."""
    lines = ["🤖 <b>GenAI Pulse — Daily Digest</b>\n"]

    source_groups = {}
    for a in articles:
        source_groups.setdefault(a["source"], []).append(a)

    source_names = {
        "arxiv": "📄 Arxiv Papers",
        "huggingface": "🤗 HuggingFace",
        "reddit": "💬 Reddit",
        "technews": "📰 Tech News",
    }

    for source, name in source_names.items():
        items = source_groups.get(source, [])[:3]
        if not items:
            continue
        lines.append(f"\n<b>{name}</b>")
        for article in items:
            lines.append(f"• <a href='{article['url']}'>{article['title'][:80]}</a>")

    lines.append("\n\n🔗 View full dashboard: your-deployed-url.com")
    return "\n".join(lines)
