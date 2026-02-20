"""Neon Postgres database module for query logs, sessions, and ingestion records."""

import json
import os
from datetime import datetime, timezone

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Get a new database connection."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create tables if they do not exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id UUID PRIMARY KEY,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_active_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            cur.execute("""
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
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ingestion_runs (
                    id SERIAL PRIMARY KEY,
                    started_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    total_chapters INTEGER,
                    total_passages INTEGER,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT
                );
            """)
            cur.execute("""
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
            """)
            conn.commit()
    finally:
        conn.close()


def ensure_session(session_id: str) -> str:
    """Create or update a session record. Returns the session_id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO sessions (id, last_active_at)
                   VALUES (%s, NOW())
                   ON CONFLICT (id) DO UPDATE SET last_active_at = NOW()
                   RETURNING id""",
                (session_id,),
            )
            result = cur.fetchone()[0]
            conn.commit()
            return str(result)
    finally:
        conn.close()


def get_session_history(session_id: str, limit: int = 6) -> list[dict]:
    """Get recent query history for a session (for multi-turn context).

    Returns list of {question, answer} dicts, oldest first.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT question, answer FROM query_logs
                   WHERE session_id = %s
                   ORDER BY created_at DESC LIMIT %s""",
                (session_id, limit),
            )
            rows = cur.fetchall()
            return [{"question": r[0], "answer": r[1]} for r in reversed(rows)]
    finally:
        conn.close()


def log_query(
    question: str,
    answer: str,
    sources: list,
    latency_ms: float,
    session_id: str | None = None,
    retrieval_mode: str = "full_book",
    selected_text: str | None = None,
):
    """Log a chatbot query and response."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO query_logs
                   (session_id, question, answer, sources, retrieval_mode, selected_text, latency_ms)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (session_id, question, answer, json.dumps(sources),
                 retrieval_mode, selected_text, latency_ms),
            )
            conn.commit()
    finally:
        conn.close()


def create_ingestion_run() -> int:
    """Create a new ingestion run record. Returns the run ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ingestion_runs (status) VALUES ('running') RETURNING id"""
            )
            run_id = cur.fetchone()[0]
            conn.commit()
            return run_id
    finally:
        conn.close()


def update_ingestion_run(
    run_id: int,
    status: str,
    total_chapters: int = 0,
    total_passages: int = 0,
    error_message: str | None = None,
):
    """Update an ingestion run with final results."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE ingestion_runs
                   SET completed_at = NOW(), status = %s,
                       total_chapters = %s, total_passages = %s,
                       error_message = %s
                   WHERE id = %s""",
                (status, total_chapters, total_passages, error_message, run_id),
            )
            conn.commit()
    finally:
        conn.close()


def log_ingestion_chapter(
    run_id: int,
    source_path: str,
    part_number: int,
    chapter_title: str,
    passages_created: int,
    status: str,
    error_message: str | None = None,
):
    """Log an individual chapter's ingestion result."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ingestion_chapters
                   (run_id, source_path, part_number, chapter_title,
                    passages_created, status, error_message)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    run_id,
                    source_path,
                    part_number,
                    chapter_title,
                    passages_created,
                    status,
                    error_message,
                ),
            )
            conn.commit()
    finally:
        conn.close()
