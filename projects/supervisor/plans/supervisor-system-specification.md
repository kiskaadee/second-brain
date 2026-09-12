---
type: plan
status: active
project: supervisor
tags:
  - supervisor
  - architecture
  - specification
  - workflow
  - productivity
---

# Specification: Personal Engineering Progress & Implementation Supervisor

## 1. Problem Statement

When an engineer tackles large, multi-phase technical roadmaps independently, a fundamental operational tension emerges between **high-level planning** and **ground-level execution**:

1. **Passive Generation vs. Active Understanding**: Automated agentic code generation often robs the engineer of internalizing the system's nuance, debugging intuition, and architectural muscle memory. The engineer wants to be the **sole driver of the code**, but still desires continuous, objective verification.
2. **Context & Invariant Drift**: As complex projects evolve over days or weeks, subtle architectural constraints (trust boundaries, contract invariants, security threat models, and explicit failure semantics) easily slip from mind.
3. **Granularity Disconnect**: Detailed architectural plans (e.g., multi-page markdown roadmaps) provide macro clarity but fail as tactical, zero-friction execution tools in the terminal during active coding sessions.
4. **Project Fragmentation**: Personal engineering spans multiple disparate repositories and stacks (infrastructure, backend services, client tools). There is no standardized, portable mechanism to set an active work session, project canonical plan deliverables into local task trackers, and evaluate repository progress across different projects without starting from scratch each time.

---

## 2. Global Long-Term Objective

Establish a **project-agnostic Engineering Progress Tracking & Supervisory System** that bridges high-level architectural specifications with active local workspace changes. 

The system acts strictly as a **navigator, observer, and progress verifier**:
- It empowers the engineer to drive the implementation manually.
- It continuously monitors changes against declared contracts and test invariants.
- It tracks and surfaces deliverable progression across any codebase with zero manual administrative overhead.

---

## 3. High-Level Goals

1. **Preserve Developer Agency**: The system must never write or mutate implementation code autonomously. It observes, evaluates, and advises.
2. **Universal Project Portability**: The same supervisory model and tracking workflows must apply identically whether the engineer is working on an infrastructure appliance (`homelab`), a media worker (`magnetflix`), a backend service (`bitetrack`), or a personal website.
3. **Single Source of Truth with Local Projection**: Long-form plans in the knowledge graph remain canonical, while ground-level task trackers (e.g., standard one-liner `todo.txt` files) in active repository checkouts serve as tactical projections.
4. **Continuous Contract & Quality Feedback**: Provide actionable feedback on local changes against the active plan's threat boundaries, design rules, and test invariants before changes are committed.
5. **Legible State Progression**: Eliminate ambiguity around *what is done*, *what is in progress*, and *what is next* across all active engineering initiatives.

---

## 4. Requirements

### 4.1 Functional Requirements (FR)

#### FR-1: Session & Focus Definition
* **FR-1.1**: The system must allow defining an active **Work Session** comprising:
  * **Target Project**: Logical identifier of the project.
  * **Workspace Path**: Local filesystem path of the repository checkout.
  * **Canonical Plan**: Path/URI to the authoritative roadmap or implementation specification.
  * **Active Deliverable**: The specific milestone or task currently being addressed.
  * **Constraints & Deadlines**: Any target completion dates, performance budgets, or scope exclusions.
  * **Evaluation Cadence**: Trigger policies for feedback (e.g., file-save events, git commit hooks, or periodic polling intervals).
* **FR-1.2**: Switching active sessions must be atomic and require no project-specific re-configuration.

#### FR-2: Bidirectional Plan & Task Projection
* **FR-2.1**: The system must parse canonical plan documents and project their deliverables into compact, standardized, human-readable task lists at the root of the active workspace.
* **FR-2.2**: Projected tasks must support prioritization, project scoping, and contextual tags (e.g., standard `todo.txt` syntax).
* **FR-2.3**: Synchronization must be bidirectional: marking a task complete locally or verifying a deliverable must reflect in the canonical plan, and changes in the canonical plan must update the local task representation.

