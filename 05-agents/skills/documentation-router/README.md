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

# Documentation Router

> **Documentation Router helps you decide whether an engineering session produced something worth preserving and, if it did, which kind of Brain artifact should preserve it.**

---

## 1. Identity
**Documentation Router** is a second-order knowledge classifier for the Brain knowledge graph. It evaluates the outcomes of an engineering or learning activity to determine if durable knowledge was generated and routes that knowledge to its canonical epistemic container.

## 2. User Value
Engineering sessions often produce different kinds of knowledge: an exploratory trade-off, a point-in-time architectural commitment, a concrete implementation roadmap, an incident root-cause analysis, or a reusable mental model.

Treating all session output as generic notes leads to knowledge bloat, fragmented documentation, and conflicting authorities. Documentation Router ensures:
- Routine work leaves **no documentation footprint**.
- Every preserved fact has **one authoritative owner**.
- Exploration, commitments, implementation plans, and investigations never pollute each other.

## 3. Invocation
### When to use it:
Invoke Documentation Router at the close of an engineering session, investigation, or design discussion when you need to answer: *"Did we produce anything durable that would be lost if not recorded?"*

### When NOT to use it:
- **Routine implementation & chores**: Bug fixes, minor refactors, or standard task execution where commit messages and PR diffs are fully self-explanatory.
- **Authoring execution**: Documentation Router routes and bounds documents; it does not replace the actual drafting of code or narrative text.

## 4. Behavior
When invoked, Documentation Router evaluates session context through a progressive evaluation:

```text
Engineering Session Complete
       ↓
1. Gatekeeper: Did something worth preserving happen?
       ├── No  → Stop (No artifact created)
       └── Yes → 2. Epistemic Classification
                      ↓
                 What kind of knowledge was produced?
                      ├── Exploration / Trade-offs → Discussion
                      ├── Architectural Decision   → ADR
                      ├── Implementation Roadmap   → Plan
                      ├── Empirical RCA            → Debug Record
                      └── Reusable Mental Model    → Knowledge Article
                      ↓
                 3. Multi-Artifact Decomposition
                      └── Split multi-dimensional knowledge to prevent overlap
```

## 5. Outputs
Documentation Router produces one or more of the following routing recommendations:

| Output Artifact | Epistemic Role | What It Captures |
| :--- | :--- | :--- |
| **No Artifact** | *Ephemeral* | Session produced routine or self-explanatory work. |
| **Discussion** (`02-discussions/`) | *WHY* | Explorations, alternatives, trade-offs, and open questions. |
| **ADR** (`03-records/decisions/`) | *WHAT was decided* | Point-in-time architectural commitments and accepted trade-offs. |
| **Plan** (`01-plans/`) | *HOW to build it* | Concrete specifications, phases (P0–P5), and Definition of Done. |
| **Debug Record** (`03-records/debug/`) | *Empirical RCA* | Diagnostic hypotheses, reproduction logs, and root causes. |
| **Knowledge Article** (`04-learning/knowledge/`) | *UNDERSTANDING* | Generalized mental models, concepts, and transferable methodologies. |

## 6. Boundaries
- **Does not force a documentation pipeline**: A Discussion does not require an ADR; an ADR does not require a Plan. Each artifact stands on its own authority.
- **Does not duplicate facts across boundaries**: It enforces that the same fact cannot be owned by multiple documents unless serving fundamentally different epistemic purposes.
- **Does not author without reference contracts**: It selects the artifact type and immediately hands off to that document's specific authoring contract.

---

## 7. Package Structure
- [`SKILL.md`](SKILL.md) — Operational instructions, decision gates, and behavioral invariants executed by the AI agent runtime.
- **Reference Authoring Specifications**:
  - [`discussion-authoring.md`](references/discussion-authoring.md) — Exploration format, narrative voice, and lifecycle.
  - [`adr-authoring.md`](references/adr-authoring.md) — MADR 4.0 format, decision drivers, and trade-offs.
  - [`plan-authoring.md`](references/plan-authoring.md) — Phased execution roadmaps, invariants, and DoD.
  - [`debug-record-authoring.md`](references/debug-record-authoring.md) — Empirical RCA logging and post-mortem structure.
  - [`knowledge-authoring.md`](references/knowledge-authoring.md) — Durable engineering concepts and methodologies.
