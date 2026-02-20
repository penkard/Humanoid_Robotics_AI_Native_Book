# Research: RAG Chatbot Integration

**Feature**: 009-rag-chatbot-integration
**Date**: 2026-02-17
**Status**: Complete

## R-001: OpenRouter Embeddings API

**Decision**: Use OpenRouter's OpenAI-compatible embeddings endpoint with Qwen3-Embedding model.

**Rationale**: OpenRouter provides a unified API for both embeddings and chat completions, eliminating the need for separate HF and Gemini API keys. The Qwen3 embedding family offers strong multilingual performance and Matryoshka Representation Learning (MRL) for flexible dimensionality.

**Findings**:
- **Endpoint**: `POST https://openrouter.ai/api/v1/embeddings`
- **Auth**: `Authorization: Bearer <OPENROUTER_API_KEY>`
- **Request format** (OpenAI-compatible):
  ```json
  {
    "model": "qwen/qwen3-embedding-8b",
    "input": ["text to embed"],
    "dimensions": 1024
  }
  ```
- **Response format**:
  ```json
  {
    "data": [{"embedding": [0.1, 0.2, ...], "index": 0}],
    "model": "qwen/qwen3-embedding-8b",
    "usage": {"prompt_tokens": 5, "total_tokens": 5}
  }
  ```

**Available Qwen3 Embedding Models via OpenRouter**:

| Model | ID | Max Dims | Pricing |
|-------|----|----------|---------|
| Qwen3-Embedding-8B | `qwen/qwen3-embedding-8b` | 4096 | $0.01/M tokens |
| Qwen3-Embedding-4B | `qwen/qwen3-embedding-4b` | 2560 | $0.02/M tokens |
| Qwen3-Embedding-0.6B | `qwen/qwen3-embedding-0.6b` | 1024 | $0.006/M tokens |

**Selected model**: `qwen/qwen3-embedding-0.6b` at 1024 dimensions.
- **Why**: Qdrant free tier has storage limits. 1024 dims offers strong semantic quality while keeping vectors 2.7x smaller than 384→1024 migration (actually 2.67x larger than current 384, but 4x smaller than 4096). The 0.6B model is cheapest and sufficient for a textbook with ~500 passages.
- **MRL support**: Can reduce to 512 or 256 dims if storage becomes an issue, with minimal quality loss.

**Alternatives considered**:
- Qwen3-Embedding-8B (4096 dims): Better quality but 4x storage cost. Overkill for educational textbook.
- Keep HF all-MiniLM-L6-v2 (384 dims): Lower quality, separate API dependency.

---

## R-002: OpenRouter Chat Completions API

**Decision**: Use OpenRouter for LLM generation, replacing Google Gemini.

**Rationale**: Consolidates all AI API calls through a single provider (OpenRouter). Access to a wide range of models without vendor lock-in.

**Findings**:
- **Endpoint**: `POST https://openrouter.ai/api/v1/chat/completions`
- **Request format** (OpenAI-compatible):
  ```json
  {
    "model": "qwen/qwen3-30b-a3b",
    "messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ],
    "max_tokens": 1024
  }
  ```
- **Streaming**: Supported via `"stream": true` (SSE format)
- **Models considered for generation**:
  - `qwen/qwen3-30b-a3b`: Strong reasoning, cost-effective ($0.10/$0.30 per M tokens)
  - `google/gemini-2.0-flash-001`: Fast, cheap, familiar from 008
  - `meta-llama/llama-4-maverick`: Good quality, competitive pricing

**Selected model**: `qwen/qwen3-30b-a3b` (default, configurable via env var).
- **Why**: Keeps the entire stack on Qwen for consistency. Good reasoning for RAG grounding. Cost-effective for educational use.

**Alternatives considered**:
- Gemini Flash via OpenRouter: Still viable as fallback; same API format.
- Direct Gemini API: Would require separate SDK and auth; rejected for simplicity.

---

## R-003: OpenAI Agents SDK for RAG Orchestration

**Decision**: Use OpenAI Agents SDK (`openai-agents` v0.9+) with OpenRouter as custom provider to orchestrate the multi-step RAG pipeline.

**Rationale**: Provides structured tool calling, conversation management, and a clean abstraction for the retrieve → assemble → generate pipeline. Works with any OpenAI-compatible endpoint including OpenRouter.

**Findings**:
- **Package**: `pip install openai-agents`
- **Custom provider setup**:
  ```python
  from openai import AsyncOpenAI
  from agents import Agent, Runner, set_default_openai_client, function_tool

  client = AsyncOpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=os.getenv("OPENROUTER_API_KEY"),
  )
  set_default_openai_client(client)
  ```
