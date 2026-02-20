---
id: 002
title: RAG Chatbot Plan Creation
stage: plan
date: 2026-02-17
surface: agent
model: claude-opus-4-6
feature: 009-rag-chatbot-integration
branch: 009-rag-chatbot-integration
user: penka
command: /sp.plan
labels: ["plan", "rag", "openrouter", "qwen", "agents-sdk", "selected-text"]
links:
  spec: specs/009-rag-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-rag-chatbot-integration/plan.md
  - specs/009-rag-chatbot-integration/research.md
  - specs/009-rag-chatbot-integration/data-model.md
  - specs/009-rag-chatbot-integration/quickstart.md
  - specs/009-rag-chatbot-integration/contracts/openapi.yaml
tests:
  - Constitution check: all 8 principles PASS
  - No NEEDS CLARIFICATION markers remain
---

## Prompt

sure, do the remaining work

(Interpreted as: continue with /sp.plan for feature 009-rag-chatbot-integration after spec was completed)

## Response snapshot

Completed full /sp.plan workflow for 009-rag-chatbot-integration. Phase 0 research resolved all technology choices: OpenRouter Qwen3-Embedding-0.6B (1024D, $0.006/M tokens) for embeddings, Qwen3-30B-A3B for chat completions, OpenAI Agents SDK v0.9+ for orchestration with custom OpenRouter provider. Phase 1 produced 5 artifacts: research.md (7 research items), data-model.md (5 entities with SQL schemas), contracts/openapi.yaml (OpenAPI 3.1 with selected-text mode), quickstart.md (developer setup guide), and plan.md (technical context, constitution check, project structure, 5 design decisions, migration plan). Updated CLAUDE.md agent context with correct technology stack.

## Outcome

- Impact: Complete implementation plan for RAG chatbot upgrade with OpenRouter + Qwen3 + Agents SDK + selected-text mode
- Tests: Constitution check 8/8 PASS, no NEEDS CLARIFICATION markers
- Files: plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml, CLAUDE.md
- Next prompts: /sp.tasks to generate implementation tasks, or /sp.adr for architectural decisions
- Reflection: The migration from HF+Gemini to unified OpenRouter simplifies operations (1 API key vs 2). Selected-text mode is the key differentiator requiring frontend JS integration with window.getSelection().

## Evaluation notes (flywheel)

- Failure modes observed: update-agent-context.ps1 reads plan from wrong path (C:\Users\penka\specs\ instead of repo root); manually corrected CLAUDE.md
- Graders run and results (PASS/FAIL): Constitution check PASS
- Prompt variant (if applicable): none
- Next experiment: Validate OpenRouter Qwen3-Embedding-0.6b actually returns 1024D vectors with dimensions param before implementation
