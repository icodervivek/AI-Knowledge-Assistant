# AI Knowledge Assistant — High Level Design Diagrams

> All diagrams use [Mermaid](https://mermaid.js.org/) syntax.  
> Render in GitHub, VS Code (Markdown Preview Mermaid Support), or [mermaid.live](https://mermaid.live).

---

## 1. Overall System Architecture

```mermaid
graph TD
    subgraph Browser["🖥️ Browser (User)"]
        UI["Next.js Frontend\nport 3000"]
    end

    subgraph Backend["⚙️ FastAPI Backend (port 8000)"]
        API["API Gateway\napi/main.py\n─────────────\nPOST /upload\nPOST /ask\nPOST /search\nPOST /reindex\nGET  /eval\nPOST /export/docx\nPOST /export/excel"]
        AUTH["API Key\nMiddleware\n(X-API-Key header)"]
        INGEST["Document Ingestion\ncore/ingest.py"]
        RETRIEVER["Hybrid Retriever\ncore/retriever.py"]
        RAG["RAG Orchestrator\ncore/rag.py"]
        PROMPT["Prompt Builder\ncore/prompt_builder.py"]
        GEN["LLM Generator\ncore/generator.py\n─────────────\nGroq Cloud\nllama-3.3-70b-versatile"]
        REDACT["PII Redactor\ncore/redactor.py"]
        EVAL["Evaluator\ncore/evaluator.py"]
        EXPORT_D["DOCX Exporter\ncore/export_docx.py"]
        EXPORT_E["Excel Exporter\ncore/export_excel.py"]
    end

    subgraph Storage["🗄️ Persistent Storage"]
        CHROMA["ChromaDB\nvector_db/\n(Bi-encoder vectors)"]
        CHUNKS["chunks.json\ndata/processed/\n(BM25 corpus)"]
        LOGS["chat_logs.json\nlogs/\n(Audit log)"]
        RAW["Raw Files\ndata/raw/ + data/uploads/"]
        EXPORTS["Exported Files\nexports/"]
    end

    subgraph External["☁️ External Services"]
        GROQ["Groq Cloud API\nllama-3.3-70b-versatile"]
        EMBED["all-MiniLM-L6-v2\n(sentence-transformers)"]
        RERANK["ms-marco-MiniLM-L-6-v2\n(cross-encoder)"]
    end

    UI -- "REST + X-API-Key" --> AUTH
    AUTH --> API
    API --> INGEST
    API --> RAG
    API --> EVAL
    API --> EXPORT_D
    API --> EXPORT_E

    INGEST --> RAW
    INGEST --> CHUNKS
    INGEST --> CHROMA

    RAG --> RETRIEVER
    RAG --> PROMPT
    RAG --> GEN
    RAG --> REDACT
    RAG --> LOGS

    RETRIEVER --> CHROMA
    RETRIEVER --> CHUNKS
    RETRIEVER --> EMBED
    RETRIEVER --> RERANK

    GEN --> GROQ
    EVAL --> LOGS

    EXPORT_D --> EXPORTS
    EXPORT_E --> EXPORTS
```

---

## 2. Document Ingestion Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Next.js Frontend
    participant API as FastAPI /upload
    participant AUTH as API Key Guard
    participant EXT as extractor.py
    participant CLN as cleaner.py
    participant CHK as chunker.py
    participant IDX as indexer.py
    participant VEC as ChromaDB
    participant FS as chunks.json

    User->>FE: Select file & click Upload
    FE->>API: POST /upload (multipart/form-data, X-API-Key)
    API->>AUTH: Verify X-API-Key header
    AUTH-->>API: ✅ Authorized

    API->>API: Validate file extension (.pdf/.docx/.txt/.csv/.json/.md)
    API->>API: Validate file size (≤ 5 MB)
    API->>API: Save raw file → data/uploads/

    API->>EXT: extract_text(file)
    EXT-->>API: raw_text (plain string)

    API->>CLN: clean_text(raw_text)
    CLN-->>API: cleaned_text

    API->>CHK: chunk_text(cleaned_text)
    CHK-->>API: chunks[] (fixed-size text windows)

    API->>API: Attach metadata (filename, size, timestamp, chunk_id)

    par Index to Vector Store
        API->>IDX: index_chunks(processed_chunks)
        IDX->>VEC: embed + upsert each chunk
        VEC-->>IDX: ✅ stored
    and Append to BM25 corpus
        API->>FS: append chunks to chunks.json
        FS-->>API: ✅ saved
    end

    API-->>FE: { message, metadata, total_chunks, vector_indexed: true }
    FE-->>User: Toast ✅ "File uploaded successfully"
```

---

## 3. RAG Query & Answer Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Next.js Frontend
    participant API as FastAPI /ask
    participant RAG as rag.py
    participant RET as retriever.py
    participant PB as prompt_builder.py
    participant GEN as generator.py
    participant GROQ as Groq Cloud (LLM)
    participant RED as redactor.py
    participant LOG as chat_logs.json

    User->>FE: Type question & press Enter
    FE->>API: POST /ask { question } + X-API-Key

    API->>RAG: ask_question(query)

    RAG->>RAG: Normalize query (lowercase, strip punctuation)
    RAG->>RAG: Check if greeting / identity phrase → fast-path reply

    RAG->>RET: search_documents(query)
    Note over RET: Hybrid 4-Stage Retrieval (see Diagram 4)
    RET-->>RAG: top-5 ranked chunks

    alt No chunks found
        RAG-->>API: "Could not find relevant information"
        API-->>FE: answer with empty citations
    else Chunks found
        RAG->>PB: build_prompt(query, chunks)
        PB-->>RAG: grounded prompt

        RAG->>GEN: generate_answer(prompt)
        GEN->>GROQ: chat/completions API call
        GROQ-->>GEN: answer text
        GEN-->>RAG: answer

        RAG->>PB: build_verification_prompt(query, answer, chunks)
        PB-->>RAG: verification prompt

        RAG->>GEN: generate_answer(verification_prompt)
        GEN->>GROQ: second pass (faithfulness check)
        GROQ-->>GEN: verified answer
        GEN-->>RAG: verified answer

        RAG->>RED: redact(answer)
        RED-->>RAG: PII-scrubbed answer

        RAG->>LOG: Append log entry (question, answer, citations, latency, timestamp)

        RAG-->>API: { answer, citations, retrieved_chunks, latency_ms }
        API-->>FE: JSON response
        FE-->>User: Stream answer char-by-char + show citations
    end
```

---

## 4. Hybrid Retrieval Pipeline (4 Stages)

```mermaid
graph TD
    Q["🔍 User Query"]

    Q --> S1A & S1B

    subgraph Stage1A["Stage 1A — Bi-Encoder Vector Search"]
        direction TB
        EMB["Embed query\nall-MiniLM-L6-v2"]
        VQUERY["ChromaDB cosine search\ntop-20 candidates"]
        VFILTER["Distance filter\n(threshold ≤ 1.35)"]
        EMB --> VQUERY --> VFILTER
    end

    subgraph Stage1B["Stage 1B — BM25 Keyword Search"]
        direction TB
        LOAD["Load chunks.json\n(BM25 corpus)"]
        TOKENIZE["Tokenize corpus + query"]
        BM25["BM25Okapi scoring\ntop-20 candidates"]
        LOAD --> TOKENIZE --> BM25
    end

    subgraph Stage1C["Stage 1C — RRF Fusion"]
        direction TB
        RRF["Reciprocal Rank Fusion\nScore = Σ 1/(k + rank)\nk = 60"]
        MERGE["Deduplicate & sort\nby combined RRF score"]
        RRF --> MERGE
    end

    subgraph Stage2["Stage 2 — Cross-Encoder Reranking"]
        direction TB
        PAIRS["Form (query, chunk) pairs"]
        CE["Cross-Encoder score\nms-marco-MiniLM-L-6-v2"]
        SORT["Sort by rerank score\nDescending"]
        TOP5["Top-5 chunks ✅"]
        PAIRS --> CE --> SORT --> TOP5
    end

    VFILTER -- "vector_results[]" --> Stage1C
    BM25 -- "bm25_results[]" --> Stage1C
    Stage1A --> Stage1C
    Stage1B --> Stage1C
    MERGE -- "≤20 candidates" --> Stage2
    Stage2 --> TOP5
```

---

## 5. Frontend Component Architecture

```mermaid
graph TD
    subgraph NextJS["Next.js App (client/app/)"]
        PAGE["page.tsx\n─────────────────────\nState: question, messages,\nfile, loading flags\n\nHandlers: uploadFile, askQuestion,\nexportDocx, exportExcel, reindex"]

        subgraph Layout["layout.tsx (Root Layout)"]
            TOAST["ToastContainer\n(react-toastify)"]
        end

        subgraph Left["Left Panel"]
            SIDEBAR["Sidebar.tsx\n─────────────\n• File picker\n• Upload button\n• Re-index button\n• Export DOCX\n• Export Excel"]
        end

        subgraph Main["Main Panel"]
            HEADER["ChatHeader.tsx\n─────────────\nApp title\nLoading indicator"]
            MSGLIST["MessageList.tsx\n─────────────\nScrollable message history\nRenders each Q&A pair"]
            MSGI["MarkdownContent.tsx\n─────────────\nRendered markdown\n+ syntax highlight"]
            INPUT["ChatInput.tsx\n─────────────\nTextarea\nSend button"]
        end

        ICONS["icons.tsx\n(SVG icon components)"]
        PALETTE["palette.ts\n(Design tokens / colors)"]
        TYPES["types.ts\n(Message interface)"]
    end

    PAGE --> SIDEBAR
    PAGE --> HEADER
    PAGE --> MSGLIST
    PAGE --> INPUT
    MSGLIST --> MSGI
    PAGE -.-> TOAST
    PAGE -.-> ICONS
    PAGE -.-> PALETTE
    PAGE -.-> TYPES
```

---

## 6. Export Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Next.js Frontend
    participant API as FastAPI
    participant EXP as export_docx.py / export_excel.py
    participant FS as exports/ directory

    User->>FE: Click "Export DOCX" or "Export Excel"
    FE->>FE: Check messages[] is not empty

    alt Export DOCX
        FE->>API: POST /export/docx { messages[] } + X-API-Key
        API->>EXP: export_to_docx(messages)
        EXP->>EXP: Build .docx (python-docx)\nTitle + Q&A pairs + citations
        EXP->>FS: Save response.docx
        EXP-->>API: file path
        API-->>FE: FileResponse (.docx blob)
    else Export Excel
        FE->>API: POST /export/excel { messages[] } + X-API-Key
        API->>EXP: export_to_excel(messages)
        EXP->>EXP: Build .xlsx (openpyxl)\nColumns: Question | Answer | Citations
        EXP->>FS: Save response.xlsx
        EXP-->>API: file path
        API-->>FE: FileResponse (.xlsx blob)
    end

    FE->>FE: triggerDownload(blob, filename)
    FE-->>User: Browser download prompt
```

---

## 7. Security Architecture

```mermaid
graph TD
    REQ["Incoming HTTP Request"]

    REQ --> KEYCHECK{"X-API-Key\nheader present?"}

    KEYCHECK -- "Missing" --> R401A["401 Unauthorized"]
    KEYCHECK -- "Present" --> KEYVAL{"Key matches\nAPI_KEY env var?"}
    KEYVAL -- "No match" --> R401B["401 Invalid API key"]
    KEYVAL -- "Match ✅" --> HANDLER["Route Handler\n(upload / ask / search / etc.)"]

    HANDLER --> PROCESS["Process Request"]

    PROCESS --> ANSWERGEN["LLM Answer Generated"]

    ANSWERGEN --> PII["PII Redactor\n(redactor.py)\n─────────────────────────\nRegex patterns scrub:\n• Email addresses\n• Phone numbers\n• 12-digit national IDs\n• Credit card numbers"]

    PII --> CLEAN["Clean Answer\n(PII replaced with [REDACTED])"]
    CLEAN --> RESPONSE["HTTP Response to Client"]

    subgraph AntiHallucination["Anti-Hallucination Layer"]
        PROMPT1["Pass 1: Grounded prompt\n(strict: answer only from context)"]
        PROMPT2["Pass 2: Verification prompt\n(faithfulness check vs retrieved chunks)"]
        PROMPT1 --> LLM1["LLM Call #1"]
        LLM1 --> PROMPT2 --> LLM2["LLM Call #2 (verify)"]
    end

    PROCESS --> AntiHallucination
    AntiHallucination --> ANSWERGEN

    subgraph AuditLog["Audit Logging"]
        LOG["chat_logs.json\n─────────────────────\nquestion · answer\ncitations · chunk_ids\nlatency_ms · timestamp"]
    end

    PROCESS --> AuditLog
```

---

## 8. Re-index Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Next.js Frontend
    participant API as FastAPI /reindex
    participant VEC as ChromaDB
    participant FS as chunks.json
    participant ING as ingest_from_path()

    User->>FE: Click "Re-index"
    FE->>API: POST /reindex + X-API-Key

    API->>VEC: Get all existing IDs
    VEC-->>API: existing_ids[]
    API->>VEC: Delete all IDs (clear collection)
    VEC-->>API: ✅ Cleared

    API->>FS: Overwrite chunks.json with []
    FS-->>API: ✅ Cleared

    loop For each file in data/raw/ + data/uploads/
        API->>API: Filter by allowed extensions (.txt/.pdf/.docx/.csv/.json/.md)
        API->>ING: ingest_from_path(file_path)
        ING->>ING: Extract → Clean → Chunk → Attach metadata
        ING->>VEC: index_chunks (embed + upsert)
        ING->>FS: Append chunks to chunks.json
        ING-->>API: chunk_count
    end

    API-->>FE: { message, files_indexed, chunks_indexed }
    FE-->>User: Toast ✅ "Re-indexed N files successfully"
```

---

## 9. Evaluation Pipeline

```mermaid
graph TD
    subgraph Trigger["Trigger"]
        CLI["python tools/eval_report.py\n─── OR ───\nGET /eval"]
    end

    subgraph Evaluator["core/evaluator.py"]
        LOAD["Load chat_logs.json\n(all past Q&A sessions)"]
        
        subgraph Metrics["Compute 4 Metrics"]
            M1["Recall@K\n% relevant chunks in top-K\n(retrieved_chunk_ids vs expected)"]
            M2["Citation Coverage\nAvg distinct sources cited\nper answer"]
            M3["Answer Grounding\nToken overlap between\nanswer text & retrieved chunks"]
            M4["Avg Latency (ms)\nEnd-to-end response time\nper query"]
        end

        LOAD --> M1 & M2 & M3 & M4
    end

    subgraph Output["Output"]
        API_RESP["JSON response\n{ recall_at_k, citation_coverage,\n  answer_grounding, avg_latency_ms }"]
        CHART["eval_report.png\nexports/ directory\n(matplotlib bar chart)"]
    end

    Trigger --> Evaluator
    M1 & M2 & M3 & M4 --> API_RESP
    M1 & M2 & M3 & M4 --> CHART
```

---

## 10. Data & Storage Layer

```mermaid
graph LR
    subgraph Inputs["📥 Input Data"]
        RAW["data/raw/\nPre-loaded documents"]
        UPLOAD["data/uploads/\nUser-uploaded documents"]
    end

    subgraph Processing["⚙️ Processed State"]
        CHUNKS["data/processed/chunks.json\n─────────────────────────\nArray of chunk objects:\n{ chunk_id, text, source, metadata }"]
    end

    subgraph VectorDB["🔢 Vector Store"]
        CHROMA["vector_db/ (ChromaDB)\n─────────────────────────\nPersistent collection:\nchunk embeddings + metadata\nModel: all-MiniLM-L6-v2\n384-dim vectors"]
    end

    subgraph Logs["📋 Logs & Exports"]
        CHATLOG["logs/chat_logs.json\n─────────────────────────\nFull audit trail:\nquery · answer · citations\nchunk_ids · latency · timestamp"]
        EXPORTS["exports/\n─────────────────────────\nresponse.docx\nresponse.xlsx\neval_report.png"]
    end

    RAW & UPLOAD -- "extract → clean → chunk" --> CHUNKS
    CHUNKS -- "embed + upsert" --> CHROMA
    CHROMA -- "vector search (top-20)" --> QA["Query Time"]
    CHUNKS -- "BM25 search (top-20)" --> QA
    QA -- "append log" --> CHATLOG
    QA -- "export on demand" --> EXPORTS
```
