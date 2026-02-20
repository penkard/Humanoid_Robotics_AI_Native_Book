# Quickstart: RAG Chatbot Integration

**Feature**: 009-rag-chatbot-integration
**Date**: 2026-02-17

## Prerequisites

- Python 3.11+
- Node.js 18+ (for Docusaurus frontend)
- An OpenRouter API key ([openrouter.ai](https://openrouter.ai))
- A Qdrant Cloud cluster ([cloud.qdrant.io](https://cloud.qdrant.io), free tier)
- A Neon Postgres database ([neon.tech](https://neon.tech), free tier)

## 1. Environment Setup

Copy the example env file and fill in your credentials:

```bash
cd backend/
cp .env.example .env
```

Required variables:
```
OPENROUTER_API_KEY=sk-or-v1-...
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
OPENROUTER_EMBEDDING_MODEL=qwen/qwen3-embedding-0.6b
OPENROUTER_CHAT_MODEL=qwen/qwen3-30b-a3b
EMBEDDING_DIMENSIONS=1024
```

## 2. Install Backend Dependencies

```bash
cd backend/
pip install -r requirements.txt
```

Key new dependencies (replacing `google-genai` and `requests` for HF):
- `openai` — OpenAI SDK client (used for OpenRouter)
- `openai-agents` — Agent orchestration framework

## 3. Initialize Database

The database tables are auto-created on first startup. To manually initialize:

```bash
python -c "from db import init_db; init_db()"
```

New tables added: `sessions`.
Modified tables: `query_logs` (added `session_id`, `retrieval_mode`, `selected_text` columns).

## 4. Ingest Textbook Content

Run the ingestion pipeline to embed all book content with Qwen3 embeddings:

```bash
python ingest.py
```

This will:
1. Find all `docs/Part-*/**.md` files
2. Chunk them by H2/H3 headings
3. Embed chunks via OpenRouter Qwen3 API
4. Upsert to Qdrant (1024-dim COSINE collection)
5. Log results to Neon

**Note**: First run creates a new `textbook-passages` collection with 1024 dimensions, replacing the old 384-dim collection.

## 5. Start the Backend

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify with:
```bash
curl http://localhost:8000/health
```

## 6. Start the Frontend

```bash
cd ..  # back to repo root
npm install
npm start
```

The ChatWidget is automatically injected on all pages via `src/theme/Root.js`.

## 7. Test the Chatbot

### Full-book mode
Open any textbook page, click the chat bubble, type: "What is a URDF model?"

### Selected-text mode
Highlight a paragraph on any page, then open the chat widget — you'll see "Ask about this selection" prompt. Type your question.

## Architecture Overview

```
Frontend (Docusaurus + React)
  └─ ChatWidget.js → captures questions + selected text
        │
        ▼
Backend (FastAPI)
  └─ POST /query
       │
       ├─ OpenAI Agents SDK (orchestration)
       │    ├─ @function_tool retrieve_passages (Qdrant search)
       │    └─ @function_tool retrieve_selected_context
       │
       ├─ OpenRouter Embeddings API (Qwen3-Embedding-0.6B, 1024D)
       ├─ OpenRouter Chat API (Qwen3-30B-A3B)
       ├─ Qdrant Cloud (vector storage)
       └─ Neon Postgres (query logs, sessions, ingestion records)
```

## Key Changes from 008

| Component | 008 (before) | 009 (after) |
|-----------|-------------|-------------|
| Embeddings | HF all-MiniLM-L6-v2 (384D) | Qwen3-Embedding-0.6B via OpenRouter (1024D) |
| LLM | Google Gemini 2.0 Flash | Qwen3-30B-A3B via OpenRouter |
| Orchestration | Direct API calls | OpenAI Agents SDK |
| Retrieval modes | Full-book only | Full-book + selected-text |
| Session tracking | None | UUID-based sessions in Neon |
| API keys | HF_API_TOKEN + GEMINI_API_KEY | OPENROUTER_API_KEY (single key) |
