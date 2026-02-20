---
id: 001
title: Initial Constitution Creation
stage: constitution
date: 2026-02-01
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 006-phase-2-implementation
user: penka
command: /sp.constitution
labels: ["constitution", "project-setup", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

# Project Constitution
## AI/Spec-Driven Book Creation + Book RAG Bot

---

## 1. Project Scope

This project consists of two tightly coupled systems:

1. **The Book**
   - A technical, curriculum-driven book built with **Docusaurus**
   - Authored using **Spec-Kit Plus** and **Claude Code**
   - Deployed to **GitHub Pages**
   - Focused on **Physical AI, Embodied Intelligence, and Humanoid Robotics**

2. **The Book RAG Bot**
   - A retrieval-augmented AI assistant
   - Grounded strictly in the book's content
   - Designed to support learning, navigation, and applied understanding

Both systems must stay aligned at all times.

---

## 2. Book Purpose & Theme

**Theme:**
AI Systems in the Physical World
Embodied Intelligence
Bridging the Digital Brain and the Physical Body

**Goal:**
Enable students to design, simulate, and deploy humanoid robots that perceive, reason, and act in real or simulated environments.

The book transitions AI from:
- Purely digital reasoning
to
- Physically grounded intelligence operating under real-world constraints

---

## 3. Book Structure & Content Rules

### Quarter Overview
- Introduce **Physical AI** as the next evolution of AI systems
- Emphasize interaction with physics, space, sensors, and human environments
- Frame the quarter as a **capstone-level experience**

### Modules (Must Be Preserved)

#### Module 1: The Robotic Nervous System (ROS 2)
- ROS 2 architecture: Nodes, Topics, Services
- Python agents integrated with ROS via `rclpy`
- Humanoid modeling using URDF

#### Module 2: The Digital Twin (Gazebo & Unity)
- Physics-accurate simulation
- Gravity, collisions, environments
- Sensor simulation: LiDAR, depth cameras, IMUs
- Human-robot interaction contexts

#### Module 3: The AI-Robot Brain (NVIDIA Isaac)
- Isaac Sim for photorealistic simulation
- Synthetic data generation
- Isaac ROS for accelerated perception
- Nav2 for humanoid navigation and planning

#### Module 4: Vision-Language-Action (VLA)
- Voice-to-Action using Whisper
- LLM-based cognitive planning
- Translating natural language goals into ROS action graphs

### Capstone
- Autonomous humanoid robot
- Voice command -> plan -> navigate -> perceive -> manipulate
- Must integrate **perception, planning, control, and action**

---

## 4. Book UI Constitution (Docusaurus)

The book UI must:
- Be **clean, minimal, and technical**
- Favor **clarity over decoration**
- Use: Clear side navigation, Module-based hierarchy, Code-first explanations
- Support: Fast scanning, Deep technical reading
- Avoid: Marketing language, Over-simplified explanations, Unstructured content blocks

The UI is a **learning instrument**, not a blog.

---

## 5. Book RAG Bot Constitution

### Core Behavior
- Is **strictly grounded** in the book's content
- Must not hallucinate beyond documented material
- Answers using: Concepts, Terminology, Structure used in the book

### Allowed Capabilities
- Explain concepts from the book
- Greet the user
- Summarize chapters or modules
- Map user questions to relevant sections, modules, capstone requirements
- Help students understand architectures, debug conceptual misunderstandings, connect theory to robotics workflows

### Disallowed Behavior
- Must not invent APIs, tools, or architectures not in the book
- Must not drift into unrelated AI topics
- Must not override the curriculum's structure
- Must not act as a general-purpose chatbot

---

## 6. Tone & Pedagogy Rules
- Precise, Technical, Forward-looking, System-level thinking
- No hype, No vague motivation talk
- The book and bot treat the reader as a **serious builder**, not a beginner.

---

## 7. Alignment Rule
Any change to book structure, modules, or terminology must be reflected in the RAG knowledge base and the bot's responses.
**Single source of truth = the book.**

---

## 8. North Star
This project exists to train students to build:
> AI systems that do not just think, but **act in the real world**.
Embodied. Grounded. Autonomous.

## Response snapshot

Created constitution v1.0.0 at `.specify/memory/constitution.md` with 8 core principles derived from user input: Dual-System Alignment, Curriculum Integrity, Code-First Technical Depth, Book-Bound RAG Intelligence, Clean Instrument UI, Precise Technical Tone, Single Source of Truth, and Embodied North Star. Added Content Structure & Module Rules section, Development Workflow section, and Governance section. All templates validated as compatible. No follow-up TODOs.

## Outcome

- Impact: Initial constitution established for the Humanoid Robotics Book + RAG Bot project
- Tests: N/A (governance document)
- Files: .specify/memory/constitution.md (created)
- Next prompts: /sp.specify for first feature spec, /sp.plan for implementation planning
- Reflection: User provided comprehensive 8-section constitution input; mapped to 8 principles with additional structural and governance sections

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS - no unresolved placeholders, version coherent, dates ISO format
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
