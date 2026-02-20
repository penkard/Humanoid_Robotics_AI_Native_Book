# Research: 008-textbook-generation

**Branch**: `008-textbook-generation` | **Date**: 2026-02-01 | **Phase**: 0

## R-001: Free-Tier Embedding Service Selection

**Decision**: Use Hugging Face Inference API with `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) as the primary free-tier embedding model.

**Rationale**:
- The existing codebase uses Google `text-embedding-004` (768 dims) which requires a paid API key. The spec mandates free-tier embeddings (FR-009).
- Hugging Face Inference API provides free access to open-source embedding models with generous rate limits for educational use.
- `all-MiniLM-L6-v2` is widely benchmarked, produces 384-dim vectors (lower storage cost in Qdrant), and performs well on semantic search tasks.
- Alternative: `BAAI/bge-small-en-v1.5` (384 dims) — slightly better benchmarks but less community adoption.

**Alternatives Considered**:
1. **Google text-embedding-004**: Current implementation. Not free-tier — requires API key with billing.
2. **OpenAI text-embedding-3-small**: Requires paid API key.
3. **Cohere embed-english-light-v3.0**: Free tier exists but with strict rate limits (100 calls/min).
4. **Local sentence-transformers**: Eliminates API dependency but requires Python environment with torch (~2GB). Viable as fallback.

**Migration Impact**: Existing Qdrant collection (`hackathon-book`, 768 dims) must be recreated with 384 dims. Full re-ingestion required.

## R-002: Neon (Serverless Postgres) Integration

**Decision**: Use Neon serverless Postgres for structured data: query logs, ingestion records, and user interaction history.

**Rationale**:
- FR-011 requires a relational database for structured data (ingestion logs, query history).
- FR-015 requires logging all chatbot queries and responses.
- Neon provides a generous free tier (0.5 GB storage, 190 compute hours/month) suitable for an educational project.
- Qdrant handles vector storage; Neon handles everything else (separation of concerns).

**Alternatives Considered**:
1. **SQLite**: Zero-config but no cloud access, no concurrent writes from multiple processes.
2. **Supabase Postgres**: Free tier available but adds unnecessary complexity (auth, realtime) for this use case.
3. **PlanetScale (MySQL)**: Free tier discontinued.

**Schema Needs**: `query_logs`, `ingestion_runs`, `ingestion_chapters` tables (see data-model.md).

## R-003: Docusaurus i18n for Urdu Translation

**Decision**: Use Docusaurus built-in i18n framework with `ur` locale for Urdu support.

**Rationale**:
- Docusaurus v3 has first-class i18n support with directory-based locale management.
- RTL rendering is handled automatically when the locale is configured with `direction: 'rtl'`.
- Content fallback to the default locale (English) is built-in — untranslated pages show English automatically.
- No third-party translation libraries needed.

**Alternatives Considered**:
1. **Manual RTL CSS**: Error-prone, doesn't handle sidebar/navbar direction.
2. **Third-party i18n plugin**: Unnecessary; Docusaurus i18n covers all requirements.

**Implementation Pattern**:
```
docs/                          # English (default)
i18n/ur/docusaurus-plugin-content-docs/current/   # Urdu translations
```

## R-004: Book Structure Alignment with Constitution

**Decision**: Map the user's 6-part structure to the constitution's module structure as follows:

| User Part | Constitution Module | Directory |
|-----------|-------------------|-----------|
| 1. Introduction to Physical AI | (Preamble) | `docs/Part-1-introduction/` |
| 2. Basics of Humanoid Robotics + ROS 2 | Module 1: ROS 2 | `docs/Part-2-ros2/` |
| 3. Digital Twin Simulation | Module 2: Gazebo & Unity | `docs/Part-3-digital-twin/` |
| 4. Vision-Language-Action Systems | Module 3: Isaac + Module 4: VLA | `docs/Part-4-vla/` |
| 5. (merged into Part 4) | — | — |
| 6. Capstone | Capstone | `docs/Part-5-capstone/` |

**Rationale**:
- The user's 6-part structure splits Module 3 (Isaac) and Module 4 (VLA) into separate parts. The existing `hackathon-book/docs` already has a 5-part structure that aligns with the constitution.
- The constitution explicitly states the module structure is non-negotiable (Principle II). The user's "Basics of Humanoid Robotics" maps naturally to the ROS 2 module's URDF humanoid modeling content.
- Keeping 6 parts is acceptable as long as all 4 constitutional modules and the capstone are preserved. The Introduction is additive, not a violation.

**Resolution**: Adopt 6 directories: Part-1 through Part-5 plus Capstone. This preserves all constitutional modules while honoring the user's requested structure.

| Directory | Content |
|-----------|---------|
| `docs/Part-1-introduction/` | Introduction to Physical AI |
| `docs/Part-2-humanoid-robotics/` | Basics of Humanoid Robotics (ROS 2, URDF) |
| `docs/Part-3-ros2/` | ROS 2 Fundamentals |
| `docs/Part-4-digital-twin/` | Digital Twin Simulation (Gazebo + Isaac) |
| `docs/Part-5-vla/` | Vision-Language-Action Systems |
| `docs/Part-6-capstone/` | Capstone Project |

## R-005: Chunking Strategy for RAG Ingestion

**Decision**: Use Markdown-aware chunking that splits on headings (`##`, `###`) with a fallback to 1000-character chunks for long sections.

**Rationale**:
- The existing `ingest.py` uses naive 1000-character splitting which can break mid-sentence and loses section boundaries.
- Markdown heading-based splitting preserves semantic boundaries (each chunk = one section or subsection).
- Source metadata (Part, Chapter, Section heading) can be extracted from the heading hierarchy.
- Fallback to character-based splitting handles unusually long sections.

**Alternatives Considered**:
1. **Fixed-size chunks (current)**: Loses section context, splits mid-code-block.
2. **Sentence-based splitting**: Better than character but still loses document structure.
3. **LangChain RecursiveCharacterTextSplitter**: Adds a heavy dependency for a simple operation.

## R-006: Duplicate Prevention on Re-Ingestion

**Decision**: Use deterministic point IDs based on `hash(source_path + section_heading + chunk_index)` instead of random UUIDs.

**Rationale**:
- FR-008 requires re-ingestion without duplicates.
- The existing `ingest.py` generates random UUIDs per chunk, making deduplication impossible.
- Deterministic IDs mean that upserting the same chunk overwrites the existing point rather than creating a duplicate.
- When a chapter is updated, changed chunks get new content at the same ID; deleted sections result in orphaned IDs that can be cleaned up by deleting all points for a source path before re-ingesting that chapter.

**Strategy**: Delete-then-insert per chapter (delete all points matching `source == chapter_path`, then insert new chunks).

## R-007: LLM for Answer Generation

**Decision**: Continue using Google Gemini (gemini-2.0-flash or latest free-tier model) for answer generation.

**Rationale**:
- The existing backend already uses Gemini for generation. Gemini provides a free tier (15 RPM, 1M tokens/day for flash models) which is sufficient for an educational chatbot.
- Switching to a different LLM provider adds unnecessary migration work.
- The spec's free-tier requirement applies to embeddings (FR-009). Generation can use any available API with a free tier.

**Alternatives Considered**:
1. **OpenAI GPT-4o-mini**: Good quality but requires paid API key for reliable access.
2. **Local Ollama**: Zero cost but requires local GPU/RAM and adds deployment complexity.
3. **Groq (Llama 3)**: Fast and free tier available, but less established for production use.
