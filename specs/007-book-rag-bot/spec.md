# Feature Specification: Book RAG Bot Backend

**Feature Branch**: `007-book-rag-bot`
**Created**: 2026-02-01
**Status**: Draft
**Input**: User description: "Build the Book RAG Bot backend grounded in book content"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask a Book Question (Priority: P1)

A student reading the book encounters a concept they want to
understand more deeply. They open the chat widget and type a
question. The bot retrieves relevant passages from the book and
returns a grounded answer using the book's terminology and
structure.

**Why this priority**: This is the core value proposition of the
RAG bot. Without accurate, grounded question answering, the bot
has no purpose.

**Independent Test**: A user types "What is a ROS 2 node?" and
receives an answer that references Module 1 content with accurate
definitions from the book.

**Acceptance Scenarios**:

1. **Given** the book content has been ingested into the knowledge
   base, **When** a student asks "What are the main components of
   ROS 2 architecture?", **Then** the bot returns an answer citing
   nodes, topics, and services as described in Module 1.
2. **Given** a student asks a question covered across multiple
   chapters, **When** the query is submitted, **Then** the bot
   synthesizes relevant passages from all matching sections and
   attributes them to specific modules.
3. **Given** a student asks a question not covered in the book,
   **When** the query is submitted, **Then** the bot responds with
   a concise message indicating the topic is outside the book's
   scope, without fabricating information.

---

### User Story 2 - Ingest Book Content (Priority: P1)

A content administrator needs to update the bot's knowledge base
whenever the book content changes. They run an ingestion process
that reads all book chapters, splits them into retrievable
passages, and stores them in the knowledge base so the bot's
answers reflect the latest content.

**Why this priority**: Without ingestion, the bot has no knowledge
to draw from. This is a prerequisite for all bot functionality.

**Independent Test**: After running ingestion on the book's
markdown files, verify that each chapter's content is searchable
and retrievable by the bot.

**Acceptance Scenarios**:

1. **Given** the book contains chapters across 4 modules and a
   preface, **When** the ingestion process runs, **Then** all
   chapter content is processed and stored in the knowledge base.
2. **Given** a chapter has been updated with new content, **When**
   ingestion is re-run, **Then** the knowledge base reflects the
   updated content without duplicating old passages.
3. **Given** the ingestion process encounters a malformed or empty
   file, **When** processing that file, **Then** it logs a warning
   and continues processing remaining files without failing.

---

### User Story 3 - Module Navigation Assistance (Priority: P2)

A student is unsure which module or chapter covers a specific
topic. They ask the bot for guidance, and it maps their question
to the relevant section(s) of the book, helping them navigate the
curriculum efficiently.

**Why this priority**: Navigation support enhances the learning
experience but is secondary to accurate question answering.

**Independent Test**: A user asks "Where do I learn about sensor
simulation?" and the bot directs them to Module 2 (Gazebo &
Unity) with a reference to the relevant chapter.

**Acceptance Scenarios**:

1. **Given** a student asks "Which module covers NVIDIA Isaac?",
   **When** the query is processed, **Then** the bot responds with
   Module 3 and lists the specific topics covered.
2. **Given** a student asks about a cross-cutting topic like
   "perception", **When** the query is processed, **Then** the bot
   identifies all modules where perception is discussed and
   summarizes each module's angle.

---

### User Story 4 - Greeting and Scope Boundaries (Priority: P3)

A user opens the chat and greets the bot or asks an off-topic
question. The bot responds appropriately: greeting the user warmly
for salutations, and politely declining off-topic questions while
redirecting to the book's scope.

**Why this priority**: Graceful boundary handling improves user
experience but is not core functionality.

**Independent Test**: A user says "Hello" and receives a friendly
greeting. A user asks "What is the weather?" and receives a
polite redirect to book-related topics.

**Acceptance Scenarios**:

1. **Given** a user sends a greeting like "Hi" or "Hello",
   **When** the message is received, **Then** the bot responds
   with a friendly greeting and a brief description of what it
   can help with.
2. **Given** a user asks an off-topic question unrelated to the
   book, **When** the message is processed, **Then** the bot
   responds indicating it can only help with topics covered in
   the book and suggests example questions.

---

### Edge Cases

- What happens when the knowledge base is empty (ingestion has
  not been run)? The bot MUST return a helpful error message
  indicating content is not yet available.
- How does the system handle very long questions (>500 words)?
  The system MUST truncate or summarize the query input to a
  reasonable length before retrieval.
- What happens when the knowledge base service is unreachable?
  The bot MUST return a user-friendly error message rather than
  an unhandled exception.
- How does the system handle concurrent users asking questions
  simultaneously? The system MUST handle at least 10 concurrent
  requests without degradation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept natural language questions from
  users and return answers grounded exclusively in book content.
- **FR-002**: System MUST ingest all book chapter files and store
  them as retrievable passages in a knowledge base.
- **FR-003**: System MUST retrieve the most relevant passages for
  a given question using semantic similarity search.
- **FR-004**: System MUST generate answers that cite or reference
  the specific module and chapter where the information originates.
- **FR-005**: System MUST refuse to answer questions outside the
  book's scope with a polite, informative redirect.
- **FR-006**: System MUST handle re-ingestion without duplicating
  previously stored content.
- **FR-007**: System MUST respond to user greetings with a
  friendly message describing its capabilities.
- **FR-008**: System MUST return meaningful error messages when
  the knowledge base is unavailable or empty.
- **FR-009**: System MUST log all queries and responses for
  operational monitoring.
- **FR-010**: System MUST preserve the book's terminology and
  structure in all generated answers (no invented concepts).

### Key Entities

- **Book Chapter**: A markdown document representing a section of
  the book. Key attributes: title, module association, content
  body, file path.
- **Passage**: A retrievable chunk of a book chapter. Key
  attributes: text content, source chapter, position within
  chapter, semantic embedding.
- **Query**: A user's natural language question. Key attributes:
  question text, timestamp, source (chat widget).
- **Response**: The bot's generated answer. Key attributes:
  answer text, source passages referenced, confidence/relevance
  indicators.

### Assumptions

- The book content is authored in Markdown format and stored in
  a known directory structure organized by module.
- The chat widget (frontend) already exists and communicates with
  the backend via a standard request/response pattern.
- Secrets and API keys are managed via environment configuration,
  never hardcoded.
- The bot serves a single book (not multiple books or courses).
- Users are authenticated implicitly by having access to the
  deployed book site; no separate login is required.
- The ingestion process is triggered manually by an administrator,
  not automatically on every content change.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users receive answers to book-related questions
  within 5 seconds of submitting their query, 95% of the time.
- **SC-002**: 90% of answers to in-scope questions reference the
  correct module and chapter as verified by manual review of a
  sample set.
- **SC-003**: 100% of out-of-scope questions receive a polite
  decline rather than a fabricated answer.
- **SC-004**: The ingestion process completes for all book
  chapters (currently ~10 files) within 2 minutes.
- **SC-005**: The system handles at least 10 concurrent user
  queries without errors or significant response degradation.
- **SC-006**: After re-ingestion, no duplicate passages exist in
  the knowledge base for unchanged content.
