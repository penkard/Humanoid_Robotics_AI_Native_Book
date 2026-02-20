<!--
  Sync Impact Report
  ==================
  Version change: 0.0.0 (template) → 1.0.0
  Modified principles: N/A (initial creation from template)
  Added sections:
    - Principle I: Dual-System Alignment
    - Principle II: Curriculum Integrity
    - Principle III: Code-First Technical Depth
    - Principle IV: Book-Bound RAG Intelligence
    - Principle V: Clean Instrument UI
    - Principle VI: Precise Technical Tone
    - Principle VII: Single Source of Truth
    - Principle VIII: Embodied North Star
    - Section: Content Structure & Module Rules
    - Section: Development Workflow
    - Governance rules
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md — Constitution Check
      section references generic gates; ✅ compatible (gates are
      derived at plan time from this constitution)
    - .specify/templates/spec-template.md — ✅ no conflicts;
      user-story structure is module-agnostic
    - .specify/templates/tasks-template.md — ✅ no conflicts;
      phase structure accommodates book + bot tasks
  Follow-up TODOs: None
-->
# Humanoid Robotics Book + RAG Bot Constitution

## Core Principles

### I. Dual-System Alignment

This project consists of two tightly coupled systems that MUST
stay aligned at all times:

1. **The Book** — A technical, curriculum-driven book built with
   Docusaurus, authored using Spec-Kit Plus and Claude Code,
   deployed to GitHub Pages. Focused on Physical AI, Embodied
   Intelligence, and Humanoid Robotics.
2. **The Book RAG Bot** — A retrieval-augmented AI assistant
   grounded strictly in the book's content, designed to support
   learning, navigation, and applied understanding.

Any change to book structure, modules, or terminology MUST be
reflected in the RAG knowledge base and the bot's responses.

### II. Curriculum Integrity

The book's module structure is non-negotiable. All four modules
and the capstone MUST be preserved:

- **Module 1 — The Robotic Nervous System (ROS 2)**: Nodes,
  Topics, Services via `rclpy`; URDF humanoid modeling.
- **Module 2 — The Digital Twin (Gazebo & Unity)**: Physics
  simulation, sensor simulation (LiDAR, depth cameras, IMUs),
  human-robot interaction.
- **Module 3 — The AI-Robot Brain (NVIDIA Isaac)**: Isaac Sim,
  synthetic data, Isaac ROS perception, Nav2 navigation.
- **Module 4 — Vision-Language-Action (VLA)**: Whisper
  voice-to-action, LLM cognitive planning, natural language
  to ROS action graphs.
- **Capstone**: Autonomous humanoid robot integrating perception,
  planning, control, and action via voice command pipeline.

No module may be removed, reordered, or merged without a formal
constitution amendment.

### III. Code-First Technical Depth

- Every explanation MUST favor code-first presentation.
- Content MUST avoid marketing language, over-simplified
  explanations, and unstructured content blocks.
- The reader is treated as a serious builder, not a beginner.
- The book transitions AI from purely digital reasoning to
  physically grounded intelligence under real-world constraints.

### IV. Book-Bound RAG Intelligence

The RAG Bot:

- MUST be strictly grounded in the book's content.
- MUST NOT hallucinate beyond documented material.
- MUST answer using the book's concepts, terminology, and
  structure.
- MAY explain concepts, summarize modules, map questions to
  sections, and help students debug conceptual misunderstandings.
- MUST NOT invent APIs/tools/architectures absent from the book,
  drift into unrelated AI topics, override the curriculum, or act
  as a general-purpose chatbot.

### V. Clean Instrument UI

The Docusaurus UI MUST:

- Be clean, minimal, and technical.
- Favor clarity over decoration.
- Use clear side navigation and module-based hierarchy.
- Support fast scanning and deep technical reading.
- Function as a learning instrument, not a blog.

### VI. Precise Technical Tone

All content (book and bot) MUST be:

- Precise and technically accurate.
- Forward-looking with system-level thinking.
- Free of hype, vague motivation, and unnecessary superlatives.

### VII. Single Source of Truth

The book is the single source of truth. All downstream systems
(RAG bot, API responses, documentation) MUST derive their content
from the book. No secondary source may contradict or extend the
book's content without an explicit constitution amendment.

### VIII. Embodied North Star

This project exists to train students to build AI systems that do
not just think, but act in the real world. Every decision MUST be
evaluated against this north star: does it advance the student's
ability to design, simulate, and deploy humanoid robots that
perceive, reason, and act?

## Content Structure & Module Rules

### Quarter Framing

- Introduce Physical AI as the next evolution of AI systems.
- Emphasize interaction with physics, space, sensors, and human
  environments.
- Frame the quarter as a capstone-level experience.

### Module Deliverables

Each module MUST include:

- Conceptual introduction grounding the module in the overall
  Physical AI narrative.
- Hands-on code walkthroughs with working examples.
- Integration points showing how the module connects to adjacent
  modules.
- Assessment or checkpoint material tied to the capstone.

### Capstone Requirements

The capstone MUST integrate all four modules into a single
pipeline: voice command → plan → navigate → perceive → manipulate.

## Development Workflow

- All content authored via Spec-Kit Plus and Claude Code.
- Deployed to GitHub Pages via Docusaurus.
- Spec-driven development: features start as specs, proceed
  through plan and tasks before implementation.
- Smallest viable diff: do not refactor unrelated content.
- No hardcoded secrets or tokens; use `.env` and documentation.
- PHR (Prompt History Record) created for every substantive
  interaction.
- ADR suggestions surfaced for architecturally significant
  decisions; never auto-created.

## Governance

- This constitution supersedes all other project practices.
- Amendments require: (1) documented rationale, (2) version bump
  per semantic versioning, (3) propagation to all dependent
  templates and the RAG knowledge base.
- All PRs and reviews MUST verify compliance with these
  principles.
- Complexity beyond what the constitution permits MUST be
  justified in writing.
- See `CLAUDE.md` for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2026-02-01 | **Last Amended**: 2026-02-01
