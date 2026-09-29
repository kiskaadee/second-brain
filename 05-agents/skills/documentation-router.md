---
type: agent
status: active
name: documentation-router
kind: skill
project: brain
tags:
  - documentation
  - router
  - epistemic-taxonomy
  - knowledge-governance
---

# Documentation Router Skill

Canonical store of the global agent skill for session context evaluation, epistemic classification, anti-overlap enforcement, and modular documentation authoring.

* **Runtime Customization Path**: `~/.gemini/config/skills/documentation-router/SKILL.md`
* **Applicable Workspaces**: Global (workstation-wide across all repositories and directories).

---

## 1. The Cardinal Invariant

> **Documentation type is determined by the nature of the knowledge being preserved, not by the activity that produced it.**

* A debugging session discovering an underlying architectural misconception produces a **Discussion** or an **ADR**, not merely a Debug Record.
* An architectural debate that reaches a firm point-in-time consensus produces an **ADR**; if it remains exploratory, it remains a **Discussion**.
* An implementation task that uncovers an unaddressed architectural question must pause and route to an **ADR** before proceeding with the **Plan**.
* A routine bug fix or maintenance chore produces **NO ARTIFACT**.

---

## 2. Epistemic Classification & Routing

| Knowledge Produced | Epistemic Role | Target Container | Governing Module |
| :--- | :--- | :--- | :--- |
| Explorations, inquiries, trade-offs, pain points, alternatives evaluated, and historical evolution. | **WHY** | `02-discussions/` (`type: discussion`) | `references/discussion-authoring.md` |
| Point-in-time architectural commitments, decision drivers, forces, and accepted trade-offs. | **WHAT was decided** | `03-records/decisions/` (`type: decision`) | `references/adr-authoring.md` |
| Authoritative implementation specifications, constraints, phased execution (P0–P5), runbooks, and DoD. | **HOW to build it** | `01-plans/` (`type: plan`) | `references/plan-authoring.md` |
| Historical investigation of unexpected system behaviors, regressions, bugs, or anomalies. | **Empirical RCA** | `03-records/debug/` (`type: debug`) | `references/debug-record-authoring.md` |

---

## 3. Relationships & Authority Boundaries

```text
Discussion ──informs──> ADR ──constrains──> Plan
     ^                      ^                 |
     └──────────────────────┴─────────────────┘
                cross-references
```

> **Rule on Relationships vs. Pipelines**:
> Discussions may inform ADRs; ADRs may constrain Plans. These relationships describe **optional information flow and authority boundaries, not a mandatory documentation lifecycle**.
>
> * A Discussion may exist and remain open or resolved without generating an ADR or Plan.
> * An ADR may be authored directly for a clear architectural commitment without requiring a preceding Discussion artifact.
> * A Plan may be authored for a known engineering project without requiring a preceding Discussion or ADR.
> * A Debug Record stands alone as historical memory of an investigation.

---

## 4. Anti-Overlap Invariants & Fact Ownership

1. **Rule of Epistemic Purpose**: The same fact may appear in multiple documents **only when it serves a different epistemic purpose**.
2. **Canonical Ownership of Facts**:
   - The **Discussion** owns the exploratory narrative, rejected alternatives, and justification.
   - The **ADR** owns the decision outcome, forces, and accepted trade-offs.
   - The **Plan** owns the technical specification, constraints, and phased execution runbooks.
   - The **Debug Record** owns the empirical observation, diagnostic tests, and root-cause mechanism.
