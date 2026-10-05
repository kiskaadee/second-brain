---
type: guide
project: brain
tags:
  - brain
  - skills
  - investigation
  - documentation-router
  - walkthrough
---

# Walkthrough: Global Documentation Router & Investigation Skills

Operational walkthrough for the implementation of the decoupled, reusable global skill system separating **procedural engineering investigation** from **second-order architectural documentation treatment**.

---

## 1. System Architecture

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

---

## 2. Implemented Artifacts & Locations

### A. Procedural Investigation Skill
- **Runtime Location**: `~/.gemini/config/skills/diagnose/SKILL.md`
- **Repository Specification**: [`skills/diagnose`](https://github.com/kiskaadee/skills/blob/main/skills/diagnose/SKILL.md)
- **Role**: Purely empirical troubleshooting following the scientific method (Observation $\to$ Verification) and the 6-part interactive checkpoint protocol.
- **Boundary**: Stops cleanly upon verified recovery; hands off to `document` if non-obvious learning or architectural questions emerged.

### B. Documentation Skill
- **Runtime Location**: `~/.gemini/config/skills/document/SKILL.md`
- **Repository Specification**: [`skills/document`](https://github.com/kiskaadee/skills/blob/main/skills/document/SKILL.md)
- **Role**: Second-order knowledge filter and gatekeeper (anti-markdown factory).
- **Core Rules**:
  - **Gatekeeping**: Routine/trivial tasks produce **NO ARTIFACT**.
  - **Classification**: Maps knowledge to Discussion (WHY), ADR (WHAT decided), Plan (HOW to build), or Debug Record (Empirical RCA).
  - **Multi-Artifact Coordination**: Decomposes multi-faceted sessions into discrete artifacts.
  - **Optional Relationships vs. Pipelines**: Discussions may inform ADRs; ADRs may constrain Plans. These describe optional information flow and authority boundaries, not a mandatory documentation pipeline. Each artifact may exist independently whenever justified.
  - **Anti-Overlap**: The same fact may appear in multiple documents only when it serves a different epistemic purpose.

### C. Modular Authoring Reference Specifications
Packaged under `~/.gemini/config/skills/documentation-router/references/`:
1. **`discussion-authoring.md`**: Exploratory narrative, preserves uncertainty and rejected alternatives, zero "decision voice".
2. **`adr-authoring.md`**: Strict **MADR 4.0** standard, compact architectural commitments, content-addressed OCI digest immutability vs. mutable tags, delegating field-level schema representation to the Plan.
3. **`plan-authoring.md`**: Authoritative implementation specification, ordered execution (P0–P5), pure constraints without re-arguing rationale, verification gates, runbooks, and DoD.
4. **`debug-record-authoring.md`**: Historical investigation / RCA record covering bugs, regressions, system anomalies, failed migrations, configuration errors, and unexpected behaviors.

### D. Global Rules Decoupling
- **Location**: `~/.gemini/config/AGENTS.md`
- Separated `Global Rule: Engineering Investigation` from `Global Rule: Architectural & Project Documentation`.

---

## 3. Verification

- Skills discovered in `~/.gemini/config/skills/`:
  - `engineering-investigation`
  - `documentation-router` (with 4 authoring reference documents)
- `python scripts/validate-brain.py && python scripts/test_validator.py`: **`✅ All checks passed.`**
