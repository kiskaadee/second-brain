---
type: decision
status: accepted
project: brain
date: 2026-10-05
tags:
  - agent-architecture
  - skills
  - learning-workflow
  - human-in-the-loop
  - software-apprenticeship
---

# Agent Skills Pedagogical Decoupling and Governance

## Context and Problem Statement

As a career-changer learning software engineering by building real systems, standard industry agent workflows often prioritize automated code generation over engineer comprehension. This introduces an insidious risk: making it too easy to delegate away the exact engineering decisions, architectural trade-offs, and mental debugging models necessary for true skill acquisition.

Concurrently, repository skills had accumulated substantial operational coupling:
1. Skills were duplicated across multiple out-of-sync locations (`~/.gemini/config/skills`, `~/Brain/05-agents/skills`, and global `AGENTS.md` instructions).
2. Trivial slash command wrappers (`practice`, `diagnose`, `build-skill`) were maintained solely to expose command ergonomics, re-explaining parent axioms and introducing drift.
3. Skills contained verbose procedures (>150 lines), excessive narrative diagrams, and unverified platform assumptions.
4. Universal portable workflows were intermixed with personal, vault-specific tooling (such as Brain ledger loggers and inbox curators).

How do we structure an agent skills system that accelerates building while actively enforcing developer learning, explicit decision ownership, and cross-platform portability?

## Decision Drivers

* **Pedagogical Alignment (The Delegation vs. Learning Boundary)**: The workflow must not optimize solely for output volume. It must force the apprentice engineer to pause, understand failure modes, and reason about architectural trade-offs.
* **Single Authoritative Source**: Every rule and skill must exist in exactly one canonical location with zero manual synchronization drift.
* **Context Load Economics**: Skills must remain concise (target ≤ 50 lines, hard cap 80 lines) to minimize prompt overhead and prevent reasoning dilution.
* **Platform Independence**: Core software engineering skills must adhere to open standards (plain Markdown, standard frontmatter) without being tightly coupled to a single vendor or agent harness.
* **Clear Epistemic Separation**: General software engineering behaviors must remain strictly decoupled from project-specific knowledge graphs or personal vault structures.

## Considered Options

* **Option 1: Monolithic Vault-Coupled Skills (Status Quo)**: Retain skills inside the personal second-brain repository, maintaining mirror copies in the harness configuration directory and wrapper aliases for slash commands.
* **Option 2: Standalone Pure-Automation Skills**: Extract skills into a separate repository optimized strictly for autonomous task completion, allowing the agent to diagnose, edit, and commit code without interactive checkpoints.
* **Option 3: Standalone Portable Skills with Pedagogical Review Gates (Adopted)**: Decouple skills into a dedicated, public domain repository (`skills`). Merge slash-command wrappers into their parent skills, enforce a strict 80-line budget per skill, separate portable engineering skills from environment-specific extensions, and mandate explicit human checkpoints ("Your call") where the agent must offer 2-3 concrete options rather than deciding autonomously.

## Decision Outcome

Chosen option: **Option 3: Standalone Portable Skills with Pedagogical Review Gates**.

This model establishes a deliberate boundary between task delegation and deliberate practice. The AI provides structured investigative discipline and proposal synthesis, but the apprentice engineer retains ownership of every critical design, diagnostic, and commit boundary.

### Core Architectural Commitments

1. **The Delegation vs. Practice Boundary**:
   - In `/practice`, the learner writes all repository implementation code and drives analysis; the agent acts strictly as a Socratic tutor using graduated assistance and transfer challenges.
   - In `/diagnose`, the agent gathers empirical evidence and eliminates hypotheses, but pauses at a 6-part checkpoint before crossing any state-changing boundary.
   - In `/git-commit`, the working tree and diff remain authoritative truth; the agent proposes 2-3 commit slicing options with draft messages, but the human approves every state transition.
   - In `/document`, the engineer provides the core insight in their own words before drafting begins, preventing AI hallucination of design rationale.

2. **Single Authority & Wrapper Elimination**:
   - Every skill's directory `name` directly defines its invocation command. Redundant alias wrappers are eliminated.
   - The standalone repository `~/Projects/active/skills` is the sole source of truth. Runtime agent configurations install skills via `install.sh`.
   - The personal Brain vault removes duplicate skill definitions and maintains only an index pointer to the standalone repository.

3. **Shared Epistemic Skeleton & line Budget**:
   - All portable skills follow a universal 5-section skeleton: `Use when`, `Steps`, `Your call`, `Done when`, and `Hands off to`.
   - Hard budget: `SKILL.md` must remain ≤ 80 lines (achieved ≤ 54 lines across all core skills). Deep schemas and reference authoring templates are progressively disclosed under `references/`.

4. **Hierarchical Separation of Concerns**:
   - `skills/`: Universally portable engineering skills (`build-skill`, `diagnose`, `document`, `git-commit`, `practice`).
   - `brain/`: Context-specific extensions (`inbox-curation`, `commit-logger`).
   - `profile/`: Global developer persona and the universal "Your call" convention (`profile/AGENTS.md`).

## Pros and Cons of the Options

### Option 1: Monolithic Vault-Coupled Skills
* Good: Kept personal notes and agent configurations within a single workspace repository.
* Bad: Caused silent drift between runtime copies and vault specs.
* Bad: Made personal vault paths and private project names leak into portable workflows.
* Bad: Multiplied maintenance burden across redundant wrapper files.

### Option 2: Standalone Pure-Automation Skills
* Good: Minimizes human keystrokes during rapid prototyping.
* Bad: Actively harms the developer's learning path by obscuring underlying mechanisms.
* Bad: Encourages passive acceptance of AI-generated architecture without verification.
* Bad: Violates the apprentice mindset required to transition into professional engineering.

### Option 3: Standalone Portable Skills with Pedagogical Review Gates (Adopted)
* Good: Protects the learning curve by embedding Socratic friction directly into the development loop.
* Good: Achieves 70%+ reduction in skill prompt token overhead.
* Good: Idempotent `install.sh` enables deployment to multiple harnesses (Antigravity, Claude Code, Gemini CLI) from one source.
* Good: Public domain licensing (The Unlicense) allows the toolkit to serve as a clean public portfolio piece.
* Bad: Requires explicit human approval and input at each milestone, sacrificing fully autonomous unattended execution in favor of correctness and learning.

## Consequences

### Positive Consequences
* The engineer must actively articulate hypotheses, verify transfer questions, and select commit boundaries, building foundational engineering instincts.
* Skills are fully decoupled from local paths (`/home/<user>`), enabling seamless portability across Linux systems and tools.
* Symlink verification demonstrated that modern CLI harnesses cleanly resolve directory and file symlinks without copying.

### Negative Consequences & Accepted Trade-offs
* Workflows require active interactive engagement; long multi-step pipelines cannot run fully unattended without human presence.
* When authoring new skills, developers must pass through the `build-skill` design review gate and adhere strictly to the 80-line budget.

## More Information
* **Canonical Repository**: [`kiskaadee/skills`](https://github.com/kiskaadee/skills)
* **Shared Architecture Spec**: [`skills/build-skill/references/skeleton.md`](https://github.com/kiskaadee/skills/blob/main/skills/build-skill/references/skeleton.md)
* **Vault Index Pointer**: [`05-agents/skills/README.md`](../../05-agents/skills/README.md)
