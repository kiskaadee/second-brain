---
type: plan
status: active
project: brain
tags:
  - learning
  - skills
  - roadmap
  - implementation
---

# Plan: Scaffolded Learning Contracts Across Engineering Skills

> **Discussion Reference**: [`02-discussions/brain/learning-centered-engineering-workflow.md`](../../02-discussions/brain/learning-centered-engineering-workflow.md)
>
> **Core Objective**: Transition operational agent skills from "AI writes it" to "AI scaffolds, learner writes it", enforcing the learning contract across everyday engineering tasks.

---

## 1. Reality Check & Skill Inventory

Mapping the theoretical redesign to actual skills in [`skills`](https://github.com/kiskaadee/skills):

| Conceptual Capability | Actual Skill | Current State vs. Learning Mode |
| :--- | :--- | :--- |
| **Engineering Tutor** | `practice` | Hint ladder implemented (question $\to$ pointer $\to$ explanation $\to$ demo); learner attempts first. |
| **Troubleshooting** | `diagnose` | Evidence-first investigation; working-tree safety stops. |
| **Git Commits** | `git-commit` | Has a `/practice` branch, but still auto-drafts commit messages. Needs author mode. |
| **Documentation** | `document` | Determines document type and drafts it. Needs learner core-sentence prompt. |
| **Journaling** | `journal-builder` | Produces polished narrative. Needs scaffolding mode with diagnostic blanks. |

---

## 2. Phased Implementation Roadmap

### Phase 1: Minimal Learning Contract (`learning-contract.md`)
**Status**: ✅ **Completed**
- Defined binding rules in `profile/learning-contract.md`:
  - *Write rule*: In learning mode, agent provides facts and questions; learner writes reasoning.
  - *Assistance levels*: `independent`, `hints`, `substantial`, `shown-solution`.
  - *Evidence $\neq$ assessment*: Passing tests or commits are evidence, not claims of competence.
  - *Mode toggle*: Explicit `delivery` vs `learning` mode per session.

---

### Phase 2: Skill Scaffolding Experiments

Pick candidate skills to enforce the contract:
- **Option A: `git-commit` author mode**: Agent lists slices, changed behavior, tests present/missing, and asks 1–2 diagnostic questions. Learner writes the commit message; agent validates accuracy and scope against the diff.
- **Option B: `journal-builder` scaffold mode**: Builds a factual skeleton from `00-inbox/commit-log.csv` plus 3–5 targeted questions with blanks for learner answers.

---

### Phase 3: Practice Records & Delayed Retrieval

- Add `assistance:` and `revisit_after:` (target date) metadata to practice drill records.
- Surface due revisits manually during `practice` or weekly review.
- Revisits require **recall before reveal**: answer without opening the previous record, then compare.

---

### Phase 4: Two-Week Dogfood Evaluation

Test in real work (project commits, course modules, LeetCode drills) and evaluate:
1. Did the learner actually write the reasoning, or rubber-stamp?
2. Were questions anchored in the learner's actual work rather than generic quizzes?
3. On revisit, did recall succeed without viewing the answer?
4. Cut any steps that feel like bureaucratic drag.

---

### Phase 5 (Gated): Event Store & Service Integration

**Gate**: Proceed only if Phase 4 proves a concrete query need that filesystem files cannot answer (e.g. tracking concepts practiced with hints that were never retrieved independently).
- If triggered, implement as an isolated learning project in `~/Projects/tests/` (PostgreSQL with `FOR UPDATE SKIP LOCKED` and append-only event logging).
