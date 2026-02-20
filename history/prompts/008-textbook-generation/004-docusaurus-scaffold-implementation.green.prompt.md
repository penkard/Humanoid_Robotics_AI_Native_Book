---
id: 004
title: Docusaurus Scaffold Implementation
stage: green
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 008-textbook-generation
branch: 008-textbook-generation
user: penka
command: /sp.implement
labels: ["implementation", "docusaurus", "scaffold", "intro", "ros2"]
links:
  spec: specs/008-textbook-generation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - package.json
  - docusaurus.config.ts
  - sidebars.ts
  - tsconfig.json
  - .gitignore
  - src/css/custom.css
  - docs/intro.md
  - docs/01-robotic-nervous-system/_category_.json
  - docs/01-robotic-nervous-system/01-ros2-nodes-and-topics.md
  - docs/01-robotic-nervous-system/02-services-and-actions.md
  - docs/01-robotic-nervous-system/03-urdf-humanoid-modeling.md
tests:
  - npx docusaurus build — PASS (static files generated successfully)
---

## Prompt

/sp.implement
1. Initialize a new Docusaurus scaffold tailored for this book.
2. Configure `docusaurus.config.ts` with the title "Physical AI" and Vercel settings.
3. Create the folder structure for `docs/01-robotic-nervous-system`.
4. Write the introduction file `intro.md` explaining "Embodied Intelligence".

## Response snapshot

Executed all 4 implementation tasks:

1. **Docusaurus scaffold**: Created fresh Docusaurus 3.9.2 + TypeScript project in repo root via `npx create-docusaurus`. Moved scaffold files, cleaned up temp directory. Updated package.json name to `physical-ai-textbook`.

2. **docusaurus.config.ts**: Title "Physical AI", tagline "Build humanoid robots that perceive, reason, and act". Vercel deployment URL. Auto-generated sidebar via `bookSidebar`. Blog disabled. `routeBasePath: '/'` makes docs the homepage. Dark mode default. Prism syntax highlighting for Python, bash, YAML. Clean footer linking to introduction.

3. **docs/01-robotic-nervous-system/**: Created with `_category_.json` (position: 2, "The Robotic Nervous System (ROS 2)") and 3 chapters: ROS 2 Nodes & Topics, Services & Actions, URDF Humanoid Modeling. Each chapter includes working code examples.

4. **docs/intro.md**: Explains Embodied Intelligence — what Physical AI is, why the humanoid form factor matters, the 5-module learning path, and code-first methodology. Set as homepage via `slug: /`.

Build validation: `npx docusaurus build` passes with zero errors.

## Outcome

- Impact: Functional Docusaurus textbook with introduction and first module (ROS 2). Site builds and serves successfully.
- Tests: Build validation — PASS.
- Files: 11 files created/modified (see list above).
- Next prompts: Continue with remaining docs parts (Digital Twin, VLA, Capstone), backend setup, or deploy to Vercel.
- Reflection: Used `routeBasePath: '/'` to make docs the homepage, eliminating need for a separate index.tsx. Caught prism-xml module error and broken links during build validation — fixed both before declaring success.

## Evaluation notes (flywheel)

- Failure modes observed: (1) `prism-xml` not available — Docusaurus prism-react-renderer bundles XML as `markup`, not `xml`. Removed from additionalLanguages. (2) Broken links to `/intro` (page is at `/` due to slug) and `/personalize` (not yet created). Fixed footer and intro.md.
- Graders run and results (PASS/FAIL): `npx docusaurus build` — PASS.
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add remaining 4 Part directories (Digital Twin, VLA, Capstone, Humanoid Robotics) and verify sidebar renders all 6 parts.
