---
type: guide
project: homelab
tags:
  - homelab
  - documentation
  - consolidation
  - epistemic-triad
  - walkthrough
---

# Walkthrough: Homelab Architecture Consolidation Documents Reorganization

Operational walkthrough of the reorganization of the Homelab Architecture Consolidation documentation across the epistemic triad:
1. Standardized the ADR around **MADR 4.0** with purely architectural commitments (delegating exact schema fields to the Plan).
2. Deepened the Discussion with authentic historical engineering narrative while stripping out "decision voice" and absolutist language.
3. Framed the Plan as the **authoritative implementation specification** without re-litigating rationale.
4. Cleanly organized all consolidation lineage artifacts into `01-plans/homelab/consolidation/`.

---

## 1. Epistemic Model & Boundaries

```text
Discussion ──informs──> ADR ──constrains──> Plan
     ^                      ^                 |
     └──────────────────────┴─────────────────┘
                cross-references
```

> **Epistemic Rule**: The same fact may appear in multiple documents only when it serves a different epistemic purpose:
> - **Discussion ([`02-discussions/homelab/architecture-migration-v3-to-v4.md`](../../../02-discussions/homelab/architecture-migration-v3-to-v4.md))**: *Why did we get here?* Preserves uncertainty, historical context, friction points, rejected alternatives, and how the reasoning evolved.
> - **ADR ([`03-records/decisions/homelab-3tier-architecture-and-provenance.md`](../../../03-records/decisions/homelab-3tier-architecture-and-provenance.md))**: *What was decided?* Concise MADR 4.0 record answering what problem was being solved, what forces mattered, what options were considered, what was chosen, and what trade-offs were accepted.
> - **Plan ([`01-plans/homelab/consolidation/architecture-consolidation-roadmap-v4.md`](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v4.md))**: *What exactly are we going to build?* Authoritative implementation specification containing contracts, schemas, security invariants, phased milestones (P0–P5), and runbooks.
> - **Project Hub ([`06-projects/homelab/README.md`](../../../06-projects/homelab/README.md))**: *Where do I find it?* Pure navigation layer indexing the current triad and historical predecessors.

---

## 2. Document Refinements Applied

### A. Architectural Decision Record (`homelab-3tier-architecture-and-provenance.md`)
- **MADR 4.0 Standard**: Formatted into Context & Problem Statement $\to$ Decision Drivers $\to$ Considered Options $\to$ Decision Outcome $\to$ Pros and Cons $\to$ Consequences $\to$ More Information.
- **Architectural-Level Commitments**: Retains the requirement that *three independent identities must exist* (deployment configuration revision, upstream source revision, container artifact digest), but delegates the exact JSON field names (`deployment_config_revision`, etc.) exclusively to the Plan.
- **Digest Immutability vs. Artifact Identity**: Clarified that *OCI container images produced by CI act as provenance objects; the immutable identity of the deployed artifact is its OCI digest, with source commit provenance carried via the `org.opencontainers.image.revision` label*.
- **Neutral Decision Rationale**: Replaced evaluative phrasing with neutral systems language: *"because it addresses the identified coupling and provenance problems while retaining a bounded operational control path"*.

### B. Architectural Discussion (`architecture-migration-v3-to-v4.md`)
- **Eliminated "Decision Voice"**: Replaced ADR-style phrases (`"The Decision: Reject local cloning..."` and `"The Adopted Resolution:"`) with narrative exploratory phrasing (`"Resulting Direction: The exploration ultimately converged on..."`).
- **Conceptual Precision**: Clarified that the architecture decouples into **three core tiers** connected by intermediate artifacts and an isolated filesystem state root, avoiding conflation into a 5-tier model.
- **Tempered Tone**: Removed absolutist claims (e.g. replaced `"could not be cleanly open-sourced"` with `"made clean open-sourcing difficult without stripping Homelab configuration"`, and `"100% pure application code"` with `"allows the software repository to remain free of Homelab-specific infrastructure"`).
- **Historical Analysis vs. Sales Pitch**: Retitled Section 4 to *"What Became Possible After the Architectural Separation"* and framed the comparisons around concrete historical friction versus engineering motivations.

### C. Implementation Roadmap & Execution Plan (`architecture-consolidation-roadmap-v4.md`)
- **Authoritative Implementation Specification**: Clarified role as the authoritative implementation specification governing concrete phased rollout.
- **Pure Constraints**: Kept technical requirements (such as `git ls-remote` commit equality) as crisp specification invariants rather than re-arguing their rationale.
- Header bidirectionally cross-links to both the ADR and Discussion.

### D. Subsystem Lineage Directory (`01-plans/homelab/consolidation/`)
- Relocated all 6 roadmap and guide documents (v1–v4) into `01-plans/homelab/consolidation/`.
- All intra-vault links updated and verified across project hubs and journal entries.

---

## 3. Verification

- `python scripts/validate-brain.py`: **`✅ All checks passed. Brain structure is valid.`**
- `python scripts/test_validator.py`: **`Ran 10 tests in 0.001s ... OK`**
