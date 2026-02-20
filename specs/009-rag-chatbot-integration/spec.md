# Feature Specification: RAG Chatbot Integration

**Feature Branch**: `009-rag-chatbot-integration`
**Created**: 2026-02-16
**Status**: Draft
**Input**: User description: "Define the full specification for integrating a RAG chatbot into my Docusaurus book. Requirements: chatbot embedded in published book, Frontend: Docusaurus (static site on Vercel), Backend: FastAPI, LLM: OpenRouter API, Embeddings: Qwen via OpenRouter, Vector DB: Qdrant Cloud, Metadata DB: Neon Serverless Postgres, Orchestration: OpenAI Agents / ChatKit SDKs. Core features: book-only answers, full-book + selected-text retrieval modes, citations, no hallucination, re-indexing on change."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask a Full-Book Question (Priority: P1)

A learner is reading the textbook and encounters a concept they want to understand better. They open the chatbot widget embedded in the book page, type a natural language question (e.g., "What is a URDF model?"), and receive an answer that is grounded strictly in the book's content. The answer includes citations referencing the specific Part, chapter, and section where the information was found, with clickable links to navigate directly to the source material.

**Why this priority**: This is the core value proposition of the RAG chatbot. Without full-book Q&A, the chatbot delivers no value. Every other feature builds on this foundation.

**Independent Test**: Ingest at least one Part of the book, ask questions about its content, verify answers are accurate, cited, and grounded. Ask an out-of-scope question and verify polite refusal.

**Acceptance Scenarios**:

1. **Given** book content has been ingested into the vector database, **When** a learner asks "What is a URDF model?", **Then** the chatbot returns an answer sourced from the textbook with a citation to the relevant Part and section.
2. **Given** the chatbot is active, **When** a learner asks a question outside the book's scope (e.g., "What is the weather today?"), **Then** the chatbot politely refuses and redirects to book-related topics.
3. **Given** the chatbot is active, **When** a learner asks a question, **Then** the response appears within 5 seconds.
4. **Given** the chatbot has returned an answer, **When** the learner clicks a citation link, **Then** they are navigated to the exact chapter and section in the textbook.
5. **Given** the chatbot has returned an answer, **When** the learner reads the cited source, **Then** the answer is consistent with the source material (no hallucination).

---

### User Story 2 - Ask About Selected Text (Priority: P1)

A learner is reading a specific passage and wants deeper explanation. They highlight a block of text on the page, and the chatbot widget offers a contextual prompt (e.g., "Ask about this selection"). The learner types a question, and the chatbot answers using only the selected text as the primary context, optionally supplemented by related passages from the full book. The answer cites the selected passage and any additional sources used.

**Why this priority**: Selected-text retrieval is a core differentiator. It transforms the chatbot from a generic Q&A tool into a context-aware reading companion. This mode enables precise, focused answers that directly address what the learner is currently reading.

**Independent Test**: Highlight a paragraph on a textbook page, ask a question about it, verify the answer is primarily grounded in the selected text with appropriate citations.

**Acceptance Scenarios**:

1. **Given** a learner has highlighted a block of text on a textbook page, **When** they open the chatbot and ask a question, **Then** the chatbot uses the highlighted text as primary context for the answer.
2. **Given** selected text is provided, **When** the chatbot generates an answer, **Then** the answer cites the selected passage and indicates it was the primary source.
3. **Given** selected text is provided but the question requires broader context, **When** the chatbot generates an answer, **Then** it supplements the selected text with additional relevant passages from the full book and cites both sources.
4. **Given** a learner has no text selected, **When** they ask a question, **Then** the chatbot defaults to full-book retrieval mode (User Story 1 behavior).

---

### User Story 3 - Re-Index Book Content (Priority: P2)

An author or maintainer updates one or more chapters of the textbook. They trigger a re-indexing process that processes the changed content, generates new embeddings, and updates the vector database. The system handles this without creating duplicate entries and without requiring a full re-ingestion of unchanged content.

