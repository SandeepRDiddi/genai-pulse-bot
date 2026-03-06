"""
Slack notifier — sends GenAI updates to a Slack channel using Block Kit.
Requires: SLACK_BOT_TOKEN in .env
"""

import httpx
import logging
from typing import List, Dict

from app.config import settings

logger = logging.getLogger(__name__)


async def send_slack_digest(articles: List[Dict]) -> bool:
    """Send a rich Slack digest using Block Kit."""
    if not settings.SLACK_BOT_TOKEN:
        logger.warning("Slack not configured — skipping")
        return False

    blocks = _build_blocks(articles)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
                json={
                    "channel": settings.SLACK_CHANNEL,
                    "text": "🤖 GenAI Pulse — Daily Digest",
                    "blocks": blocks,
                },
                timeout=10,
            )
            data = response.json()
            if not data.get("ok"):
                logger.error(f"Slack API error: {data.get('error')}")
                return False

            logger.info("✅ Slack digest sent")
            return True

    except Exception as e:
        logger.error(f"❌ Slack send failed: {e}")
        return False


def _build_blocks(articles: List[Dict]) -> List[Dict]:
    """Build Slack Block Kit message blocks."""
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🤖 GenAI Pulse — Daily Digest", "emoji": True},
        },
        {"type": "divider"},
    ]

    source_groups = {}
    for a in articles:
        source_groups.setdefault(a["source"], []).append(a)

    source_config = {
        "arxiv": ("📄", "Arxiv Papers"),
        "huggingface": ("🤗", "HuggingFace"),
        "reddit": ("💬", "Reddit Trending"),
        "technews": ("📰", "Tech News"),
    }

    for source, (emoji, name) in source_config.items():
        items = source_groups.get(source, [])[:3]
        if not items:
            continue

        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{emoji} {name}*"},
        })

        for article in items:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• <{article['url']}|{article['title'][:100]}>\n  _{article.get('summary', '')[:150]}..._",
                },
            })

        blocks.append({"type": "divider"})

    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": "🔗 <your-deployed-url.com|View full dashboard> • GenAI Pulse Bot"}
        ],
    })

    return blocks
