from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question")
    top_k: Optional[int] = Field(None, ge=1, le=25, description="Override retrieval K")

class Source(BaseModel):
    title: str
    url: str
    published: str | None = None
    source: str | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

BriefingPersona = Literal["leadership", "business", "tech"]

class BriefingResponse(BaseModel):
    persona: BriefingPersona
    briefing: str
    sources: List[Source]
