# Quickstart: 008-textbook-generation

**Branch**: `008-textbook-generation` | **Date**: 2026-02-01

## Prerequisites

- Node.js >= 20.0
- Python >= 3.11
- Git
- Accounts: Qdrant Cloud (free tier), Neon (free tier), Hugging Face (free API token)

## 1. Clone and Install Frontend

```bash
cd Humanoid_Robotics_Native_book
npm install
```

## 2. Configure Environment

Create `backend/.env`:

```env
# Qdrant Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres
DATABASE_URL=postgresql://user:password@your-project.neon.tech/textbook?sslmode=require

# Hugging Face (free-tier embeddings)
HF_API_TOKEN=hf_your_token_here

# Google Gemini (answer generation)
GEMINI_API_KEY=your-gemini-api-key
```

## 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

`requirements.txt` will include:
```
fastapi
uvicorn
qdrant-client
python-dotenv
google-genai
psycopg2-binary
requests
```

## 4. Initialize Database

```bash
python -c "from db import init_db; init_db()"
```

This creates the `query_logs`, `ingestion_runs`, and `ingestion_chapters` tables in Neon.

## 5. Ingest Book Content

```bash
python ingest.py
```

Processes all `docs/Part-*/` Markdown files into Qdrant.

## 6. Start Backend

```bash
python main.py
# Server runs at http://localhost:8000
```

## 7. Start Frontend

```bash
cd ..  # back to repo root
npm start
# Opens http://localhost:3000
```

## 8. Verify

- Visit http://localhost:3000 — textbook should render with auto-sidebar
- Open chat widget (bottom-right) and ask: "What is a URDF model?"
- Check http://localhost:8000/health for service connectivity

## Development Workflow

1. Edit chapter content in `docs/Part-*/`
2. Re-ingest: `POST /ingest` or `python ingest.py`
3. Frontend hot-reloads automatically on content changes
4. Backend requires restart for code changes (or use `uvicorn main:app --reload`)

## Adding Urdu Translations

```bash
npm run write-translations -- --locale ur
# Creates i18n/ur/ skeleton
# Add translated .md files to i18n/ur/docusaurus-plugin-content-docs/current/
npm start -- --locale ur
# Preview Urdu version
```