**Why this priority**: Re-indexing is essential for maintaining the chatbot's accuracy as the book evolves, but it is a maintenance operation rather than a user-facing feature. The chatbot must work first (US1, US2) before re-indexing becomes relevant.

**Independent Test**: Modify a chapter's content, trigger re-indexing, verify the updated content is reflected in chatbot answers and old content is not duplicated.

**Acceptance Scenarios**:

1. **Given** a chapter has been modified, **When** re-indexing is triggered, **Then** the updated content replaces old entries without creating duplicates.
2. **Given** the full textbook (6 parts), **When** full re-indexing runs, **Then** it completes within 5 minutes.
3. **Given** re-indexing is triggered for specific chapters, **When** the process completes, **Then** only those chapters are re-processed while other chapters remain unchanged.
4. **Given** re-indexing completes, **When** a learner asks a question about the updated content, **Then** the chatbot reflects the latest changes.

---

### User Story 4 - Monitor Chatbot Health and Usage (Priority: P3)

A maintainer checks the system's health and reviews chatbot usage patterns. They access a health endpoint to verify all services (vector DB, metadata DB, embedding API, LLM API) are operational. They review query logs to understand what learners are asking, identify unanswered questions, and measure response latency.

**Why this priority**: Observability is important for production operations but is not required for core chatbot functionality. It can be added after the chatbot is working.

**Independent Test**: Hit the health endpoint and verify accurate service status reporting. Submit queries and verify they appear in the metadata database with correct timestamps and latency measurements.

**Acceptance Scenarios**:

1. **Given** all backend services are running, **When** the health endpoint is queried, **Then** it returns the connectivity status of each service (vector DB, metadata DB, embedding API, LLM API).
2. **Given** a learner asks a question, **When** the response is generated, **Then** the question, answer, cited sources, and response latency are logged to the metadata database.
3. **Given** the metadata database contains query logs, **When** a maintainer queries the logs, **Then** they can see usage patterns including most-asked topics, average latency, and error rates.

---

### Edge Cases

- What happens when the embedding API (OpenRouter) is temporarily unavailable? The system returns a user-friendly error message and logs the failure. Previously cached results remain available.
- What happens when the LLM API (OpenRouter) is temporarily unavailable? The system returns an error message suggesting the learner try again shortly. The retrieved passages are still available for display without a generated answer.
- What happens when the vector database is empty (no content ingested)? The chatbot displays a message: "Content is being prepared. Please check back later."
- What happens when a learner sends an extremely long question (>2000 characters)? The system truncates the query to a reasonable length and processes it, or returns a validation error asking the learner to shorten their question.
- What happens when the selected text contains only code blocks or images with no meaningful prose? The system informs the learner that the selection doesn't contain enough text to answer questions about and suggests selecting a passage with explanatory text.
- What happens when multiple learners query simultaneously? The system handles concurrent queries without degradation up to the defined capacity.
- What happens when a learner asks a question in a language other than English? The chatbot responds in English and indicates that only English queries are currently supported.
- What happens when re-indexing is triggered while a query is in progress? The query completes normally; re-indexing does not block active queries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a chatbot interface accessible from any page of the published textbook, rendered as an embedded widget.
- **FR-002**: System MUST accept natural language questions and generate answers grounded strictly in the book's content using retrieval-augmented generation.
- **FR-003**: System MUST support two retrieval modes: (a) full-book retrieval, where the entire indexed content is searched, and (b) selected-text retrieval, where user-highlighted text is used as primary context.
- **FR-004**: System MUST include citations in every chatbot answer, referencing the specific Part, chapter, and section from which the information was sourced.
- **FR-005**: System MUST refuse questions outside the book's scope with a polite redirect to book-related topics.
- **FR-006**: System MUST NOT generate answers that contain information not present in the retrieved passages (no hallucination beyond retrieved content).
- **FR-007**: System MUST generate vector embeddings for book passages using the Qwen embedding model accessed via the OpenRouter API.
- **FR-008**: System MUST store passage vectors and metadata in a vector database for semantic retrieval.
- **FR-009**: System MUST store structured data (query logs, ingestion records, session history) in a relational metadata database.
- **FR-010**: System MUST support re-indexing of updated chapters without creating duplicate entries in the vector database.
- **FR-011**: System MUST support selective re-indexing (specific chapters) and full re-indexing (entire book).
- **FR-012**: System MUST provide a health check endpoint reporting the connectivity status of all external services.
- **FR-013**: System MUST log every chatbot query and response, including cited sources and response latency, to the metadata database.
- **FR-014**: System MUST preserve all book-specific terminology as used in the source material.
- **FR-015**: System MUST return meaningful error messages when services are unavailable (empty knowledge base, API failures, rate limits).
- **FR-016**: System MUST guard against concurrent re-indexing operations (only one at a time).
- **FR-017**: System MUST transmit the selected text from the frontend to the backend when the learner uses selected-text retrieval mode.
- **FR-018**: System MUST use an orchestration framework to manage the multi-step RAG pipeline (embedding, retrieval, context assembly, generation).

