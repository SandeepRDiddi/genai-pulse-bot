from __future__ import annotations
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

SYSTEM = (
    "You are a GenAI technology update assistant. "
    "Use ONLY the provided context snippets when making factual claims. "
    "If the context is insufficient, say you don't have enough context. "
    "Always be concise and action-oriented. "
    "Cite sources with [1], [2] ... matching the provided links."
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def chat_completion(base_url: str, api_key: str, model: str, user_text: str, context_blocks: list[str]) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    context = "\n\n".join(context_blocks)
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"{user_text}\n\nContext:\n{context}"},
    ]
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": messages, "temperature": 0.2}
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
