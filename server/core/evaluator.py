import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_FILE = os.path.join(BASE_DIR, "logs", "chat_logs.json")


def load_logs():
    if not os.path.exists(LOGS_FILE):
        return []
    with open(LOGS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def citation_coverage(logs):
    if not logs:
        return 0.0
    with_citations = sum(1 for log in logs if log.get("citations"))
    return round(with_citations / len(logs) * 100, 2)


def answer_grounding(logs):
    if not logs:
        return 0.0
    scores = []
    for log in logs:
        answer_words = set(log.get("answer", "").lower().split())
        chunks = log.get("retrieved_chunks", [])
        if not answer_words or not chunks:
            continue
        chunk_words = set()
        for chunk in chunks:
            chunk_words.update(chunk.lower().split())
        if not chunk_words:
            continue
        overlap = len(answer_words & chunk_words)
        scores.append(overlap / len(answer_words))
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores) * 100, 2)


def recall_at_k(logs):
    if not logs:
        return 0.0
    scores = []
    for log in logs:
        citations = log.get("citations", [])
        chunk_ids = log.get("retrieved_chunk_ids", [])
        if not citations or not chunk_ids:
            continue
        chunk_ids_str = " ".join(chunk_ids).lower()
        hit = any(
            citation.lower().replace(".json", "").replace(".pdf", "")
            .replace(".docx", "").replace(".csv", "").replace(".md", "")
            .replace(".txt", "") in chunk_ids_str
            for citation in citations
        )
        scores.append(1.0 if hit else 0.0)
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores) * 100, 2)


def avg_latency(logs):
    if not logs:
        return 0.0
    values = [log["latency_ms"] for log in logs if log.get("latency_ms") is not None]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)


def compute_metrics():
    logs = load_logs()
    return {
        "total_queries": len(logs),
        "recall_at_k": recall_at_k(logs),
        "citation_coverage": citation_coverage(logs),
        "answer_grounding": answer_grounding(logs),
        "avg_latency_ms": avg_latency(logs),
    }
