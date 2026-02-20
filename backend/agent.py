"""RAG orchestration for the textbook chatbot.

Uses OpenRouter (via openai SDK) for chat completions.
Embeddings come from the configured backend (Ollama locally, HF in production).
Retrieval is handled directly against Qdrant — no agent framework overhead needed
for a single-tool, grounded RAG pipeline.
"""

import os
import re

from openai import AsyncOpenAI
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from embeddings import embed_texts

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CHAT_MODEL = os.getenv("OPENROUTER_CHAT_MODEL", "qwen/qwen3-30b-a3b")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "textbook-passages"

# Qdrant client
_qdrant: QdrantClient | None = None
if QDRANT_URL and QDRANT_API_KEY:
    _qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


# Greeting patterns — detected before RAG to skip embedding entirely
_GREETING_PATTERN = re.compile(
    r"^\s*(hi|hello|hey|howdy|greetings|good\s+(morning|afternoon|evening|day)|"
    r"what'?s\s+up|sup|yo|hiya|salaam|salam|assalam|namaste|bonjour|hola|ciao)"
    r"[\s!.,?]*$",
    re.IGNORECASE,
)

GREETING_RESPONSE = (
    "Hello! I'm your teaching assistant for the **Humanoid Robotics: Physical AI** textbook.\n\n"
    "I can help you with any topic from the six parts:\n"
    "- **Part 1** — Introduction to Physical AI\n"
    "- **Part 2** — Basics of Humanoid Robotics (URDF, kinematics, actuators)\n"
    "- **Part 3** — ROS 2 Fundamentals (nodes, topics, services, rclpy)\n"
    "- **Part 4** — Digital Twin Simulation (Gazebo, Isaac Sim, sensors)\n"
    "- **Part 5** — Vision-Language-Action Systems (Whisper, LLM planning)\n"
    "- **Part 6** — Capstone Project\n\n"
    "What would you like to explore?"
)

SYSTEM_PROMPT = """You are a friendly and helpful teaching assistant for the "Humanoid Robotics: Physical AI" textbook.

RULES:
1. When the user greets you (hi, hello, good morning, etc.), respond warmly and introduce yourself and the textbook topics. Do NOT refuse a greeting.
2. For content questions, answer based on the provided textbook context. Cite the Part and Section for key claims.
3. If the context does not contain enough information to answer a content question, say: "I don't have enough information from the textbook to answer that. Try asking about: Introduction to Physical AI, Humanoid Robotics, ROS 2, Digital Twin Simulation, Vision-Language-Action Systems, or the Capstone project."
4. For questions clearly unrelated to the textbook (weather, sports, news, etc.), politely redirect: "I'm focused on the textbook content. Feel free to ask me about humanoid robotics, ROS 2, simulation, or VLA systems!"
5. Preserve all book-specific terminology exactly as it appears in the source.
6. Keep answers concise and technically precise.

Textbook structure:
- Part 1: Introduction to Physical AI
- Part 2: Basics of Humanoid Robotics (URDF, kinematics, actuators)
- Part 3: ROS 2 Fundamentals (nodes, topics, services, rclpy)
- Part 4: Digital Twin Simulation (Gazebo, Isaac Sim, sensors)
- Part 5: Vision-Language-Action Systems (Whisper, LLM planning, voice-to-action)
- Part 6: Capstone (voice command → plan → navigate → perceive → manipulate)"""


def _search_qdrant(query_embedding: list[float], limit: int = 5) -> list[dict]:
    """Search Qdrant for passages similar to the query embedding."""
    if not _qdrant:
        return []
    results = _qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=limit,
        with_payload=True,
    )
    passages = []
    for r in results:
        p = r.payload or {}
        passages.append({
            "text": p.get("text", ""),
            "source": p.get("source", ""),
            "part": p.get("part", ""),
            "part_number": p.get("part_number", 0),
            "section": p.get("section", ""),
            "chunk_index": p.get("chunk_index", 0),
            "score": r.score,
        })
    return passages


async def run_rag_query(
    question: str,
    selected_text: str | None = None,
    conversation_history: list[dict] | None = None,
) -> dict:
    """Run the RAG pipeline: retrieve → assemble context → generate answer.

    Args:
        question: User's question.
        selected_text: Optional text highlighted on the page.
        conversation_history: Optional list of {question, answer} for multi-turn.

    Returns:
        Dict with answer, sources, retrieval_mode.
    """
    retrieval_mode = "selected_text" if selected_text else "full_book"
    sources: list[dict] = []
    context_parts: list[str] = []

    # Short-circuit: greetings don't need RAG — answer directly
    if not selected_text and _GREETING_PATTERN.match(question):
        return {
            "answer": GREETING_RESPONSE,
            "sources": [],
            "retrieval_mode": "greeting",
        }

    if selected_text:
        # Selected-text mode: highlighted text is the primary context
        context_parts.append(
            f"[PRIMARY — text selected by the learner on the page]\n{selected_text}"
        )
        sources.append({
            "text": selected_text[:200],
            "source": "user-selected",
            "part": "Selected Text",
            "part_number": 0,
            "section": "User Selection",
            "chunk_index": 0,
            "is_primary": True,
        })
        # Supplement with related Qdrant passages
        try:
            q_text = f"{question} {selected_text[:400]}"
            q_emb = embed_texts([q_text])[0]
            for p in _search_qdrant(q_emb, limit=3):
                context_parts.append(
                    f"[SUPPLEMENTARY — {p['part']} > {p['section']}]\n{p['text']}"
                )
                sources.append({
                    "text": p["text"][:200],
                    "source": p["source"],
                    "part": p["part"],
                    "part_number": p["part_number"],
                    "section": p["section"],
                    "chunk_index": p["chunk_index"],
                    "is_primary": False,
                })
        except Exception:
            pass  # Supplementary search failure is non-fatal

    else:
        # Full-book mode: embed question → search Qdrant
        q_emb = embed_texts([question])[0]
        passages = _search_qdrant(q_emb, limit=5)
        if not passages:
            return {
                "answer": "The textbook content is still being indexed. Please try again shortly.",
                "sources": [],
                "retrieval_mode": retrieval_mode,
            }
        for p in passages:
            context_parts.append(
                f"[{p['part']} > {p['section']}]\n{p['text']}"
            )
            sources.append({
                "text": p["text"][:200],
                "source": p["source"],
                "part": p["part"],
                "part_number": p["part_number"],
                "section": p["section"],
                "chunk_index": p["chunk_index"],
                "is_primary": False,
            })

    context = "\n\n---\n\n".join(context_parts)

    # Build messages
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add last 3 conversation turns for multi-turn context
    for turn in (conversation_history or [])[-3:]:
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})

    if selected_text:
        user_content = (
            f"The learner highlighted this passage from the textbook:\n\n"
            f'"{selected_text}"\n\n'
            f"Supplementary context:\n\n{context}\n\n"
            f"Question: {question}"
        )
    else:
        user_content = (
            f"Context from the textbook:\n\n{context}\n\n"
            f"Question: {question}"
        )

    messages.append({"role": "user", "content": user_content})

    # Generate answer via OpenRouter
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    try:
        response = await client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
        )
        answer = response.choices[0].message.content or "No answer generated."
    except Exception as e:
        raise RuntimeError(f"Chat generation failed: {e}")

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_mode": retrieval_mode,
    }