- **Agent definition**:
  ```python
  agent = Agent(
      name="textbook-rag-bot",
      instructions=SYSTEM_PROMPT,
      model="qwen/qwen3-30b-a3b",
      tools=[retrieve_passages, retrieve_selected_context],
  )
  ```
- **Tool definition** for retrieval:
  ```python
  @function_tool
  def retrieve_passages(query: str) -> str:
      """Search the textbook for passages relevant to the query."""
      # Embed query, search Qdrant, return formatted passages
      ...
  ```
- **Runner** for execution:
  ```python
  result = await Runner.run(agent, messages)
  answer = result.final_output
  ```

**Key advantages**:
- Built-in tool calling: Agent decides when to use retrieval
- Conversation context: Multi-turn support via message history
- Structured output: Can enforce citation format
- Streaming support: `Runner.run_streamed()` for SSE

**Alternatives considered**:
- LangChain: Heavier dependency, more abstraction than needed.
- Raw OpenAI SDK calls: Possible but lacks tool orchestration.
- ChatKit SDK: Better suited for frontend chat UI, not backend orchestration. Could complement Agents SDK for the frontend but adds complexity beyond what's needed for a Docusaurus widget.

---

## R-004: Qdrant Collection Migration (384 → 1024 dims)

**Decision**: Create a new Qdrant collection with 1024-dimension vectors, re-ingest all content.

**Rationale**: Vector dimensions must match the embedding model. Migrating from HF 384-dim to Qwen 1024-dim requires a new collection. The existing `textbook-passages` collection will be replaced.

**Findings**:
- Qdrant free tier supports up to 1GB storage
- 1024-dim vectors at ~500 passages ≈ 2MB vector storage (well within limits)
- Collection must be recreated (cannot resize vectors in place)
- Payload schema remains the same (text, source, part, part_number, chapter, section, chunk_index)

**Migration plan**:
1. Delete existing `textbook-passages` collection
2. Create new collection with `size=1024, distance=COSINE`
3. Re-ingest all content using Qwen embeddings via OpenRouter
4. Update `VECTOR_DIM` constant from 384 to 1024

---

## R-005: Selected-Text Retrieval Mode

**Decision**: Frontend captures highlighted text via `window.getSelection()` and sends it alongside the question to the backend. Backend uses the selected text as primary context, optionally supplemented by Qdrant retrieval.

**Rationale**: This is the key differentiator (US2). The frontend already exists as a React widget; adding text selection capture is straightforward JavaScript.

**Findings**:
- **Frontend**: `window.getSelection().toString()` captures highlighted text
- **Trigger**: When user opens chatbot with text selected, show "Ask about this selection" prompt
- **API change**: `POST /query` gains optional `selected_text` field
- **Backend logic**:
  1. If `selected_text` is provided → use it as primary context
  2. Optionally embed selected text → search Qdrant for related passages
  3. Assemble context: selected text first, then supplementary passages
  4. Generate answer with citation indicating "Selected passage" as primary source
- **Edge cases**: Code-only selections, very short selections (<20 chars), empty selections

---

## R-006: Session Management

**Decision**: Use simple session ID tracking via Neon Postgres. No complex session state on the backend.

**Rationale**: The spec requires Session as a key entity for multi-turn context. A lightweight approach avoids over-engineering while enabling query grouping and conversation history retrieval.

**Findings**:
- **Session ID**: Generated client-side (UUID), sent with each query
- **Storage**: New `sessions` table in Neon with `session_id`, `created_at`, `last_active_at`
- **Query association**: `query_logs` gains a `session_id` column
- **Conversation context**: Last N messages from same session sent to LLM for multi-turn
- **No server-side state**: Each request is self-contained; session is reconstructed from DB

---

## R-007: Environment Variable Changes

**Decision**: Replace HF_API_TOKEN and GEMINI_API_KEY with OPENROUTER_API_KEY.

**Current `.env`**:
```
QDRANT_URL=...
QDRANT_API_KEY=...
DATABASE_URL=...
HF_API_TOKEN=...
GEMINI_API_KEY=...
```

**New `.env`**:
```
QDRANT_URL=...
QDRANT_API_KEY=...
DATABASE_URL=...
OPENROUTER_API_KEY=...
OPENROUTER_EMBEDDING_MODEL=qwen/qwen3-embedding-0.6b
OPENROUTER_CHAT_MODEL=qwen/qwen3-30b-a3b
EMBEDDING_DIMENSIONS=1024
```

**Rationale**: Single API key for all AI services. Model names configurable via env for easy switching.
