---
type: plan
status: completed
project: brain
tags:
  - brain
  - skills
  - investigation
  - documentation-router
  - agents
---

# Implementation Plan: Documentation Router & Engineering Investigation Skills Decoupling

## Executive Summary

Based on the architectural reasoning, refactoring lessons, and operational feedback, this plan decouples engineering investigation from documentation generation into two cooperating, independent pipelines:

1. **`engineering-investigation`**: A purely procedural skill focused on empirical troubleshooting, scientific method progression, and interactive checkpoints. Stops cleanly at verification/recovery without forcing documentation capture.
2. **`documentation-router`**: A second-order global documentation evaluation and routing system that inspects session context, determines whether durable knowledge capture is justified, classifies knowledge type (not activity type), enforces anti-overlap invariants, and coordinates modular authoring specifications:
   - `references/discussion-authoring.md`
   - `references/adr-authoring.md`
   - `references/plan-authoring.md`
   - `references/debug-record-authoring.md`
3. **Global Rules Update in `~/.gemini/config/AGENTS.md`**: Separating the investigation rule from the documentation governance rule while maintaining the global inbox capture contract.

---

## 1. System Topology & Architectural Boundary

```text
                           Engineering Session
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          Investigation Skill           Documentation Router
          "How do I reason?"            "What should be preserved?"
          (Procedural / Empirical)       (Second-Order Knowledge Filter)
                    │                           │
                    ▼                           ▼
          Verified System State         Is an artifact justified?
                                                │
                                    ┌───────────┼───────────┬───────────┐
                                    ▼           ▼           ▼           ▼
                                Discussion     ADR        Plan     Debug Record
                                  (WHY)       (WHAT)      (HOW)      (RCA)
```

### The Cardinal Invariant
> **Documentation type is determined by the nature of the knowledge being preserved, not by the activity that produced it.**
> 
> - A debugging session discovering an architectural flaw produces a **Discussion** or an **ADR**, not necessarily a Debug Record.
> - A design session that converges on an architectural commitment produces an **ADR**; if it remains exploratory, it stays a **Discussion**.
> - An implementation request requiring a new architectural commitment must pause and route to an **ADR** before resuming the **Plan**.
> - Routine maintenance or trivial bug fixes produce **NO ARTIFACT**.

---

## 2. Refactored Skill: `engineering-investigation`

**Runtime Location**: `~/.gemini/config/skills/engineering-investigation/SKILL.md`  
*(Replaces `~/.gemini/config/skills/engineering-investigation-and-knowledge/`)*

### Key Changes
- **Removed**: "Evaluate Durable Learning" decision branch, "Conditional Knowledge Capture Decision" section, "Staging & Epistemic Reporting Protocol" (report markdown template, Brain staging paths, vault curation).
- **Retained**:
  - The 8-stage scientific method lifecycle (Observe $\to$ Hypotheses $\to$ Rationalized Inspection $\to$ Narrow Failure Domain $\to$ Root Cause Determination $\to$ Declarative Remediation $\to$ Local Validation $\to$ Runtime Verification).
  - Core epistemic principles: preserve reasoning, separate observation from inference, explain diagnostic command rationale, eliminate hindsight bias, proportional depth, zero secret leakage.
  - The 6-part interactive checkpoint protocol (Current State, Reasoning, Changes, Validation, Next Action, Recovery) with pauses before user-controlled state boundaries.
- **Handoff Boundary**: Explicitly stops upon successful runtime verification. Emits findings to session context; if non-obvious learning or architectural questions emerged, hands off to `documentation-router`.

---

## 3. New Skill: `documentation-router`

**Runtime Location**: `~/.gemini/config/skills/documentation-router/SKILL.md`

### Responsibilities
1. **Gatekeeping (Anti-Markdown Factory)**: Answers *"Did something worth preserving happen?"* Routine maintenance, trivial syntax, standard operations $\to$ **NO ARTIFACT**.
2. **Epistemic Classification**: Matches knowledge produced to the appropriate epistemic container:
   - Exploration, trade-offs, uncertainty, alternatives $\to$ **Discussion**
   - Formal architectural/design commitment constraining future work $\to$ **ADR**
   - Ordered implementation steps, contracts, runbooks, verification $\to$ **Plan**
   - Empirical root-cause post-mortem of broken system $\to$ **Debug Record**
