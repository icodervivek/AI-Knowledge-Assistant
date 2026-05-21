import json
import os

from datetime import datetime

from core.extractor import extract_text, extract_text_from_bytes
from core.chunker import chunk_text
from core.cleaner import clean_text
from core.format_file_size import format_file_size
from core.indexer import index_chunks

MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = [
    ".txt",
    ".pdf",
    ".docx",
    ".csv",
    ".json",
    ".md"
]

async def process_document(file):

    # Validate extension
    if not any(
        file.filename.endswith(ext)
        for ext in ALLOWED_EXTENSIONS
    ):

        raise ValueError("Invalid file type. Only .txt, .pdf, .docx, .csv, .json, .md supported.")

    # Read file
    content = await file.read()

    # Create uploads folder
    os.makedirs(
        "data/uploads",
        exist_ok=True
    )

    # Save raw uploaded file
    upload_path = f"data/uploads/{file.filename}"

    with open(upload_path, "wb") as buffer:

        buffer.write(content)

    # Reset cursor
    file.file.seek(0)

    # Validate size
    if len(content) > MAX_FILE_SIZE:

        raise ValueError("File too large")

    # Extract text
    raw_text = extract_text(file)

    # Clean text
    cleaned_text = clean_text(raw_text)

    # Chunk text
    chunks = chunk_text(cleaned_text)

    # Generate metadata
    metadata = {

        "filename": file.filename,

        "content_type": file.content_type,

        "file_size": format_file_size(len(content)),

        "total_chunks": len(chunks),

        "createdAt": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    }

    # Create chunk objects
    processed_chunks = []

    for index, chunk in enumerate(chunks):

        processed_chunks.append({

            "chunk_id": f"{file.filename}_{index + 1}",

            "text": chunk,

            "source": file.filename,

            "metadata": metadata
        })
        
        

    # Create processed folder
    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    chunks_file = "data/processed/chunks.json"

    existing_chunks = []

    # Create chunks.json if missing
    if not os.path.exists(chunks_file):

        with open(
            chunks_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump([], file)

    # Load existing chunks safely
    try:

        with open(
            chunks_file,
            "r",
            encoding="utf-8"
        ) as file:

            existing_chunks = json.load(file)

    except json.JSONDecodeError:

        existing_chunks = []

    # Append new chunks
    existing_chunks.extend(processed_chunks)

    # Save all chunks
    with open(
        chunks_file,
        "w",
        encoding="utf-8"
    ) as json_file:

        json.dump(
            existing_chunks,
            json_file,
            indent=4,
            ensure_ascii=False
        )
        
    index_chunks(processed_chunks)

    return {
    "message": "Document uploaded and indexed successfully",
    "metadata": metadata,
    "total_chunks": len(processed_chunks),
    "vector_indexed": True
    }
    

def ingest_from_path(file_path: str):
      import mimetypes

      filename = os.path.basename(file_path)

      with open(file_path, "rb") as f:
          content = f.read()

      content_type, _ = mimetypes.guess_type(file_path)

      cleaned_text = clean_text(
          extract_text_from_bytes(content, filename)
      )

      chunks = chunk_text(cleaned_text)

      metadata = {
          "filename": filename,
          "content_type": content_type or "unknown",
          "file_size": format_file_size(len(content)),
          "total_chunks": len(chunks),
          "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M")
      }

      processed_chunks = [
          {
              "chunk_id": f"{filename}_{i + 1}",
              "text": chunk,
              "source": filename,
              "metadata": metadata
          }
          for i, chunk in enumerate(chunks)
      ]

      os.makedirs("data/processed", exist_ok=True)
      chunks_file = "data/processed/chunks.json"

      existing_chunks = []
      if os.path.exists(chunks_file):
          try:
              with open(chunks_file, "r", encoding="utf-8") as f:
                  existing_chunks = json.load(f)
          except json.JSONDecodeError:
              existing_chunks = []

      existing_chunks.extend(processed_chunks)

      with open(chunks_file, "w", encoding="utf-8") as f:
          json.dump(existing_chunks, f, indent=4, ensure_ascii=False)

      index_chunks(processed_chunks)

      return len(processed_chunks)