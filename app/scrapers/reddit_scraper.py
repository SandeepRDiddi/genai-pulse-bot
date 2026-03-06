"""
Reddit scraper — fetches hot posts from AI/ML subreddits.
Uses PRAW (Python Reddit API Wrapper).
Falls back to public JSON API if no credentials provided.
"""

import requests
import logging
from datetime import datetime
from typing import List, Dict
from app.config import settings

logger = logging.getLogger(__name__)

SUBREDDITS = [
    "MachineLearning",
    "artificial",
    "LocalLLaMA",
    "singularity",
    "OpenAI",
]


def fetch_reddit_posts(max_results: int = 25) -> List[Dict]:
    """Fetch hot posts from AI subreddits using public JSON API."""
    articles = []
    per_sub = max(1, max_results // len(SUBREDDITS))

    for subreddit in SUBREDDITS:
        posts = _fetch_subreddit(subreddit, per_sub)
        articles.extend(posts)

    # Sort by score descending
    articles.sort(key=lambda x: x["score"], reverse=True)

    logger.info(f"✅ Reddit: fetched {len(articles)} posts")
    return articles[:max_results]


def _fetch_subreddit(subreddit: str, limit: int = 5) -> List[Dict]:
    """Fetch posts from a single subreddit using the public JSON API."""
    try:
        headers = {"User-Agent": settings.REDDIT_USER_AGENT}
        response = requests.get(
            f"https://www.reddit.com/r/{subreddit}/hot.json",
            params={"limit": limit},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        articles = []
        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})

            # Skip stickied/pinned posts
            if p.get("stickied") or p.get("pinned"):
                continue

            # Skip posts with very low scores
            if p.get("score", 0) < 10:
                continue

            post_id = p.get("id", "")
            articles.append({
                "id": f"reddit_{post_id}",
                "title": f"💬 r/{subreddit}: {p.get('title', 'Unknown')}",
                "summary": p.get("selftext", "")[:400] + "..." if len(p.get("selftext", "")) > 400
                          else p.get("selftext", f"Trending post on r/{subreddit} with {p.get('score', 0):,} upvotes."),
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "source": "reddit",
                "category": _categorize_reddit_post(p.get("title", "") + " " + p.get("selftext", "")),
                "published_at": datetime.fromtimestamp(p.get("created_utc", 0)),
                "authors": p.get("author", "unknown"),
                "score": p.get("score", 0),
            })

        return articles

    except Exception as e:
        logger.error(f"Error fetching r/{subreddit}: {e}")
        return []


def _categorize_reddit_post(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["gpt", "llm", "language model", "chatgpt", "claude", "gemini"]):
        return "LLM"
    elif any(w in text_lower for w in ["image", "stable diffusion", "midjourney", "dall-e"]):
        return "Vision"
    elif any(w in text_lower for w in ["open source", "local", "ollama", "llama"]):
        return "Open Source"
    elif any(w in text_lower for w in ["paper", "research", "study"]):
        return "Research"
    return "General AI"