3. **Multi-Artifact Decomposition**: Detects when a session produces distinct knowledge products and decomposes them into distinct artifacts rather than blending them.
4. **Anti-Overlap Invariants & Canonical Fact Ownership**:
   - **Optional Flow and Authority**: Discussions may inform ADRs; ADRs may constrain Plans. These describe information flow and authority boundaries, not a mandatory documentation pipeline. A Discussion, ADR, Plan, or Debug Record may exist independently when justified.
   - **Rule of Epistemic Purpose**: The same fact may appear in multiple documents *only* when it serves a different epistemic purpose.
   - **Decision Authority**: ADRs are authoritative for decisions; Plans are authoritative for implementation specifications; Discussions preserve historical exploration and have no decision authority.
   - **Preservation of History**: Superseded documents are kept in lineage folders marked `superseded`, never rewritten into synthetic history.

---

## 4. Cooperating Authoring Modules

Stored under `~/.gemini/config/skills/documentation-router/references/`:

### A. `discussion-authoring.md`
- **Core Question**: *"What are we trying to understand, and what did we learn while exploring it?"*
- **Epistemic Voice**: Narrative, exploratory, retrospective.
- **Strict Invariants**:
  - **Zero "Decision Voice"**: Never uses phrases like `"The Decision: ..."` or imperative directives. Uses `"The exploration ultimately converged on..."` or `"Resulting Direction: ..."`.
  - **Preserves Uncertainty & Failed Ideas**: Retains rejected alternatives and why they were explored.
  - **Tempered Tone**: Avoids absolutes.
  - **Convergence**: Closes by linking forward to resulting ADRs/Plans without duplicating their resolution contracts.

### B. `adr-authoring.md`
- **Core Question**: *"What did we decide, and why?"*
- **Structural Basis**: **MADR 4.0 Standard**:
  `Context and Problem Statement` $\to$ `Decision Drivers` $\to$ `Considered Options` $\to$ `Decision Outcome` $\to$ `Pros and Cons` $\to$ `Consequences` $\to$ `More Information`.
- **Strict Invariants**:
  - **Architectural Commitments Only**: Prohibits implementation procedures, bash runbooks, execution timeouts, and internal schema field names.
  - **Independent Identity Requirement**: Mandates that deployment configuration, source provenance, and artifact identity must be independently observable, delegating exact schema representations to the Plan.
  - **Artifact Digest Immutability**: Distinguishes mutable container image tags from content-addressed immutable OCI digests.
  - **Neutral Systems Language**: Justifies outcomes through trade-offs rather than subjective/evaluative claims.

### C. `plan-authoring.md`
- **Core Question**: *"What exactly are we going to change, in what order, under which constraints, and how will we prove it worked?"*
- **Epistemic Role**: **Authoritative Implementation Specification**.
- **Strict Invariants**:
  - **No Disguised ADRs**: Must not silently introduce new architectural commitments. If implementation uncovers an architectural dilemma, it must pause and route to an ADR.
  - **Pure Constraints, No Re-argument**: Technical decisions are stated as strict implementation invariants, without repeating historical debate.
  - **Actionable Execution**: Contains system topology, controller authority, resource ownership, schema contracts, security invariants, ordered phases (P0–P5), non-destructive runbooks, rollback procedures, and Definition of Done.

### D. `debug-record-authoring.md`
- **Core Question**: *"What empirically broke, how did the investigation diagnose it, and what was the root cause?"*
- **Epistemic Role**: Historical incident post-mortem / RCA record.
- **Structure**: System Context $\to$ Problem & Observations $\to$ Diagnostic Inquiries $\to$ Hypothesis Testing $\to$ Root Cause $\to$ Remediation & Validation $\to$ Deployment & Recovery Runbook $\to$ Transferable Learnings.

---

## 5. Global Rules & Canonical Catalog Updates

1. **Global Configuration (`~/.gemini/config/AGENTS.md`)**:
   - Separated into three distinct global rules:
     - `Global Rule: Brain Inbox Capture` (Physical artifact capture mechanism)
     - `Global Rule: Engineering Investigation` (Procedural scientific method & checkpoints)
     - `Global Rule: Architectural & Project Documentation` (Epistemic router governance)
2. **Canonical Brain Agent Store (`05-agents/`)**:
   - Documented `05-agents/skills/engineering-investigation.md`.
   - Documented `05-agents/skills/documentation-router.md`.
   - Updated catalog index in `05-agents/README.md`.

---

## 6. Verification

1. Verified skills in `~/.gemini/config/skills/`:
   - `engineering-investigation/SKILL.md`
   - `documentation-router/SKILL.md`
   - `documentation-router/references/` (4 authoring specifications)
2. Verified global AGENTS.md rules formatting and syntax.
3. Verified Brain vault integrity: `python scripts/validate-brain.py` and `python scripts/test_validator.py`.
