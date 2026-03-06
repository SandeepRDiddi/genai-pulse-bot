"""
Arxiv scraper — fetches latest AI/ML papers from Arxiv API.
Searches across cs.AI, cs.LG, cs.CL, cs.CV, cs.NE categories.
"""

import arxiv
import hashlib
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

SEARCH_QUERIES = [
    "large language model",
    "generative AI",
    "diffusion model",
    "transformer",
    "multimodal",
    "RLHF reinforcement learning human feedback",
]

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]


def fetch_arxiv_papers(max_results: int = 20) -> List[Dict]:
    """Fetch latest AI papers from Arxiv."""
    articles = []
    seen_ids = set()

    client = arxiv.Client()

    for query in SEARCH_QUERIES[:3]:  # limit queries to avoid rate limiting
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results // 3,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            for result in client.results(search):
                paper_id = result.entry_id.split("/")[-1]
                if paper_id in seen_ids:
                    continue
                seen_ids.add(paper_id)

                # Categorize the paper
                category = categorize_paper(result.title + " " + result.summary)

                articles.append({
                    "id": f"arxiv_{paper_id}",
                    "title": result.title,
                    "summary": result.summary[:500] + "..." if len(result.summary) > 500 else result.summary,
                    "url": result.entry_id,
                    "source": "arxiv",
                    "category": category,
                    "published_at": result.published,
                    "authors": ", ".join([a.name for a in result.authors[:3]]),
                    "score": 0,
                })

        except Exception as e:
            logger.error(f"Error fetching Arxiv papers for query '{query}': {e}")
            continue

    logger.info(f"✅ Arxiv: fetched {len(articles)} papers")
    return articles


def categorize_paper(text: str) -> str:
    """Simple keyword-based categorization."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["language model", "llm", "gpt", "bert", "text"]):
        return "LLM"
    elif any(w in text_lower for w in ["diffusion", "image generation", "vision", "visual"]):
        return "Vision"
    elif any(w in text_lower for w in ["audio", "speech", "voice", "sound"]):
        return "Audio"
    elif any(w in text_lower for w in ["reinforcement", "rlhf", "reward"]):
        return "RL"
    elif any(w in text_lower for w in ["multimodal", "multi-modal"]):
        return "Multimodal"
    return "General AI"
