from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .schemas import ChatRequest, ChatResponse, Source, BriefingResponse
from .retrieval import retrieve
from .llm import chat_completion
from .briefing import generate_briefing

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    hits = retrieve(req.query, top_k=req.top_k)

    context_blocks = []
    sources = []
    for i, h in enumerate(hits, start=1):
        context_blocks.append(
            f"[{i}] Title: {h['title']}\nURL: {h['url']}\nSource: {h.get('source') or ''}\nPublished: {h.get('published') or 'unknown'}\nSummary: {h['summary']}"
        )
        sources.append(Source(title=h["title"], url=h["url"], published=h.get("published"), source=h.get("source")))

    answer = await chat_completion(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        user_text=f"Question:\n{req.query}",
        context_blocks=context_blocks,
    )
    return ChatResponse(answer=answer, sources=sources)

@app.get("/briefing/{persona}", response_model=BriefingResponse)
async def briefing(persona: str):
    persona = persona.lower().strip()
    if persona not in ("leadership","business","tech"):
        persona = "leadership"
    b, srcs = await generate_briefing(persona)
    sources = [Source(title=s["title"], url=s["url"], published=s.get("published"), source=s.get("source")) for s in srcs]
    return BriefingResponse(persona=persona, briefing=b, sources=sources)
