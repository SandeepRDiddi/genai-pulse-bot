from __future__ import annotations
from functools import lru_cache
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def get_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)

def embed_texts(model_name: str, texts: list[str]) -> list[list[float]]:
    model = get_model(model_name)
    embs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [e.tolist() for e in embs]

def vector_size(model_name: str) -> int:
    model = get_model(model_name)
    return model.get_sentence_embedding_dimension()
