# Implementation Plan: AI-Native Textbook with RAG Chatbot

**Branch**: `008-textbook-generation` | **Date**: 2026-02-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/008-textbook-generation/spec.md`

## Summary

Build an AI-native textbook on humanoid robotics using Docusaurus with auto-generated sidebar, backed by a RAG chatbot (Qdrant + Neon + Hugging Face embeddings + Gemini generation). The existing `hackathon-book` codebase provides a working Docusaurus site and FastAPI RAG backend that must be restructured, upgraded to free-tier embeddings, extended with Neon for structured logging, and enhanced with Urdu i18n and a personalization chapter.

## Technical Context

**Language/Version**: TypeScript (Docusaurus frontend), Python 3.11+ (FastAPI backend)
**Primary Dependencies**: Docusaurus 3.9.2, React 19, FastAPI, Qdrant Client, google-genai, psycopg2, requests (Hugging Face API)
**Storage**: Qdrant Cloud (vector store, 384-dim COSINE), Neon serverless Postgres (query logs, ingestion records)
**Testing**: Jest (frontend components), pytest (backend API + ingestion pipeline)
**Target Platform**: GitHub Pages (static frontend), Cloud-hosted backend (FastAPI + Uvicorn)
**Project Type**: Web application (static site + API backend)
**Performance Goals**: p95 chatbot response < 5s, ingestion < 5 min for full textbook, 10 concurrent queries
**Constraints**: Free-tier services only for embeddings and databases; no paid API keys for core functionality
**Scale/Scope**: ~20-30 chapter files, ~200-500 passages, single-digit concurrent users (educational context)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gates

| # | Principle | Gate | Status |
|---|-----------|------|--------|
| I | Dual-System Alignment | Book content changes must propagate to RAG knowledge base | PASS — Re-ingestion endpoint (POST /ingest) ensures sync |
| II | Curriculum Integrity | All 4 modules + capstone preserved in 6-part structure | PASS — Parts 2-5 map to Modules 1-4; Part 6 = Capstone; Part 1 = additive Introduction |
| III | Code-First Technical Depth | Content favors code-first presentation, serious builder audience | PASS — Spec assumes technically proficient learners; chapters include code walkthroughs |
| IV | Book-Bound RAG Intelligence | Chatbot grounded strictly in book content, no hallucination | PASS — FR-004 (grounded retrieval), FR-006 (scope refusal), FR-014 (terminology preservation) |
| V | Clean Instrument UI | Minimal, technical UI; clear navigation | PASS — Auto-sidebar, clean Docusaurus theme, chat widget as overlay |
| VI | Precise Technical Tone | No hype, accurate terminology | PASS — FR-014 enforces book terminology; system prompt constrains generation |
| VII | Single Source of Truth | Book is authoritative; all downstream derives from book | PASS — RAG ingests from docs/; no secondary sources |
| VIII | Embodied North Star | Advances student ability to design/simulate/deploy humanoid robots | PASS — Curriculum covers ROS 2, simulation, VLA, capstone integration |

### Post-Design Re-check

| # | Concern | Status |
|---|---------|--------|
| I | Ingestion pipeline uses delete-then-insert per chapter — ensures no stale data | PASS |
| II | 6-part directory structure explicitly maps to constitutional modules | PASS |
| IV | System prompt includes strict grounding instruction + scope refusal logic | PASS |
| VII | Embedding model change (HF vs Google) doesn't affect source-of-truth principle | PASS |

All gates pass. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/008-textbook-generation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research decisions
├── data-model.md        # Entity definitions and schemas
├── quickstart.md        # Developer setup guide
├── contracts/
│   └── openapi.yaml     # API contract (OpenAPI 3.1)
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
# Docusaurus Frontend
docs/
├── Part-1-introduction/
│   ├── _category_.json
│   └── 01-overview.md
├── Part-2-humanoid-robotics/
│   ├── _category_.json
│   ├── 01-ros2-basics.md
│   └── 02-urdf-modeling.md
├── Part-3-ros2/
│   ├── _category_.json
│   ├── 01-nodes-topics.md
│   └── 02-services-actions.md
├── Part-4-digital-twin/
│   ├── _category_.json
│   ├── 01-gazebo.md
│   └── 02-isaac-sim.md
├── Part-5-vla/
│   ├── _category_.json
│   ├── 01-vla-overview.md
│   └── 02-voice-to-action.md
├── Part-6-capstone/
│   ├── _category_.json
│   └── 01-capstone-project.md
└── personalize/
    └── index.mdx             # Self-assessment personalization chapter

i18n/
└── ur/
    └── docusaurus-plugin-content-docs/
        └── current/          # Urdu translations mirror docs/ structure

src/
├── components/
│   └── ChatWidget.js         # RAG chatbot widget (exists, needs update)
├── theme/
│   └── Root.js               # Global wrapper injecting ChatWidget
├── pages/
│   └── index.tsx             # Homepage
└── css/
    └── custom.css            # Global styles

# Backend
backend/
├── main.py                   # FastAPI server (query + ingest + health endpoints)
├── ingest.py                 # Markdown-aware ingestion pipeline
├── db.py                     # Neon Postgres connection and schema init
├── embeddings.py             # Hugging Face embedding client
├── chunker.py                # Markdown-aware text chunking
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
└── tests/
    ├── test_query.py         # Query endpoint tests
    ├── test_ingest.py        # Ingestion pipeline tests
    └── test_chunker.py       # Chunking logic tests

# Config
docusaurus.config.ts          # Docusaurus config (auto-sidebar, i18n)
sidebars.ts                   # Auto-generated sidebar config
package.json                  # Node dependencies
```

