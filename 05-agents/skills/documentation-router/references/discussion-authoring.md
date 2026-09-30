# Discussion Authoring Specification

## Epistemic Role & Core Purpose

A **Discussion** explores architectural inquiries, problem statements, trade-offs, and design alternatives. It answers:
> *"What are we trying to understand, and what did we learn while exploring it?"*

A discussion preserves the intellectual journey: why a legacy model broke down, what options were considered, what failed during investigation, and how the reasoning evolved. It is an exploration, not an execution manual or an authoritative decree.

---

## 1. Epistemic Invariants & Voice Rules

1. **Exploratory Narrative Tone**:
   Write in a thoughtful, investigative, retrospective voice. Focus on forces, constraints, and dilemmas.
2. **Zero "Decision Voice"**:
   Discussions inform decisions; they do not issue them.
   * **Prohibited**: `"The Decision: Reject local cloning on the host."`
   * **Correct**: `"Resulting Direction: The exploration ultimately converged on rejecting local cloning on the appliance host in favor of commit equality verification via git ls-remote."`
3. **Preserve Uncertainty & Rejected Alternatives**:
   Do not erase dead ends or false starts. Document why an option (e.g. calculating commit distance or using message brokers) was considered, what failure mode or friction it introduced, and why it was set aside.
4. **Tempered Language (Avoid Absolutes)**:
   Avoid rhetorical hyperbole.
   * **Prohibited**: `"The software could not be cleanly open-sourced"` or `"100% pure code"`.
   * **Correct**: `"Hosting infrastructure co-located with code made clean open-sourcing or external sharing difficult without stripping private configuration."`
5. **No Implementation Procedure Duplication**:
   Do not include multi-step phased execution checklists, bash deployment runbooks, or detailed schema models.
6. **Convergence, Not Mandate**:
   End with how the exploration converged, linking forward to the resulting ADR or Plan without re-listing their formal resolution contracts.

---

## 2. Standard Document Structure

```markdown
---
type: discussion
status: open | resolved
project: <project-name>
date: YYYY-MM-DD
tags: [list, of, tags]
---

# Architectural Discussion: <Descriptive Title>

## 1. Problem Statement & Historical Context
* Initial setup and why the original model looked attractive.
* Concrete operational failures, friction points, or unexpected behaviors observed.

## 2. Context & Analysis: Core Dilemmas
* Underlying systems design dilemma (e.g. KISS vs. separation of concerns).
* Conceptual clarity: clearly distinguish tiers, intermediate artifacts, and storage/runtime boundaries.

## 3. Evaluated Dilemmas & Rejected Alternatives
* Detailed exploration of alternatives considered:
  - Option A: Problem it attempted to solve, why it fell short, and resulting trade-off rationale.
  - Option B: Problem it attempted to solve, why it fell short, and resulting trade-off rationale.

## 4. What Became Possible After the Architectural Separation
* Structured comparison: Historical constraints of the old model vs. engineering motivations unlocked by the new model.

## 5. Convergence & Successors
* Summary of how the exploration converged.
* Links forward to the governing Architectural Decision Record (ADR) and implementation Plan.
```
