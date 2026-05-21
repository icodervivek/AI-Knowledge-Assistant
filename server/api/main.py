from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException
from fastapi import Header, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from core.export_docx import export_to_docx
from core.export_excel import export_to_excel

import traceback

from core.ingest import process_document
from core.rag import ask_question

app = FastAPI()

API_KEY = os.getenv("API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

class AskRequest(BaseModel):
    question: str

class ChatMessage(BaseModel):
    question: str
    answer: str
    citations: list[str]

class ExportRequest(BaseModel):
    messages: list[ChatMessage]

def to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()

    return model.dict()

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/upload", dependencies=[Depends(verify_api_key)])
async def upload_file(
    file: UploadFile = File(...)
):

    try:

        result = await process_document(file)
        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e) or e.__class__.__name__
        )
        
        
@app.post("/reindex", dependencies=[Depends(verify_api_key)])
async def reindex():
    import os
    import json
    from core.ingest import ingest_from_path
    from core.vector_store import collection

    # Clear ChromaDB collection
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    # Clear chunks.json
    chunks_file = "data/processed/chunks.json"
    os.makedirs("data/processed", exist_ok=True)
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump([], f)

    folders = ["data/raw", "data/uploads"]
    allowed = [".txt", ".pdf", ".docx", ".csv", ".json", ".md"]

    total_files = 0
    total_chunks = 0

    for folder in folders:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if any(filename.endswith(ext) for ext in allowed):
                path = os.path.join(folder, filename)
                total_chunks += ingest_from_path(path)
                total_files += 1

    return {
        "message": "Re-index complete",
        "files_indexed": total_files,
        "chunks_indexed": total_chunks
    }
    
@app.get("/eval", dependencies=[Depends(verify_api_key)])
async def evaluate():
    from core.evaluator import compute_metrics
    return compute_metrics()

@app.post("/search", dependencies=[Depends(verify_api_key)])
async def search(
    request: SearchRequest
):
    from core.retriever import search_documents

    results = search_documents(request.query)
    
    return {
        "query": request.query,
        "results": results
    }


@app.post("/ask", dependencies=[Depends(verify_api_key)])
async def ask(request: AskRequest):
    result = ask_question(
        request.question
    )
    
    return result


@app.post("/export/docx", dependencies=[Depends(verify_api_key)])
async def export_docx(request: ExportRequest):
    if not request.messages:
        raise HTTPException(
            status_code=400,
            detail="No chat messages available to export."
        )

    output_path = export_to_docx(
        [to_dict(message) for message in request.messages]
    )
    
    return FileResponse(
        output_path,
        media_type=
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="response.docx"
    )
    
    
@app.post("/export/excel", dependencies=[Depends(verify_api_key)])
async def export_excel(request: ExportRequest):
    if not request.messages:
        raise HTTPException(
            status_code=400,
            detail="No chat messages available to export."
        )

    output_path = export_to_excel(
        [to_dict(message) for message in request.messages]
    )
        
        
    return FileResponse(
        output_path,  
        media_type=
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="response.xlsx"
    )


