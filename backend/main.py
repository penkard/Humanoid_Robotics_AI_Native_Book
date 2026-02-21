"""FastAPI backend for the AI-native textbook RAG chatbot.

Uses OpenRouter for embeddings (Qwen3) and chat completions,
with OpenAI Agents SDK orchestration. Supports full-book and
selected-text retrieval modes with session tracking.
"""

import os
import time
import uuid

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import get_connection, log_query, init_db, ensure_session, get_session_history
from agent import run_rag_query

# --- Configuration ---
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI(title="Textbook RAG Chatbot API", version="3.0.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://physical-ai-textbook.vercel.app",
    "https://penkard.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---

class QueryRequest(BaseModel):
    question: str | None = None
    query: str | None = None  # backwards compatibility
    selected_text: str | None = None
    session_id: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    latency_ms: float
    retrieval_mode: str
    session_id: str


class IngestRequest(BaseModel):
    chapters: list[str] | None = None


class IngestResponse(BaseModel):
    run_id: int
    status: str
    total_chapters: int
    total_passages: int
    duration_seconds: float
    chapters: list[dict]


class HealthResponse(BaseModel):
    status: str
    services: dict


# --- Ingestion state ---
_ingestion_running = False


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check connectivity to Qdrant, Neon, OpenRouter embedding and chat APIs."""
    services = {}

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        if QDRANT_URL and QDRANT_API_KEY:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
            client.get_collections()
            services["qdrant"] = "connected"
        else:
            services["qdrant"] = "disconnected"
    except Exception:
        services["qdrant"] = "disconnected"

    # Check Neon
    try:
        conn = get_connection()
        conn.close()
        services["neon"] = "connected"
    except Exception:
        services["neon"] = "disconnected"

    # Check OpenRouter Embedding API
    try:
        from embeddings import embed_texts, EMBEDDING_DIMENSIONS
        test_result = embed_texts(["health check"])
        if test_result and len(test_result[0]) == EMBEDDING_DIMENSIONS:
            services["embedding_api"] = "available"
        else:
            services["embedding_api"] = "unavailable"
    except Exception:
        services["embedding_api"] = "unavailable"

    # Check OpenRouter Chat API
    try:
        from openai import OpenAI
        if OPENROUTER_API_KEY:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
            response = client.chat.completions.create(
                model=os.getenv("OPENROUTER_CHAT_MODEL", "qwen/qwen3-30b-a3b"),
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            services["chat_api"] = "available"
        else:
            services["chat_api"] = "unavailable"
    except Exception:
        services["chat_api"] = "unavailable"

    # Determine overall status
    values = list(services.values())
    if all(v in ("connected", "available") for v in values):
        status = "healthy"
    elif any(v in ("connected", "available") for v in values):
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(status=status, services=services)


@app.post("/query", response_model=QueryResponse)
async def query_handler(request: QueryRequest):
    """Handle chatbot queries with RAG retrieval and OpenRouter generation."""
    question = request.question or request.query
    if not question:
        raise HTTPException(status_code=422, detail="Missing question field.")

    # Validate question length
    if len(question) > 2000:
        raise HTTPException(status_code=422, detail="Question too long. Please keep it under 2000 characters.")

    # Validate selected_text length
    if request.selected_text and len(request.selected_text) > 5000:
        raise HTTPException(status_code=422, detail="Selected text too long. Please select a shorter passage.")

    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=503, detail="OpenRouter API not configured.")

    start_time = time.time()

    # Handle session
    session_id = request.session_id or str(uuid.uuid4())
    try:
        ensure_session(session_id)
    except Exception:
        pass  # Session tracking failure is non-fatal

    # Get conversation history for multi-turn context
    conversation_history = []
    try:
        conversation_history = get_session_history(session_id)
    except Exception:
        pass

    # Run RAG pipeline
    try:
        result = await run_rag_query(
            question=question,
            selected_text=request.selected_text,
            conversation_history=conversation_history,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Query processing failed: {e}")

    latency_ms = (time.time() - start_time) * 1000

    # Log query to Neon (non-blocking, don't fail if DB is down)
    try:
        log_query(
            question=question,
            answer=result["answer"],
            sources=result["sources"],
            latency_ms=latency_ms,
            session_id=session_id,
            retrieval_mode=result["retrieval_mode"],
            selected_text=request.selected_text,
        )
    except Exception:
        pass

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        latency_ms=latency_ms,
        retrieval_mode=result["retrieval_mode"],
        session_id=session_id,
    )


@app.post("/ingest", response_model=IngestResponse)
async def trigger_ingestion(request: IngestRequest | None = None):
    """Trigger content ingestion pipeline."""
    global _ingestion_running
    if _ingestion_running:
        raise HTTPException(status_code=409, detail="Ingestion already in progress.")

    from ingest import run_ingestion

    chapters = request.chapters if request else None
    _ingestion_running = True
    try:
        result = run_ingestion(specific_chapters=chapters)
        return IngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _ingestion_running = False


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    try:
        init_db()
        print("Database tables initialized.")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")


if __name__ == "__main__":
    print("Starting FastAPI server (v3.0.0)...")
    print(f"Chat model: {os.getenv('OPENROUTER_CHAT_MODEL', 'qwen/qwen3-30b-a3b')}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
