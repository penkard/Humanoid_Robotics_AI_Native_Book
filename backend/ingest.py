"""Markdown-aware ingestion pipeline for the textbook RAG system.

Processes docs/Part-*/ Markdown files into Qdrant with rich metadata,
deduplication on re-ingestion, and logging to Neon Postgres.
Uses OpenRouter Qwen3 embeddings (1024 dimensions by default).
"""

import glob
import hashlib
import os
import time

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

from chunker import chunk_markdown
from embeddings import embed_texts, EMBEDDING_DIMENSIONS
from db import (
    create_ingestion_run,
    log_ingestion_chapter,
    update_ingestion_run,
)

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "textbook-passages"
VECTOR_DIM = EMBEDDING_DIMENSIONS  # 768 from nomic-embed-text (Ollama), configurable via env


def _get_qdrant_client() -> QdrantClient:
    """Get a Qdrant client instance."""
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise RuntimeError("QDRANT_URL or QDRANT_API_KEY not set.")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def _ensure_collection(client: QdrantClient):
    """Create or recreate the textbook-passages collection with correct dimensions."""
    try:
        info = client.get_collection(COLLECTION_NAME)
        current_dim = info.config.params.vectors.size
        if current_dim != VECTOR_DIM:
            print(f"Collection has {current_dim} dims, need {VECTOR_DIM}. Recreating...")
            client.delete_collection(COLLECTION_NAME)
            raise Exception("Recreate needed")
    except Exception:
        print(f"Creating collection '{COLLECTION_NAME}' ({VECTOR_DIM} dims, COSINE)...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_DIM, distance=models.Distance.COSINE
            ),
        )
        print("Collection created.")


def _deterministic_id(source: str, section: str, chunk_index: int) -> str:
    """Generate a deterministic point ID from source + section + chunk_index."""
    key = f"{source}:{section}:{chunk_index}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _find_docs_path() -> str:
    """Detect the docs/ directory relative to repo root."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "docs"),
        os.path.join(os.getcwd(), "..", "docs"),
        os.path.join(os.getcwd(), "docs"),
    ]
    for candidate in candidates:
        abs_path = os.path.abspath(candidate)
        if os.path.isdir(abs_path):
            return abs_path
    raise RuntimeError("Cannot find docs/ directory.")


def _find_chapter_files(
    docs_path: str, specific_chapters: list[str] | None = None
) -> list[str]:
    """Find all Markdown chapter files in docs/Part-*/."""
    if specific_chapters:
        files = []
        for ch in specific_chapters:
            if os.path.isabs(ch):
                path = ch
            else:
                path = os.path.join(docs_path, ch)
            if os.path.isfile(path):
                files.append(path)
        return files

    pattern = os.path.join(docs_path, "Part-*", "**", "*.md")
    files = glob.glob(pattern, recursive=True)
    return sorted([f for f in files if f.endswith(".md")])


def run_ingestion(specific_chapters: list[str] | None = None) -> dict:
    """Run the full ingestion pipeline.

    Args:
        specific_chapters: Optional list of chapter paths for selective re-ingestion.

    Returns:
        Dict with run_id, status, totals, chapter results, and duration.
    """
    start_time = time.time()
    client = _get_qdrant_client()
    _ensure_collection(client)

    docs_path = _find_docs_path()
    files = _find_chapter_files(docs_path, specific_chapters)
    print(f"Found {len(files)} chapter files to process.")

    # Create ingestion run in Neon
    run_id = None
    try:
        run_id = create_ingestion_run()
    except Exception as e:
        print(f"Warning: Could not log to Neon: {e}")

    total_passages = 0
    chapter_results = []

    for filepath in files:
        rel_path = os.path.relpath(filepath, os.path.dirname(docs_path))
        print(f"Processing: {rel_path}")

        try:
            # Chunk the markdown
            chunks = chunk_markdown(filepath)
            if not chunks:
                print(f"  Skipped (no content): {rel_path}")
                chapter_results.append(
                    {"source_path": rel_path, "status": "skipped", "passages_created": 0}
                )
                if run_id:
                    try:
                        log_ingestion_chapter(run_id, rel_path, 0, "", 0, "skipped")
                    except Exception:
                        pass
                continue

            # Extract part_number and chapter for logging
            part_number = chunks[0].get("part_number", 0)
            chapter_title = chunks[0].get("chapter", "")

            # Delete existing points for this source (deduplication)
            source_value = chunks[0].get("source", "")
            try:
                client.delete(
                    collection_name=COLLECTION_NAME,
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="source",
                                    match=models.MatchValue(value=source_value),
                                )
                            ]
                        )
                    ),
                )
            except Exception:
                pass  # Collection may be empty

            # Generate embeddings via OpenRouter Qwen3
            texts = [c["text"] for c in chunks]
            embeddings = embed_texts(texts)

            # Upsert points with deterministic IDs
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = _deterministic_id(
                    chunk["source"], chunk["section"], chunk["chunk_index"]
                )
                # Convert hex ID to integer for Qdrant
                int_id = int(point_id, 16) % (2**63)
                points.append(
                    models.PointStruct(
                        id=int_id,
                        vector=embedding,
                        payload=chunk,
                    )
                )

            client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
            print(f"  Upserted {len(points)} passages from {rel_path}")

            total_passages += len(points)
            chapter_results.append(
                {
                    "source_path": rel_path,
                    "status": "success",
                    "passages_created": len(points),
                }
            )

            if run_id:
                try:
                    log_ingestion_chapter(
                        run_id, rel_path, part_number, chapter_title, len(points), "success"
                    )
                except Exception:
                    pass

        except Exception as e:
            print(f"  Error processing {rel_path}: {e}")
            chapter_results.append(
                {
                    "source_path": rel_path,
                    "status": "failed",
                    "passages_created": 0,
                    "error": str(e),
                }
            )
            if run_id:
                try:
                    log_ingestion_chapter(
                        run_id, rel_path, 0, "", 0, "failed", str(e)
                    )
                except Exception:
                    pass

    duration = time.time() - start_time
    status = "completed" if all(c["status"] != "failed" for c in chapter_results) else "failed"

    # Update ingestion run in Neon
    if run_id:
        try:
            update_ingestion_run(
                run_id, status, len(files), total_passages,
                error_message=None if status == "completed" else "Some chapters failed"
            )
        except Exception:
            pass

    result = {
        "run_id": run_id or 0,
        "status": status,
        "total_chapters": len(files),
        "total_passages": total_passages,
        "duration_seconds": round(duration, 2),
        "chapters": chapter_results,
    }

    print(f"\nIngestion complete: {total_passages} passages from {len(files)} chapters in {duration:.1f}s")
    return result


def main():
    """CLI entry point for ingestion."""
    print("Starting ingestion pipeline...")
    print(f"Embedding model: {os.getenv('OPENROUTER_EMBEDDING_MODEL', 'qwen/qwen3-embedding-0.6b')}")
    print(f"Vector dimensions: {VECTOR_DIM}")
    result = run_ingestion()
    print(f"\nRun ID: {result['run_id']}")
    print(f"Status: {result['status']}")
    print(f"Total chapters: {result['total_chapters']}")
    print(f"Total passages: {result['total_passages']}")
    print(f"Duration: {result['duration_seconds']}s")


if __name__ == "__main__":
    main()
