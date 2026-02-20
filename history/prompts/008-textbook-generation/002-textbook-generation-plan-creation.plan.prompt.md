---
id: 002
title: Textbook Generation Plan Creation
stage: plan
date: 2026-02-01
surface: agent
model: claude-opus-4-5-20251101
feature: 008-textbook-generation
branch: 008-textbook-generation
user: penka
command: /sp.plan
labels: ["planning", "architecture", "rag", "docusaurus", "qdrant", "neon"]
links:
  spec: specs/008-textbook-generation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-textbook-generation/plan.md
  - specs/008-textbook-generation/research.md
  - specs/008-textbook-generation/data-model.md
  - specs/008-textbook-generation/quickstart.md
  - specs/008-textbook-generation/contracts/openapi.yaml
tests:
  - Constitution check (8 gates - all PASS)
  - Post-design re-check (4 items - all PASS)
---

## Prompt

/sp.plan textbook-generation

## Response snapshot

Generated complete implementation plan for the AI-native textbook with RAG chatbot. Produced 5 artifacts:

1. **plan.md** — Technical context, constitution check (8 gates PASS), project structure (frontend + backend), 6 key design decisions (embedding migration, Neon integration, markdown-aware chunking, deterministic IDs, docs restructure, ingestion API).
2. **research.md** — 7 research decisions (R-001 through R-007): HF embeddings, Neon Postgres, Docusaurus i18n, book structure alignment, chunking strategy, dedup approach, LLM selection.
3. **data-model.md** — Qdrant collection schema (384-dim, 7 payload fields), 3 Neon tables (query_logs, ingestion_runs, ingestion_chapters), content hierarchy, locale structure.
4. **contracts/openapi.yaml** — OpenAPI 3.1 spec with 3 endpoints: POST /query, POST /ingest, GET /health.
5. **quickstart.md** — Developer setup guide covering prerequisites, environment config, database init, ingestion, and Urdu translation workflow.

## Outcome

- Impact: Full architectural plan created, bridging the existing hackathon-book codebase to the spec's requirements. Key migrations identified: Google embeddings to HF free-tier, add Neon Postgres, restructure docs directory, upgrade chunking strategy.
- Tests: Constitution check — 8/8 gates PASS. Post-design re-check — 4/4 PASS.
- Files: plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml
- Next prompts: `/sp.tasks` to generate implementation tasks, or `/sp.adr` for significant decisions.
- Reflection: Existing codebase provides strong foundation. Main work is migration (embeddings, structure) rather than greenfield development.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.ps1 resolved paths to C:\Users\penka\specs\ instead of inside the repo. Workaround: wrote plan artifacts directly to repo specs directory.
- Graders run and results (PASS/FAIL): Constitution gates — PASS (8/8). Post-design re-check — PASS (4/4).
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.tasks to validate plan completeness through task decomposition.
