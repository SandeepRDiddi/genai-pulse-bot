"""
HuggingFace scraper — fetches trending models and latest Space releases.
Uses the public HuggingFace Hub API (no auth required for public data).
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

HF_API_BASE = "https://huggingface.co/api"


def fetch_huggingface_releases(max_results: int = 20) -> List[Dict]:
    """Fetch trending models and latest datasets from HuggingFace Hub."""
    articles = []

    # Fetch trending models
    articles.extend(_fetch_trending_models(max_results // 2))

    # Fetch latest papers from HF Daily Papers
    articles.extend(_fetch_hf_daily_papers(max_results // 2))

    logger.info(f"✅ HuggingFace: fetched {len(articles)} items")
    return articles


def _fetch_trending_models(limit: int = 10) -> List[Dict]:
    """Fetch trending models from HuggingFace Hub."""
    try:
        response = requests.get(
            f"{HF_API_BASE}/models",
            params={
                "sort": "trending",
                "limit": limit,
                "full": False,
            },
            timeout=10,
        )
        response.raise_for_status()
        models = response.json()

        articles = []
        for model in models:
            model_id = model.get("id", "")
            articles.append({
                "id": f"hf_model_{model_id.replace('/', '_')}",
                "title": f"🤗 Trending Model: {model_id}",
                "summary": f"New trending model on HuggingFace Hub. Tags: {', '.join(model.get('tags', [])[:5])}. "
                           f"Downloads: {model.get('downloads', 0):,}. Likes: {model.get('likes', 0):,}.",
                "url": f"https://huggingface.co/{model_id}",
                "source": "huggingface",
                "category": _categorize_hf_model(model.get("tags", [])),
                "published_at": datetime.utcnow(),
                "authors": model_id.split("/")[0] if "/" in model_id else "Unknown",
                "score": model.get("likes", 0),
            })
        return articles

    except Exception as e:
        logger.error(f"Error fetching HF trending models: {e}")
        return []


def _fetch_hf_daily_papers(limit: int = 10) -> List[Dict]:
    """Fetch HuggingFace Daily Papers."""
    try:
        response = requests.get(
            "https://huggingface.co/api/daily_papers",
            params={"limit": limit},
            timeout=10,
        )
        response.raise_for_status()
        papers = response.json()

        articles = []
        for paper in papers:
            paper_id = paper.get("paper", {}).get("id", "")
            title = paper.get("paper", {}).get("title", "Unknown Paper")
            summary = paper.get("paper", {}).get("summary", "")

            articles.append({
                "id": f"hf_paper_{paper_id}",
                "title": f"📄 HF Daily: {title}",
                "summary": summary[:500] + "..." if len(summary) > 500 else summary,
                "url": f"https://huggingface.co/papers/{paper_id}",
                "source": "huggingface",
                "category": "Research",
                "published_at": datetime.utcnow(),
                "authors": ", ".join([a.get("name", "") for a in paper.get("paper", {}).get("authors", [])[:3]]),
                "score": paper.get("paper", {}).get("upvotes", 0),
            })
        return articles

    except Exception as e:
        logger.error(f"Error fetching HF daily papers: {e}")
        return []


def _categorize_hf_model(tags: List[str]) -> str:
    tags_lower = [t.lower() for t in tags]
    if any(t in tags_lower for t in ["text-generation", "llm", "causal-lm"]):
        return "LLM"
    elif any(t in tags_lower for t in ["image-generation", "text-to-image", "diffusion"]):
        return "Vision"
    elif any(t in tags_lower for t in ["audio", "speech", "text-to-speech"]):
        return "Audio"
    elif any(t in tags_lower for t in ["multimodal", "image-text-to-text"]):
        return "Multimodal"
    return "General AI"
