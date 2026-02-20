# Data Model: RAG Chatbot Integration

**Feature**: 009-rag-chatbot-integration
**Date**: 2026-02-17

## Entities

### 1. Passage (Qdrant Vector DB)

Stored as Qdrant points in the `textbook-passages` collection.

| Field | Type | Description |
|-------|------|-------------|
| id | int64 | Deterministic ID from SHA-256(source:section:chunk_index) |
| vector | float[1024] | Qwen3 embedding (1024 dimensions via OpenRouter) |
| text | string (payload) | Full passage text |
| source | string (payload) | Relative file path (e.g., `docs/Part-3-ros2/01-nodes-topics.md`) |
| part | string (payload) | Part title (e.g., "ROS 2 Fundamentals") |
| part_number | int (payload) | Part sequence number (1-6) |
| chapter | string (payload) | Chapter title |
| section | string (payload) | Section heading (H2/H3) |
| chunk_index | int (payload) | Chunk position within the chapter |

**Changes from 008**: Vector dimension changes from 384 → 1024. Collection must be recreated.

### 2. Session (Neon Postgres)

New table for tracking conversation sessions.

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. QueryLog (Neon Postgres)

Extended from existing `query_logs` table.

```sql
CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources JSONB,
    retrieval_mode VARCHAR(20) DEFAULT 'full_book',
    selected_text TEXT,
    latency_ms REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**New columns**: `session_id`, `retrieval_mode` ('full_book' | 'selected_text'), `selected_text`.

### 4. IngestionRun (Neon Postgres)

No changes from 008.

```sql
CREATE TABLE IF NOT EXISTS ingestion_runs (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    total_chapters INTEGER,
    total_passages INTEGER,
    status VARCHAR(20) NOT NULL,
    error_message TEXT
);
```

### 5. IngestionChapter (Neon Postgres)

No changes from 008.

```sql
CREATE TABLE IF NOT EXISTS ingestion_chapters (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES ingestion_runs(id),
    source_path TEXT NOT NULL,
    part_number INTEGER NOT NULL,
    chapter_title TEXT,
    passages_created INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    error_message TEXT
);
```

## Entity Relationships

```
Session 1 --- * QueryLog
QueryLog * --- * Passage (via sources JSONB)
IngestionRun 1 --- * IngestionChapter
IngestionChapter 1 --- * Passage (via source_path)
```

## State Transitions

### IngestionRun
```
running → completed
running → failed
```

### Query Retrieval Mode
```
(no selected_text) → full_book mode
(selected_text present) → selected_text mode
```

## Validation Rules

- `session_id`: Must be a valid UUID v4
- `question`: Max 2000 characters (FR from edge cases)
- `selected_text`: Max 5000 characters (reasonable passage length)
- `retrieval_mode`: Enum of 'full_book' | 'selected_text'
- `sources` JSONB: Array of objects with `text`, `source`, `part`, `section` fields
