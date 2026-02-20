# Implementation Plan: RAG Chatbot Integration

**Branch**: `009-rag-chatbot-integration` | **Date**: 2026-02-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-rag-chatbot-integration/spec.md`

## Summary

Upgrade the existing RAG chatbot (from feature 008) to use OpenRouter as the unified AI provider, replacing both HuggingFace embeddings and Google Gemini. Add selected-text retrieval mode where learners highlight text and ask contextual questions. Introduce OpenAI Agents SDK for pipeline orchestration, Qwen3 embeddings (1024D) replacing MiniLM (384D), and session-based conversation tracking.

## Technical Context

**Language/Version**: Python 3.11, JavaScript (ES2020+)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (`openai-agents`), Qdrant Client, psycopg2, React 19
**Storage**: Qdrant Cloud (vectors, 1024D COSINE), Neon Serverless Postgres (metadata/logs/sessions)
**Testing**: pytest (backend), manual integration tests (frontend)
**Target Platform**: Linux server (Render), static site (Vercel/GitHub Pages)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <5s p95 query latency (SC-001), <5min full re-indexing (SC-005)
**Constraints**: Free-tier service limits, single-digit concurrent users, English only
**Scale/Scope**: ~500 passages from 6-part textbook, ~10 concurrent users max

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Dual-System Alignment | PASS | Both book and bot are updated together; bot stays grounded in book content |
| II. Curriculum Integrity | PASS | No module changes; same 6-part structure |
| III. Code-First Technical Depth | PASS | Implementation is code-first, no marketing content |
| IV. Book-Bound RAG Intelligence | PASS | Strict grounding enforced via system prompt + retrieval-only context. Selected-text mode strengthens this. |
| V. Clean Instrument UI | PASS | ChatWidget remains minimal; text selection uses native browser API |
| VI. Precise Technical Tone | PASS | No tone changes |
| VII. Single Source of Truth | PASS | Book remains sole content source; RAG derives from ingested book content |
| VIII. Embodied North Star | PASS | Enhances student ability to learn robotics concepts interactively |

**Post-Phase 1 re-check**: All gates still PASS. OpenRouter + Qwen is an infrastructure change; book content and structure unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/009-rag-chatbot-integration/
├── plan.md              # This file
├── research.md          # Phase 0: technology research
├── data-model.md        # Phase 1: entity definitions & schema
├── quickstart.md        # Phase 1: developer setup guide
├── contracts/
│   └── openapi.yaml     # Phase 1: API contract (v3.0.0)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app (MODIFY: OpenRouter, selected-text, sessions)
├── embeddings.py        # Embedding client (REWRITE: HF → OpenRouter Qwen3)
├── agent.py             # NEW: OpenAI Agents SDK orchestration
├── chunker.py           # Markdown chunker (NO CHANGE)
├── ingest.py            # Ingestion pipeline (MODIFY: 384→1024 dims)
├── db.py                # Neon Postgres (MODIFY: add sessions table, query_logs columns)
├── requirements.txt     # Dependencies (MODIFY: add openai, openai-agents; remove google-genai)
└── .env.example         # Environment template (MODIFY: new vars)

src/
├── components/
│   └── ChatWidget.js    # Chat UI (MODIFY: add text selection capture, session tracking)
└── theme/
    └── Root.js           # Global widget injection (NO CHANGE)

tests/
├── test_embeddings.py   # NEW: OpenRouter embedding tests
├── test_query.py        # NEW: Query endpoint tests (both modes)
└── test_ingest.py       # NEW: Ingestion pipeline tests
```

**Structure Decision**: Web application structure (backend + frontend). Same layout as 008, extending existing files. One new file: `backend/agent.py` for the Agents SDK orchestration layer.

## Design Decisions

### D-001: Qwen3-Embedding-0.6B at 1024 dimensions
- Cheapest Qwen3 model ($0.006/M tokens)
- 1024 dims is a good balance: 2.67x more expressive than MiniLM-384 while fitting Qdrant free tier
- MRL support allows reducing to 512D later if storage is a concern

### D-002: Single OpenRouter API key for all AI services
- Replaces HF_API_TOKEN + GEMINI_API_KEY with one OPENROUTER_API_KEY
- Models configurable via env vars (OPENROUTER_EMBEDDING_MODEL, OPENROUTER_CHAT_MODEL)

### D-003: OpenAI Agents SDK for orchestration
- `@function_tool` decorator for Qdrant retrieval tools
- Agent decides when to call retrieval vs. answer directly
- Built-in streaming support via `Runner.run_streamed()`
- Custom provider: `set_default_openai_client(AsyncOpenAI(base_url="https://openrouter.ai/api/v1"))`

### D-004: Selected-text mode via frontend text selection
- `window.getSelection().toString()` captures highlighted text
- Sent as `selected_text` field in POST /query
- Backend uses selected text as primary context, supplements with Qdrant results
- Citations mark primary source with `is_primary: true`

### D-005: Lightweight session management
- Client generates UUID session_id
- Stored in Neon `sessions` table
- `query_logs` links to session for conversation grouping
- Last N messages from session sent to LLM for multi-turn context

## Migration Plan

1. **Qdrant collection**: Delete and recreate `textbook-passages` with 1024 dims
2. **Backend files**: Update embeddings.py, main.py, ingest.py, db.py; create agent.py
3. **Dependencies**: Replace `google-genai` + `requests` with `openai` + `openai-agents`
4. **Frontend**: Add text selection capture to ChatWidget.js
5. **Environment**: Replace HF/Gemini keys with OpenRouter keys
6. **Re-ingest**: Run full ingestion with new Qwen3 embeddings

## Complexity Tracking

> No constitution violations. All changes are within existing project scope.

| Aspect | Assessment |
|--------|-----------|
| New files | 1 (agent.py) + 3 test files — minimal |
| Modified files | 6 backend + 1 frontend — all existing |
| New dependencies | 2 (openai, openai-agents) replacing 2 (google-genai, requests for HF) |
| Schema changes | 1 new table (sessions), 3 new columns (query_logs) — additive |
| Breaking changes | Qdrant collection recreation requires re-ingestion |
