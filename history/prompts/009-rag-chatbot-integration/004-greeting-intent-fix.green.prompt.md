---
id: 004
title: Greeting Intent Detection Fix
stage: green
date: 2026-02-19
surface: agent
model: claude-sonnet-4-6
feature: 009-rag-chatbot-integration
branch: 009-rag-chatbot-integration
user: penka
command: manual fix
labels: ["greeting", "intent-detection", "ux", "system-prompt"]
links:
  spec: specs/009-rag-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/agent.py
tests:
  - "hi" => greeting mode, instant welcome: PASS
  - "hello" => greeting mode, instant welcome: PASS
  - "good morning" => greeting mode, instant welcome: PASS
  - "salaam" => greeting mode, instant welcome: PASS
  - "Hey there!" => full_book mode, LLM responds warmly: PASS
  - "What is a URDF model?" => full_book mode, RAG answer: PASS
  - "What is the weather today?" => full_book mode, polite redirect: PASS
---

## Prompt

make sure that the bot must answer when the user greets and answer clearly

## Response snapshot

Added greeting short-circuit in `agent.py`:
1. `_GREETING_PATTERN` regex matches hi/hello/good morning/salaam/namaste/hola etc. before any embedding call.
2. `GREETING_RESPONSE` constant returns instant welcome listing all 6 textbook parts — zero latency.
3. Updated `SYSTEM_PROMPT` rule 1 to explicitly allow warm greeting responses from the LLM for edge cases regex misses.
4. Rule 4 changed from curt refusal to polite redirect for off-topic questions.

## Outcome

- Impact: Bot now greets users warmly; no more "I can only answer questions about the textbook content" on hi/hello
- Tests: 7/7 PASS
- Files: backend/agent.py (1 file, ~30 lines added)
- Next prompts: /sp.git.commit_pr to commit all 009 work
- Reflection: Greeting intent should bypass RAG entirely — it wastes embedding latency and confuses the LLM's grounding rules. A simple regex is the correct tool here, not RAG.

## Evaluation notes (flywheel)

- Failure modes observed: System prompt "STRICT RULES" caused LLM to apply grounding rules to greetings, treating them as off-topic queries.
- Graders run and results: 7/7 PASS
- Prompt variant: none
- Next experiment: Add "thank you", "bye", "who are you" as additional non-RAG intents if users report them
