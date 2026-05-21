import json
import os
from core.embeddings import generate_embedding
from core.vector_store import collection
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi

THRESHOLD   = 1.35
RERANK_MODEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
CHUNKS_FILE  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "chunks.json")


def load_chunks():
    if not os.path.exists(CHUNKS_FILE):
        return []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def bm25_search(query: str, chunks: list, top_k: int = 20) -> list:
    if not chunks:
        return []

    tokenized_corpus = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    scored = sorted(
        enumerate(scores), key=lambda x: x[1], reverse=True
    )[:top_k]

    results = []
    for idx, score in scored:
        if score > 0:
            c = chunks[idx]
            results.append({
                "text":     c["text"],
                "source":   c["source"],
                "chunk_id": c["chunk_id"],
                "bm25_score": round(float(score), 4)
            })
    return results


def rrf_fusion(vector_results: list, bm25_results: list, k: int = 60) -> list:
    scores = {}

    # Score from vector search ranking
    for rank, chunk in enumerate(vector_results):
        cid = chunk["chunk_id"]
        scores[cid] = scores.get(cid, {"chunk": chunk, "score": 0})
        scores[cid]["score"] += 1 / (k + rank + 1)

    # Score from BM25 ranking
    for rank, chunk in enumerate(bm25_results):
        cid = chunk["chunk_id"]
        if cid not in scores:
            scores[cid] = {"chunk": chunk, "score": 0}
        scores[cid]["score"] += 1 / (k + rank + 1)

    # Sort by combined RRF score
    fused = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    return [item["chunk"] for item in fused]


def search_documents(query: str, top_k: int = 5) -> list:
    query = query.lower().strip()

    # ── Stage 1A: Vector search (bi-encoder) ──────────────
    query_embedding = generate_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=20
    )

    vector_results = []
    for doc, metadata, distance, chunk_id in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        results["ids"][0]
    ):
        if distance <= THRESHOLD:
            vector_results.append({
                "text":     doc,
                "source":   metadata.get("source"),
                "chunk_id": metadata.get("chunk_id", chunk_id),
                "distance": round(distance, 3)
            })

    # ── Stage 1B: Keyword search (BM25) ───────────────────
    all_chunks   = load_chunks()
    bm25_results = bm25_search(query, all_chunks, top_k=20)

    # ── Stage 1C: RRF fusion ───────────────────────────────
    candidates = rrf_fusion(vector_results, bm25_results)

    if not candidates:
        return []

    # ── Stage 2: Cross-encoder reranking ──────────────────
    candidates = candidates[:20]  # ensure we only rerank what we score

    pairs  = [[query, c["text"]] for c in candidates]
    scores = RERANK_MODEL.predict(pairs)

    for i, score in enumerate(scores):
        candidates[i]["rerank_score"] = round(float(score), 4)

    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

    return candidates[:top_k]
