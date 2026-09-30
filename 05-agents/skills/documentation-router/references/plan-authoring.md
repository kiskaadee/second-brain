# Plan Authoring Specification

## Epistemic Role & Core Purpose

A **Plan** is the **authoritative implementation specification** and phased execution blueprint for delivering an accepted decision or known engineering goal. It answers:
> *"What exactly are we going to change, in what order, under which constraints, and how will we prove it worked?"*

A plan owns the concrete technical specifications, contracts, resource matrices, execution sequencing, operational runbooks, verification gates, and Definition of Done. It is an engineering execution document, not an architectural debate.

---

## 1. Epistemic Invariants & Boundaries

1. **No Disguised ADRs**:
   A plan must never silently introduce new architectural commitments. It operationalizes accepted ADRs.
   * If implementation reveals that an architectural assumption is broken or that a new commitment is required, **stop execution** and route the decision to an ADR before resuming the plan.
2. **Pure Constraints, No Re-argument**:
   State technical requirements as binding implementation constraints rather than re-litigating why alternatives were rejected.
   * **Prohibited**: `"Early designs considered full Git clones, but after long evaluation we realized..."`
   * **Correct**: `"Remote provenance inspection MUST evaluate commit equality using git ls-remote bounded by a 10-second timeout."`
3. **Actionable & Non-Destructive Runbooks**:
   Provide exact execution commands, verified pre-flight snapshots, state parity proofs, and rollback instructions for all state-bearing operations.
4. **Phased Execution & Verification Gates**:
   Group work into ordered milestones (e.g. P0 through P5). Each phase must specify concrete deliverables and verifiable exit criteria before the next phase begins.
5. **Bidirectional Cross-References**:
   Explicitly link to the governing ADR and companion Discussion in the document header.
6. **Preservation of Lineage**:
   When a new plan supersedes an earlier iteration (e.g. v4 supersedes v3), retain the older plans in a dedicated subsystem or lineage directory marked `superseded`. Never rewrite historical plans into synthetic current states.

---

## 2. Standard Document Structure

```markdown
---
type: plan
status: draft | active | completed | abandoned
project: <project-name>
tags: [list, of, tags]
---

# <Project Title> Roadmap & Execution Plan

> **Architectural Decision Record**: [Link to governing ADR](../path/to/adr.md)
>
> **Architectural Discussion & Rationale**: [Link to companion Discussion](../path/to/discussion.md)
>
> **Target System**: <Target host, appliance, or environment>

---

## Executive Summary
Concise statement of what this plan implements and its primary operational outcomes.

---

## 1. Technical Specifications & Contracts
* System architecture topology (Mermaid diagram).
* Component taxonomy, resource ownership, and controller authority matrices.
* Formal schema contracts (manifest specifications, domain models, security invariants).
* Explicit constraint rules (transport protocols, timeout bounds, state filesystem paths).

---

## 2. Working Rules & Coordination Constraints
* Production safety invariants (e.g. one production transition at a time, zero data loss).
* Multi-track branch coordination rules (stable integration seams).
* Minimal control path constraints (reconciliation simplicity).

---

## 3. Phased Implementation Roadmap
Overview table listing phases, target scopes, and verification gates:

| Phase | Status | Deliverables | Verification Gates |
| :--- | :--- | :--- | :--- |
| **P0: Baseline** | Active | ... | ... |
| **P1: Migration** | Pending | ... | ... |

### Phase 0: <Phase Name>
* **Deliverable 0.1**: Concrete action and files modified.
* **Deliverable 0.2**: Concrete action and files modified.

### Phase 1: <Phase Name>
* **Architectural Invariants**: Non-negotiable requirements for this phase.
* **Execution Runbook**: Exact bash commands, backup steps, state freeze, and cutover.
* **Rollback Procedure**: Reversion steps if verification gates fail.

---

## 4. Definition of Done
Explicit checklist required before the plan can transition to `status: completed`:
- [ ] Structural boundaries verified.
- [ ] Zero data loss verified with state parity proofs.
- [ ] Automated tests, linters, and type checkers passing.
- [ ] Runtime health and recovery validated in production.
```
