# AI Knowledge Assistant

An enterprise-grade Q&A chatbot that answers questions over your uploaded documents using a multi-stage RAG (Retrieval-Augmented Generation) pipeline. Upload PDFs, Word docs, CSVs, and more — then ask natural-language questions and get grounded, citation-backed answers.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 User (Browser)                          │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP (X-API-Key header)
┌──────────────────────▼──────────────────────────────────┐
│          Next.js Frontend  (port 3000)                  │
│  Upload · Chat · Re-index · Export DOCX/Excel           │
└──────────────────────┬──────────────────────────────────┘
                       │  REST API
┌──────────────────────▼──────────────────────────────────┐
│           FastAPI Backend  (port 8000)                  │
│                                                         │
│  ┌──── Hybrid Retrieval ──────────────────────────────┐ │
│  │  Stage 1A  Bi-Encoder → ChromaDB vector search    │ │
│  │            (all-MiniLM-L6-v2, top-20 by distance) │ │
│  │  Stage 1B  BM25 keyword search  (top-20)          │ │
│  │  Stage 1C  RRF Fusion  (combine + re-rank both)   │ │
│  │  Stage 2   Cross-Encoder rerank → top-5 chunks    │ │
│  │            (ms-marco-MiniLM-L-6-v2)               │ │
│  └───────────────────────────────────────────────────┘ │
│                       │                                 │
│  ┌──── Generation ───────────────────────────────────┐  │
│  │  Pass 1  Build grounded prompt + generate answer  │  │
│  │  Pass 2  Verify faithfulness against context      │  │
│  │  Groq Cloud — llama-3.3-70b-versatile             │  │
│  └───────────────────────────────────────────────────┘  │
│                       │                                 │
│          Regex Redaction (PII removal)                  │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┴───────────────┐
         │                             │
┌────────▼────────┐          ┌─────────▼───────┐
│  ChromaDB       │          │  chunks.json    │
│  (vector store) │          │  (BM25 corpus)  │
└─────────────────┘          └─────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 19, TypeScript, Tailwind CSS, Axios |
| Backend | FastAPI, Uvicorn, Pydantic |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector DB | ChromaDB (persistent) |
| Keyword search | rank-bm25 (BM25Okapi) |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM | Groq Cloud — `llama-3.3-70b-versatile` |
| Export | python-docx, openpyxl |
| Evaluation | matplotlib, custom metrics |
| Container | Docker, Docker Compose |

---

## Prerequisites

