# Feature Specification: AI-Native Textbook with RAG Chatbot

**Feature Branch**: `008-textbook-generation`
**Created**: 2026-02-01
**Status**: Draft
**Input**: User description: "Build an AI-native textbook on humanoid robotics with a RAG chatbot, using Docusaurus with auto sidebar, RAG backend (Qdrant + Neon), free-tier embeddings, optional Urdu translation and personalize chapter."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read and Navigate the Textbook (Priority: P1)

A learner visits the textbook site and browses through a structured, six-part curriculum covering Physical AI, Humanoid Robotics, ROS 2, Digital Twin Simulation, Vision-Language-Action Systems, and a Capstone project. The sidebar auto-generates from the content hierarchy, allowing the learner to jump between chapters, sections, and modules without friction. Each chapter loads quickly and renders code blocks, diagrams, and structured content clearly.

**Why this priority**: The textbook is the single source of truth (Constitution Principle VII). Without navigable, well-structured book content, no other feature (RAG, translation) delivers value. This is the foundational deliverable.

**Independent Test**: Can be fully tested by deploying the Docusaurus site with all six parts populated, verifying that every chapter renders correctly and the auto-generated sidebar reflects the full book structure.

**Acceptance Scenarios**:

1. **Given** the textbook site is deployed, **When** a learner visits the homepage, **Then** they see the book title, a brief introduction, and a table of contents linking to all six parts.
2. **Given** the sidebar is rendered, **When** a learner expands any part, **Then** they see all chapters within that part listed in curriculum order.
3. **Given** a chapter contains code examples, **When** the learner views the chapter, **Then** code blocks render with syntax highlighting and are copy-able.
4. **Given** the learner is on any chapter page, **When** they look at the sidebar, **Then** their current location is visually indicated and they can navigate to any other chapter.

---

### User Story 2 - Ask the RAG Chatbot a Book Question (Priority: P1)

A learner encounters a concept they don't understand while reading (e.g., "What is a URDF model?" or "How does Nav2 work in Isaac Sim?"). They open the chatbot widget on the textbook site, type their question in natural language, and receive an answer grounded strictly in the book's content. The answer cites the relevant module and chapter so the learner can read further.

**Why this priority**: The RAG chatbot is the core differentiator of this AI-native textbook (Constitution Principle I — Dual-System Alignment). It transforms passive reading into interactive learning. Without it, this is just another static textbook.

**Independent Test**: Can be tested by ingesting at least one chapter, asking questions about its content, and verifying that answers are accurate, cited, and grounded in the book.

**Acceptance Scenarios**:

1. **Given** book content has been ingested, **When** a learner asks "What is a URDF model?", **Then** the chatbot returns an answer sourced from the ROS 2 chapter with a citation to the relevant section.
2. **Given** the chatbot is active, **When** a learner asks a question outside the book's scope (e.g., "What is the weather?"), **Then** the chatbot politely refuses and redirects to book-related topics.
3. **Given** the chatbot is active, **When** a learner asks a question, **Then** the response appears within 5 seconds.
4. **Given** the chatbot has returned an answer, **When** the learner reads the cited source, **Then** the answer is consistent with the source material.

---

### User Story 3 - Ingest Book Content into the RAG Knowledge Base (Priority: P1)

An author or maintainer writes or updates book chapters in Markdown. The system processes these chapters, splits them into meaningful passages, generates embeddings using a free-tier embedding service, and stores them in a vector database. When chapters are updated, the system re-ingests without creating duplicate entries.

**Why this priority**: Without ingestion, the RAG chatbot has no knowledge base to draw from. This is a prerequisite for User Story 2 and must work reliably for the system to function.

**Independent Test**: Can be tested by running the ingestion pipeline on a set of Markdown files and verifying that passages are stored, retrievable via semantic search, and free of duplicates after re-ingestion.

**Acceptance Scenarios**:

1. **Given** a set of Markdown chapter files, **When** the ingestion pipeline runs, **Then** all chapters are processed and their passages stored in the vector database.
2. **Given** a chapter has been previously ingested, **When** the same chapter is ingested again after an update, **Then** old passages are replaced (not duplicated) and new content is reflected.
3. **Given** the ingestion pipeline completes, **When** a semantic search is performed for a known concept, **Then** the relevant passage is returned with its source chapter and section metadata.
4. **Given** the full textbook (6 parts), **When** ingestion runs end-to-end, **Then** it completes within 5 minutes.

