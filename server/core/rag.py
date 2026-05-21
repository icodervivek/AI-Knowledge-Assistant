from core.retriever import search_documents
from core.prompt_builder import build_prompt, build_verification_prompt
from core.generator import generate_answer
from core.redactor import redact

import json
import os
import time

from datetime import datetime

ENABLE_VERIFICATION = True

GREETINGS = {"hi", "hello", "hey", "hiya", "howdy", "greetings", "good morning", "good afternoon", "good evening", "what's up", "whats up", "sup"}

IDENTITY_PHRASES = {"who are you", "what are you", "what can you do", "what do you do", "tell me about yourself", "introduce yourself", "what is your name", "whats your name", "who made you", "how can you help", "how can you help me", "what is this", "what is this app", "help"}

def ask_question(query: str):

    start_time = time.time()
    normalized = query.strip().lower().rstrip("!.,?")

    # Handle greetings
    if normalized in GREETINGS:
        return {
            "answer": "Hello! I'm your AI Knowledge Assistant. Upload a document and ask me anything about it.",
            "citations": [],
            "retrieved_chunks": [],
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }

    # Handle identity questions
    if normalized in IDENTITY_PHRASES:
        return {
            "answer": "I'm the **AI Knowledge Assistant** — a RAG-powered AI built to help you find information from your internal documents.\n\n**What I can do:**\n- Answer questions from uploaded documents\n- Show source citations for every answer\n- Export answers to Word or Excel\n\n**How to use:**\n1. Upload a document using the sidebar\n2. Ask me any question about it\n3. I'll find the answer and show you the source",
            "citations": [],
            "retrieved_chunks": [],
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }

    # Retrieve relevant chunks
    retrieved_chunks = search_documents(normalized)

    # If no relevant chunks found, return immediately
    if not retrieved_chunks:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "citations": [],
            "retrieved_chunks": [],
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }

    # Build prompt and generate answer
    prompt = build_prompt(query, retrieved_chunks)
    answer = generate_answer(prompt)

    # Verify answer against context
    if ENABLE_VERIFICATION and retrieved_chunks:
        verification_prompt = build_verification_prompt(
            query, answer, retrieved_chunks
        )
        answer = generate_answer(verification_prompt)

    latency = time.time() - start_time

    answer = redact(answer)
    
    # Extract citations (unique source filenames)
    citations = list(set(chunk["source"] for chunk in retrieved_chunks))

    # Extract chunk IDs
    retrieved_chunk_ids = [chunk["chunk_id"] for chunk in retrieved_chunks]

    # Extract chunk text for evaluator metrics
    retrieved_chunk_texts = [chunk["text"] for chunk in retrieved_chunks]

    os.makedirs("logs", exist_ok=True)
    logs_file = "logs/chat_logs.json"

    log_entry = {
        "question": query,
        "answer": answer,
        "citations": citations,
        "retrieved_chunk_ids": retrieved_chunk_ids,
        "retrieved_chunks": retrieved_chunk_texts,
        "latency_ms": round(latency * 1000, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    existing_logs = []
    if os.path.exists(logs_file):
        try:
            with open(logs_file, "r", encoding="utf-8") as f:
                existing_logs = json.load(f)
        except json.JSONDecodeError:
            existing_logs = []

    existing_logs.append(log_entry)

    with open(logs_file, "w", encoding="utf-8") as f:
        json.dump(existing_logs, f, indent=4, ensure_ascii=False)

    return {
        "answer": answer,
        "citations": citations,
        "retrieved_chunks": retrieved_chunk_texts,
        "latency_ms": round(latency * 1000, 2)
    }