### Key Entities

- **Part**: A top-level division of the textbook (6 total). Has a title, sequence number, and description.
- **Chapter**: A unit of content within a Part. Contains sections, code examples, and explanatory text.
- **Passage**: A semantically meaningful chunk of a Chapter, created during ingestion. Has text content, a vector embedding, and source metadata (Part, chapter, section, chunk index).
- **Query**: A learner's natural language question submitted to the chatbot. Has the question text, optional selected text, retrieval mode, timestamp, and associated response.
- **Response**: The chatbot's answer to a Query. Has answer text, cited source passages, retrieval mode used, and latency.
- **Ingestion Run**: A record of a re-indexing operation. Tracks start time, end time, chapters processed, passages created, and status.
- **Session**: A logical grouping of queries from a single learner interaction. Tracks conversation context for multi-turn interactions.

### Assumptions

- The textbook is authored in Markdown and built with Docusaurus, deployed as a static site on Vercel.
- The backend is a separately deployed FastAPI application.
- LLM access for answer generation is provided via the OpenRouter API, which exposes an OpenAI-compatible chat completions endpoint.
- Embeddings are generated using a Qwen embedding model accessed through the OpenRouter API.
- Qdrant Cloud (free tier) is used as the vector database for storing passage embeddings and metadata.
- Neon serverless Postgres is used as the metadata database for query logs, ingestion records, and session data.
- The OpenAI Agents SDK and/or ChatKit SDK are used for orchestrating the multi-step RAG pipeline.
- The chatbot operates in English only for Q&A.
- The selected-text feature requires JavaScript running on the client side to capture highlighted text and send it to the backend.
- Free-tier service limits are acceptable for the educational context (single-digit concurrent users).
- The existing 6-part textbook structure (Part 1 through Part 6) is the content source.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Learners receive chatbot answers within 5 seconds (p95) for any question about the book's content.
- **SC-002**: 90% of chatbot answers are accurate when verified against the source material (evaluated on a 50-question test set).
- **SC-003**: 100% of out-of-scope questions are refused with a polite redirect (tested against a 20-question out-of-scope set).
- **SC-004**: Every chatbot answer includes at least one source citation referencing a specific Part, chapter, or section.
- **SC-005**: Full textbook re-indexing completes within 5 minutes.
- **SC-006**: Re-indexing of an updated chapter produces zero duplicate passages.
- **SC-007**: The system supports at least 10 concurrent chatbot queries without response degradation.
- **SC-008**: Selected-text retrieval mode produces answers that reference the selected passage as the primary source in at least 95% of cases.
- **SC-009**: All external service statuses are accurately reported by the health check endpoint.
- **SC-010**: 100% of chatbot interactions are logged to the metadata database with question, answer, sources, and latency.
