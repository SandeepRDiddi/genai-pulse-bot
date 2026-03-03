from __future__ import annotations
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

def get_client(url: str) -> QdrantClient:
    return QdrantClient(url=url)

def ensure_collection(client: QdrantClient, collection: str, vector_size: int) -> None:
    existing = client.get_collections().collections
    if any(c.name == collection for c in existing):
        return
    client.create_collection(
        collection_name=collection,
        vectors_config=qm.VectorParams(size=vector_size, distance=qm.Distance.COSINE),
    )
    # helpful for recency sorting
    client.create_payload_index(
        collection_name=collection,
        field_name="published_ts",
        field_schema=qm.PayloadSchemaType.INTEGER,
    )

def upsert_points(
    client: QdrantClient,
    collection: str,
    ids: List[str],
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
) -> None:
    points = [qm.PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
    client.upsert(collection_name=collection, points=points)

def search(client: QdrantClient, collection: str, query_vector: List[float], limit: int):
    return client.search(collection_name=collection, query_vector=query_vector, limit=limit, with_payload=True)
