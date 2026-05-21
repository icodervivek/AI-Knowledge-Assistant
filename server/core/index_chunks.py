import json

from core.embeddings import generate_embedding
from core.vector_store import collection

with open("data/processed/chunks.json", "r", encoding="utf-8") as file:
    chunks = json.load(file)

for chunk in chunks:
    embedding = generate_embedding(
        chunk["text"]
    )
    
    existing = collection.get(
    ids=[str(chunk["chunk_id"])]
    )

    if existing["ids"]:
        continue
    
    collection.add(
        ids=[str(chunk["chunk_id"])],
        documents=[chunk["text"]],
        embeddings=[embedding],
        metadatas=[
        {
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "content_type":
                chunk["metadata"]["content_type"],
            "createdAt":
                chunk["metadata"]["createdAt"]
        }
        ]
    )
    
print("Chunks indexed successfully.")