from __future__ import annotations
from .config import settings
from .retrieval import retrieve
from .llm import chat_completion

PERSONA_PROMPTS = {
    "leadership": (
        "Create a 5-minute Leadership Brief on the latest GenAI trends. "
        "Structure: (1) Top shifts, (2) Why it matters, (3) Risks/controls, (4) Recommended actions this week. "
        "Be crisp. Use citations [1].."
    ),
    "business": (
        "Create a Business Brief on the latest GenAI trends. "
        "Structure: (1) High-value use cases, (2) Value levers/ROI signals, (3) Adoption patterns, (4) Vendor/stack notes, (5) Risks & governance. "
        "Use citations [1].."
    ),
    "tech": (
        "Create a Technical Brief on the latest GenAI trends. "
        "Structure: (1) Architectures/patterns, (2) Tooling/OSS, (3) Evals/benchmarks, (4) Deployment gotchas, (5) What to prototype next. "
        "Use citations [1].."
    ),
}

async def generate_briefing(persona: str, query_override: str | None = None, top_k: int | None = None):
    seed_query = query_override or settings.global_query
    hits = retrieve(seed_query, top_k=top_k or settings.top_k)

    context_blocks = []
    sources = []
    for i, h in enumerate(hits, start=1):
        context_blocks.append(
            f"[{i}] Title: {h['title']}\nURL: {h['url']}\nSource: {h.get('source') or ''}\nPublished: {h.get('published') or 'unknown'}\nSummary: {h['summary']}"
        )
        sources.append({"title": h["title"], "url": h["url"], "published": h.get("published"), "source": h.get("source")})

    prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["leadership"])
    briefing = await chat_completion(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        user_text=prompt,
        context_blocks=context_blocks,
    )
    return briefing, sources
