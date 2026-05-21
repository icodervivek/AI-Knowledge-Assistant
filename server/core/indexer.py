from core.embeddings import generate_embedding
from core.vector_store import collection


def index_chunks(chunks):
    for chunk in chunks:
        
        existing = collection.get(
            ids=[str(chunk["chunk_id"])]
        )
        
        if existing["ids"]:
            continue
        
        embedding = generate_embedding(
            chunk["text"]
        )
        
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