#### FR-3: Workspace Observation & Diff Analysis
* **FR-3.1**: The system must observe uncommitted workspace modifications (working tree diffs, staged changes, newly created files) without requiring a git commit or push.
* **FR-3.2**: The system must correlate observed changes directly to the active deliverable declared in the current session.

#### FR-4: Contract & Invariant Verification
* **FR-4.1**: The system must evaluate workspace changes against declared project invariants (e.g., prohibited patterns, architectural boundary violations, security threat model regressions).
* **FR-4.2**: The system must support running and capturing the results of project-specific verification commands (e.g., unit test suites, structural linters, type checks, schema validators).
* **FR-4.3**: The system must categorize evaluation results into explicit, deterministic states:
  * **Compliant / Verified**: Deliverable criteria met, invariants intact, tests passing.
  * **In-Progress / Partial**: Change in progress, no violations detected.
  * **Violation / Regression**: Architectural boundary breached, invariant broken, or security constraint violated.

#### FR-5: Multi-Modal Feedback & Querying
* **FR-5.1**: The system must expose evaluation feedback via ambient inspection (e.g., local dashboard feed, status summaries).
* **FR-5.2**: The system must support on-demand interrogation, allowing the engineer to ask questions about the current diff, edge cases, or next steps in the plan.
* **FR-5.3**: Feedback must focus strictly on rationale, boundary compliance, edge cases, and verification proofs—never on unsolicited boilerplate generation.

#### FR-6: Historical Progress Auditing
* **FR-6.1**: The system must maintain an append-only log of session milestones and completed deliverables with timestamps, commit SHAs, and verification status.

---

### 4.2 Non-Functional Requirements (NFR)

#### NFR-1: Non-Intrusive Workflow
* **NFR-1.1**: The system must operate strictly out of band. Failure, lag, or downtime of the supervisory system must never block git operations, editor responsiveness, or the ability to build and run the codebase.
* **NFR-1.2**: The system must make zero modifications to existing source files without explicit confirmation.

#### NFR-2: Zero External Dependency on Source Trees
* **NFR-2.1**: The system must not mandate vendor-specific configuration files, custom frameworks, or proprietary libraries inside the target project’s source code.
* **NFR-2.2**: The local task artifact (`todo.txt`) must adhere to open, plain-text standards readable by standard CLI and text utilities.

#### NFR-3: Privacy & Data Sovereignty
* **NFR-3.1**: All workspace analysis, diff evaluation, and session metadata must reside locally on the engineer's workstation.
* **NFR-3.2**: Sensitive credentials, environment files, and `.gitignore`-excluded files must be excluded from inspection by default.

#### NFR-4: Performance & Resource Footprint
* **NFR-4.1**: Observation cycles must execute with minimal CPU and memory overhead, deferring heavy verification passes to deliberate trigger points.
* **NFR-4.2**: Workspace diff capture must complete in sub-second time on standard repositories.

---

## 5. System Boundary & Explicit Non-Goals

To maintain conceptual purity, the following are **explicitly out of scope**:

* **Not an Automated Code Generator**: The tool will not write feature implementations, refactor files automatically, or replace developer coding.
* **Not a Project Management SaaS**: The system is not a cloud ticketing tool (Jira, Linear, GitHub Issues) or a multi-user collaborative dashboard. It is a personal developer feedback loop.
* **Not a CI/CD Orchestrator**: The system does not replace remote CI runners (Gitea Actions, GitHub Actions); it provides pre-commit, real-time local feedback.
* **Not a Language-Specific Linter**: The system does not reimplement AST analysis for specific languages; it orchestrates existing project-native verification tools.

---

## 6. Success Criteria

A successful realization of this specification means:

1. **Seamless Context Switching**: Starting a work session on any project requires only selecting the project and plan; the workspace immediately populates with current actionable tasks.
2. **Zero Invariant Regressions**: Architectural and security invariants defined during planning are caught locally *before* code is staged or committed.
3. **High Developer Momentum**: The engineer stays focused on writing code with immediate clarity on the next micro-task and continuous confidence that the implementation matches the design.
