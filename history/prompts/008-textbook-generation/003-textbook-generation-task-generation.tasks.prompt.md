---
id: 003
title: Textbook Generation Task Generation
stage: tasks
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 008-textbook-generation
branch: 008-textbook-generation
user: penka
command: /sp.tasks
labels: ["tasks", "implementation", "rag", "docusaurus", "planning"]
links:
  spec: specs/008-textbook-generation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-textbook-generation/tasks.md
tests:
  - Format validation: all 41 tasks follow checklist format (checkbox + ID + labels + file paths)
---

## Prompt

/sp.tasks textbook-generation

## Response snapshot

Generated 41 implementation tasks across 9 phases for the AI-native textbook with RAG chatbot. Tasks organized by user story (US1-US6) with clear dependencies.

Phase breakdown:
- Phase 1 Setup: 7 tasks (T001-T007) — directory restructure, config, deps
- Phase 2 Foundational: 4 tasks (T008-T011) — embeddings.py, db.py, chunker.py, health endpoint
- Phase 3 US3 Ingestion (P1): 5 tasks (T012-T016) — rewrite ingest pipeline, Qdrant collection, Neon logging, POST /ingest
- Phase 4 US2 Chatbot (P1): 6 tasks (T017-T022) — query endpoint, system prompt, query logging, error handling, ChatWidget update
- Phase 5 US1 Navigation (P1): 4 tasks (T023-T026) — content, sidebar, homepage, CSS
- Phase 6 US4 Module Nav (P2): 2 tasks (T027-T028) — curriculum prompt, capstone content
- Phase 7 US5 Urdu (P3): 4 tasks (T029-T032) — i18n config, directory, translation, RTL CSS
- Phase 8 US6 Personalize (P3): 3 tasks (T033-T035) — MDX chapter, category, study paths
- Phase 9 Polish: 6 tasks (T036-T041) — e2e validation, gitignore, CORS

MVP scope: T001-T022 (22 tasks) = working textbook with RAG chatbot.

## Outcome

- Impact: Complete task breakdown enabling immediate implementation. Each task has exact file paths and clear deliverables.
- Tests: Format validation — all 41 tasks follow `- [ ] [ID] [P?] [Story?] Description with file path` format.
- Files: specs/008-textbook-generation/tasks.md
- Next prompts: `/sp.implement` to begin executing tasks, or `/sp.analyze` to validate cross-artifact consistency.
- Reflection: US3 (Ingestion) ordered before US2 (Chatbot) because chatbot depends on ingested content. This is a deviation from spec priority ordering but is the correct execution order.

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.ps1 resolved FEATURE_DIR outside repo. Worked around by using known repo path.
- Graders run and results (PASS/FAIL): Format validation — PASS (41/41 tasks compliant).
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.implement to validate task executability.