- **Python 3.11+**
- **Node.js 20+** and npm
- **Groq API key** — free at [console.groq.com](https://console.groq.com)
- **Docker & Docker Compose** — only needed for the containerised option

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd "AI Knowledge Assistant"
```

### 2. Backend setup

```bash
cd server

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Create `server/.env`

```env
GROQ_API_KEY=your_groq_api_key_here
API_KEY=ai-knowledge-assistant-secret-2026
```

### 4. Frontend setup

```bash
cd ../client
npm install
```

### 5. Create `client/.env`

```env
NEXT_PUBLIC_API_KEY=ai-knowledge-assistant-secret-2026
```

---

## Running the App

### Option A — Makefile (recommended)

```bash
make run        # Start backend + frontend together
make reindex    # Re-index all documents
make eval       # Run evaluation report
```

> Requires `make` installed. On Windows, use Git Bash or WSL. Alternatively use Option B.

### Option B — PowerShell scripts

```powershell
.\scripts\run.ps1       # Start backend + frontend
.\scripts\reindex.ps1   # Re-index documents
.\scripts\eval.ps1      # Run evaluation
```

### Option C — Manual

```bash
# Terminal 1 — Backend  (from server/)
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend  (from client/)
npm run dev
```

Open **http://localhost:3000** in your browser.

### Option D — Docker

```bash
make docker-build   # Build images (first time ~10 min)
make docker-up      # Start containers in background
make docker-logs    # Stream logs
make docker-down    # Stop and remove containers
```

Or directly:

```bash
docker-compose build
docker-compose up -d
docker-compose down
```

---

## Environment Variables

| File | Variable | Description |
|---|---|---|
| `server/.env` | `GROQ_API_KEY` | Groq Cloud API key for LLM |
| `server/.env` | `API_KEY` | Shared secret — sent as `X-API-Key` header |
| `client/.env` | `NEXT_PUBLIC_API_KEY` | Same secret, used in frontend requests |

---

## API Reference

All endpoints require the `X-API-Key` header.

| Method | Path | Description |
|---|---|---|
| `POST` | `/upload` | Upload a document (PDF, DOCX, TXT, CSV, JSON, MD) |
| `POST` | `/reindex` | Clear ChromaDB + chunks.json and rebuild from raw/uploads |
| `POST` | `/ask` | Ask a question; returns `answer`, `citations`, `retrieved_chunks`, `latency_ms` |
| `POST` | `/search` | Semantic search; returns raw ranked chunks |
| `GET` | `/eval` | Compute evaluation metrics (Recall@K, Citation Coverage, etc.) |
| `POST` | `/export/docx` | Export chat history as a `.docx` file |
| `POST` | `/export/excel` | Export chat history as a `.xlsx` file |

### Example: Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ai-knowledge-assistant-secret-2026" \
  -d '{"question": "What is the onboarding process?"}'
```

Response:
```json
{
  "answer": "The onboarding process involves...",
  "citations": ["onboarding_sop.pdf"],
  "retrieved_chunks": ["..."],
  "latency_ms": 1240.5
}
```

---

## How to Use

1. **Upload documents** — click "Upload Document" in the sidebar or use `POST /upload`
2. **Re-index** — click the "Re-index" button to rebuild the vector database after uploads
3. **Ask questions** — type in the chat input and press Enter
4. **View citations** — sources are shown below each answer
5. **Export** — click "Export DOCX" or "Export Excel" to download the chat history

Supported file types: `.pdf`, `.docx`, `.txt`, `.csv`, `.json`, `.md`

---

## Evaluation

```bash
cd server
python tools/eval_report.py
```

Saves a chart to `exports/eval_report.png` with four metrics:

| Metric | Description |
|---|---|
| **Recall@K** | % of relevant chunks retrieved in top-K results |
| **Citation Coverage** | Avg number of distinct sources cited per answer |
| **Answer Grounding** | Token overlap between answer and retrieved context |
| **Avg Latency (ms)** | End-to-end response time per query |

---

## Project Structure

```
AI Knowledge Assistant/
├── server/                     # FastAPI backend
│   ├── api/
│   │   └── main.py             # All 7 API endpoints
│   ├── core/
│   │   ├── retriever.py        # Hybrid retrieval pipeline
│   │   ├── rag.py              # RAG orchestration + logging
│   │   ├── generator.py        # Groq LLM wrapper
│   │   ├── embeddings.py       # Bi-encoder embeddings
│   │   ├── vector_store.py     # ChromaDB client
│   │   ├── ingest.py           # Document ingestion
│   │   ├── extractor.py        # Text extraction (PDF/DOCX/CSV…)
│   │   ├── chunker.py          # Text chunking
│   │   ├── prompt_builder.py   # Prompt + verification templates
│   │   ├── evaluator.py        # Metrics computation
│   │   ├── redactor.py         # PII regex redaction
│   │   ├── export_docx.py      # DOCX export
│   │   └── export_excel.py     # Excel export
│   ├── tools/
│   │   ├── synth_data.py       # Generate synthetic test documents
│   │   └── eval_report.py      # Run evaluation + save chart
│   ├── data/
│   │   ├── raw/                # Pre-loaded documents
│   │   ├── uploads/            # User-uploaded documents
│   │   └── processed/
│   │       └── chunks.json     # BM25 corpus
│   ├── logs/
│   │   └── chat_logs.json      # Query/answer audit log
│   ├── exports/                # Exported DOCX/Excel/PNG files
│   ├── vector_db/              # ChromaDB persistent storage
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env                    # GROQ_API_KEY, API_KEY
│
├── client/                     # Next.js frontend
│   ├── app/
│   │   ├── page.tsx            # Main chat UI
│   │   └── layout.tsx
│   ├── public/
│   ├── next.config.ts
│   ├── package.json
│   ├── Dockerfile
│   └── .env                    # NEXT_PUBLIC_API_KEY
│
├── scripts/
│   ├── run.ps1                 # Start app (PowerShell)
│   ├── reindex.ps1             # Re-index (PowerShell)
│   └── eval.ps1                # Evaluation (PowerShell)
│
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Security

- **API key authentication** — all endpoints require `X-API-Key` header
- **PII redaction** — answers are scanned for emails, phone numbers, 12-digit national IDs, and credit card numbers before being returned
- **Anti-hallucination** — strict prompt rules forbid answers outside the retrieved context; a second LLM pass verifies faithfulness
- **CORS** — configurable origins in `api/main.py`

---

## Ethical AI

This assistant is designed with responsible AI principles:

- Answers are grounded strictly in uploaded documents
- Sensitive personal information is automatically redacted from responses
- All queries and answers are logged for audit purposes
- The system clearly states when it cannot find relevant information rather than guessing
