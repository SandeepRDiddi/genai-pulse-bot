"""
Tech News scraper — fetches AI news from TechCrunch, Wired, VentureBeat via RSS feeds.
No API keys required — uses public RSS feeds.
"""

import feedparser
import hashlib
import logging
from datetime import datetime
from typing import List, Dict
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "MIT Tech Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
}

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning",
    "large language model", "llm", "chatgpt", "openai", "anthropic",
    "google deepmind", "generative ai", "gpt", "claude", "gemini",
    "stable diffusion", "midjourney", "ai model", "neural network",
]


def fetch_tech_news(max_results: int = 20) -> List[Dict]:
    """Fetch AI news from tech RSS feeds."""
    articles = []
    seen_ids = set()
    per_feed = max(2, max_results // len(RSS_FEEDS))

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            count = 0

            for entry in feed.entries:
                if count >= per_feed:
                    break

                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))

                # Filter for AI-relevant content
                combined = (title + " " + summary).lower()
                if not any(kw in combined for kw in AI_KEYWORDS):
                    continue

                # Generate stable ID
                article_id = hashlib.md5(entry.get("link", title).encode()).hexdigest()[:12]
                full_id = f"news_{article_id}"

                if full_id in seen_ids:
                    continue
                seen_ids.add(full_id)

                # Parse date
                published = _parse_date(entry)

                # Clean summary
                clean_summary = _clean_html(summary)[:500]
                if len(summary) > 500:
                    clean_summary += "..."

                articles.append({
                    "id": full_id,
                    "title": f"📰 {title}",
                    "summary": clean_summary,
                    "url": entry.get("link", ""),
                    "source": "technews",
                    "category": _categorize_news(title + " " + summary),
                    "published_at": published,
                    "authors": source_name,
                    "score": 0,
                })
                count += 1

        except Exception as e:
            logger.error(f"Error fetching RSS feed {source_name}: {e}")
            continue

    logger.info(f"✅ Tech News: fetched {len(articles)} articles")
    return articles[:max_results]


def _parse_date(entry) -> datetime:
    try:
        if hasattr(entry, "published"):
            return parsedate_to_datetime(entry.published).replace(tzinfo=None)
    except Exception:
        pass
    return datetime.utcnow()


def _clean_html(text: str) -> str:
    """Remove basic HTML tags from text."""
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _categorize_news(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["chatgpt", "gpt", "llm", "language model", "claude", "gemini"]):
        return "LLM"
    elif any(w in text_lower for w in ["image", "video", "diffusion", "sora", "midjourney"]):
        return "Vision"
    elif any(w in text_lower for w in ["regulation", "policy", "law", "safety", "ethics"]):
        return "AI Policy"
    elif any(w in text_lower for w in ["startup", "funding", "billion", "investment", "raises"]):
        return "AI Business"
    elif any(w in text_lower for w in ["open source", "open-source", "github"]):
        return "Open Source"
    return "General AI"
