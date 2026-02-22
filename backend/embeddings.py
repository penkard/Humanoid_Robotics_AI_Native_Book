"""Embedding client with Ollama (local) and HuggingFace (production) backends.

Strategy:
- Local dev: Ollama nomic-embed-text (768D, free, no API key)
- Production: HuggingFace Inference API all-MiniLM-L6-v2 (384D) or
              any OpenAI-compatible endpoint via EMBEDDING_BACKEND env var

Set EMBEDDING_BACKEND=ollama (default) or hf in your .env.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "ollama")

# Ollama settings (local)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# HuggingFace settings (production fallback)
HF_API_TOKEN = os.getenv("HUGGING_FACE_API_KEY") or os.getenv("HF_API_TOKEN", "")
HF_MODEL = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
HF_API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{HF_MODEL}"

# Resolved at import time so ingest.py can reference it for VECTOR_DIM
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))

BATCH_SIZE = 32


def _embed_ollama(texts: list[str]) -> list[list[float]]:
    """Embed texts using local Ollama nomic-embed-text."""
    all_embeddings: list[list[float]] = []
    for text in texts:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": OLLAMA_MODEL, "prompt": text},
            timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(f"Ollama embedding error {resp.status_code}: {resp.text}")
        embedding = resp.json().get("embedding", [])
        if not embedding:
            raise RuntimeError("Ollama returned empty embedding.")
        all_embeddings.append(embedding)
    return all_embeddings


def _embed_hf(texts: list[str]) -> list[list[float]]:
    """Embed texts using HuggingFace Inference API."""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        resp = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": batch, "options": {"wait_for_model": True}},
            timeout=60,
        )
        if not resp.ok:
            raise RuntimeError(f"HF embedding API error {resp.status_code}: {resp.text}")
        all_embeddings.extend(resp.json())
    return all_embeddings


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using the configured backend.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors.

    Raises:
        RuntimeError: If the embedding API call fails.
    """
    if not texts:
        return []

    backend = EMBEDDING_BACKEND.lower()

    if backend == "ollama":
        return _embed_ollama(texts)
    elif backend == "hf":
        return _embed_hf(texts)
    else:
        raise RuntimeError(f"Unknown EMBEDDING_BACKEND: {backend!r}. Use 'ollama' or 'hf'.")