---

### User Story 4 - Module Navigation Assistance (Priority: P2)

A learner is unsure which module to study next or wants to understand how modules connect. They ask the chatbot questions like "What should I learn after ROS 2?" or "How does the Digital Twin module relate to the Capstone?" The chatbot uses the book's curriculum structure to guide the learner through the learning path.

**Why this priority**: Curriculum guidance enhances the learning experience but is not essential for core functionality. The textbook and basic Q&A (P1 stories) must work first.

**Independent Test**: Can be tested by asking curriculum-navigation questions and verifying the chatbot responds with accurate module relationships and learning path guidance drawn from the book structure.

**Acceptance Scenarios**:

1. **Given** the learner asks "What comes after ROS 2?", **When** the chatbot responds, **Then** it identifies the Digital Twin module as the next step and explains the connection.
2. **Given** the learner asks "How do all modules connect to the Capstone?", **When** the chatbot responds, **Then** it describes the integration pipeline (perception, planning, control, action) as defined in the Capstone chapter.

---

### User Story 5 - Browse Textbook in Urdu (Priority: P3)

A learner who prefers Urdu selects the Urdu language option. The textbook interface and chapter content display in Urdu where translations are available. Untranslated content falls back to English gracefully.

**Why this priority**: Urdu translation broadens accessibility but is optional and can be added incrementally after the English textbook and RAG system are complete.

**Independent Test**: Can be tested by enabling the Urdu locale, navigating to a translated chapter, and verifying Urdu content renders correctly with proper RTL support. Navigating to an untranslated chapter should show English content.

**Acceptance Scenarios**:

1. **Given** the Urdu locale is enabled, **When** the learner navigates to a chapter that has an Urdu translation, **Then** the content displays in Urdu with correct right-to-left formatting.
2. **Given** the Urdu locale is enabled, **When** the learner navigates to a chapter without an Urdu translation, **Then** the content displays in English with a notice that translation is not yet available.
3. **Given** the learner switches between English and Urdu, **When** they are on any page, **Then** the language toggle is visible and switching is instant without page reload artifacts.

---

### User Story 6 - Personalized Learning Chapter (Priority: P3)

A learner accesses a "Personalize Your Learning" chapter that helps them assess their background and recommends a study path. The chapter may include self-assessment questions or interactive elements that guide the learner to the most relevant starting point based on their prior knowledge (e.g., "I know ROS 2 already" leads to skipping Module 1).

**Why this priority**: Personalization adds value but is a secondary enhancement. The core textbook and RAG system must function first.

**Independent Test**: Can be tested by navigating to the personalization chapter, completing a self-assessment, and verifying that the recommended path aligns with the stated prior knowledge.

**Acceptance Scenarios**:

1. **Given** a learner visits the personalization chapter, **When** they indicate prior experience with ROS 2, **Then** the chapter recommends starting at Module 2 (Digital Twin) and explains what they can skip.
2. **Given** a learner has no prior experience, **When** they complete the self-assessment, **Then** the chapter recommends the full sequential path starting from Module 1.

---

### Edge Cases