**Structure Decision**: Web application with a static Docusaurus frontend deployed to GitHub Pages and a Python FastAPI backend deployed separately. The existing `hackathon-book/` directory content will be migrated into the repo root's `docs/` directory with the new 6-part structure. The `backend/` directory at repo root is the canonical backend location.

## Key Design Decisions

### D-001: Migrate from Google Embeddings to Hugging Face

**Current state**: `backend/ingest.py` uses Google `text-embedding-004` (768 dims, paid).
**Target state**: Hugging Face Inference API with `all-MiniLM-L6-v2` (384 dims, free).
**Impact**: Qdrant collection must be recreated (new dimension size). Full re-ingestion required.
**Rationale**: See research.md R-001.

### D-002: Add Neon Postgres for Structured Data

**Current state**: No relational database. No query logging.
**Target state**: Neon free-tier Postgres for query_logs, ingestion_runs, ingestion_chapters.
**Impact**: New `db.py` module, schema migrations, logging middleware in FastAPI.
**Rationale**: See research.md R-002.

### D-003: Markdown-Aware Chunking

**Current state**: Naive 1000-char splitting in `ingest.py`.
**Target state**: Heading-based splitting with metadata extraction (part, chapter, section).
**Impact**: New `chunker.py` module. Richer Qdrant payloads enable better source citations.
**Rationale**: See research.md R-005.

### D-004: Deterministic Point IDs for Deduplication

**Current state**: Random UUID per chunk (duplicates on re-ingestion).
**Target state**: Hash-based IDs + delete-then-insert per chapter.
**Impact**: Changes to `ingest.py` upsert logic.
**Rationale**: See research.md R-006.

### D-005: Restructure Docs Directory

**Current state**: `hackathon-book/docs/` has Part-1 through Part-5.
**Target state**: Root-level `docs/` with Part-1 through Part-6 matching spec's 6-part structure.
**Impact**: Content migration from `hackathon-book/docs/` to `docs/`. Config updates.

### D-006: Add Ingestion API Endpoint

**Current state**: Ingestion is a standalone script (`python ingest.py`).
**Target state**: `POST /ingest` endpoint for triggering ingestion via API (plus CLI fallback).
**Impact**: New endpoint in `main.py`. Enables automated re-ingestion on content updates.

## Complexity Tracking

No constitution violations detected. No complexity justifications needed.