- What happens when the RAG chatbot receives a question in a language other than English? The chatbot responds in English and indicates that only English queries are fully supported (Urdu support is limited to translated content browsing, not chatbot interaction).
- What happens when the vector database is empty (no content ingested)? The chatbot displays a message indicating that content is being prepared and to check back later.
- What happens when the embedding service is unavailable during ingestion? The system logs the failure, reports which chapters failed, and allows retry without re-processing successful chapters.
- What happens when a chapter contains no meaningful text (only images or diagrams)? The ingestion pipeline logs a warning and skips the chapter, noting it in the ingestion report.
- What happens when multiple learners query the chatbot simultaneously? The system handles concurrent queries without degradation up to the defined capacity.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render a six-part textbook with the following structure: (1) Introduction to Physical AI, (2) Basics of Humanoid Robotics, (3) ROS 2 Fundamentals, (4) Digital Twin Simulation (Gazebo + Isaac), (5) Vision-Language-Action Systems, (6) Capstone.
- **FR-002**: System MUST auto-generate the sidebar navigation from the content file hierarchy without manual sidebar configuration.
- **FR-003**: System MUST provide a chatbot interface accessible from any textbook page that accepts natural language questions.
- **FR-004**: System MUST retrieve relevant passages from the book's content using semantic search and generate answers grounded strictly in the retrieved content.
- **FR-005**: System MUST cite the source module and chapter/section in every chatbot answer.
- **FR-006**: System MUST refuse questions outside the book's scope with a polite redirect to book-related topics.
- **FR-007**: System MUST ingest Markdown chapter files into a vector database, splitting content into meaningful passages with source metadata (part, chapter, section).
- **FR-008**: System MUST handle re-ingestion of updated chapters without creating duplicate passages.
- **FR-009**: System MUST use a free-tier embedding service to generate vector representations of passages.
- **FR-010**: System MUST store passage vectors and metadata in a vector database for retrieval.
- **FR-011**: System MUST store structured data (ingestion logs, query history, user interactions) in a relational database.
- **FR-012**: System MUST support Urdu as an optional locale with right-to-left rendering and graceful English fallback for untranslated content.
- **FR-013**: System MUST include a personalization chapter with self-assessment that recommends a study path based on prior knowledge.
- **FR-014**: System MUST preserve all book-specific terminology as defined in the constitution (no invented concepts, no hallucination beyond documented material).
- **FR-015**: System MUST log all chatbot queries and responses for observability.
- **FR-016**: System MUST return meaningful error messages when the chatbot cannot process a query (e.g., empty knowledge base, service unavailable).

### Key Entities

- **Part**: A top-level division of the textbook (6 total). Contains an ordered set of chapters. Has a title, sequence number, and description.
- **Chapter**: A unit of content within a Part. Contains sections, code examples, and explanatory text. Has a title, sequence within its Part, and Markdown source.
- **Passage**: A semantically meaningful chunk of a Chapter, created during ingestion. Has text content, a vector embedding, and source metadata (Part, Chapter, Section).
- **Query**: A learner's natural language question submitted to the chatbot. Has the question text, timestamp, and associated response.
- **Response**: The chatbot's answer to a Query. Has answer text, cited source passages, and confidence metadata.
- **Locale**: A language configuration (English default, Urdu optional). Determines content rendering direction and translation availability.

### Assumptions

- The textbook is authored in Markdown and built with Docusaurus (per constitution).
- The six-part book structure maps to the constitution's four modules plus an Introduction and Capstone, aligning with Constitution Principle II (Curriculum Integrity).
- Free-tier embedding services (e.g., Hugging Face Inference API or similar) provide sufficient quality for educational RAG without cost.
- Qdrant is used as the vector database and Neon (serverless Postgres) as the relational database, as specified in the technical requirements.
- The chatbot operates in English only for Q&A; Urdu support is limited to content display.
- A single ingestion pipeline processes all chapters; incremental chapter-level re-ingestion is supported.
- The personalization chapter uses static self-assessment content (not AI-generated personalization at runtime).
- The target audience is technically proficient learners (per Constitution Principle III — Code-First Technical Depth).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six textbook parts are browsable with auto-generated sidebar reflecting the complete book hierarchy.
- **SC-002**: Learners receive chatbot answers within 5 seconds (p95) for any question about the book's content.
- **SC-003**: 90% of chatbot answers are accurate when verified against the source material (manual evaluation on a 50-question test set).
- **SC-004**: 100% of out-of-scope questions are refused with a polite redirect (tested against a 20-question out-of-scope set).
- **SC-005**: Full textbook ingestion completes within 5 minutes.
- **SC-006**: Re-ingestion of an updated chapter produces zero duplicate passages.
- **SC-007**: The system supports at least 10 concurrent chatbot queries without response degradation.
- **SC-008**: Urdu-translated chapters render correctly with RTL layout and English fallback works for untranslated chapters.
- **SC-009**: The personalization chapter self-assessment produces a valid study path recommendation for all defined learner profiles.
- **SC-010**: Every chatbot answer includes at least one source citation (module, chapter, or section reference).
