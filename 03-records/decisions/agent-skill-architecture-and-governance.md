---
type: decision
status: accepted
project: brain
date: 2026-09-29
tags:
  - architecture
  - agents
  - skills
  - documentation
  - governance
---

# Architectural Decision Record: Agent Skill Architecture, Proportional Sizing, and Meta-Builder Governance

## 1. Context and Problem Statement

As AI coding assistants have evolved from one-off chat tools into semi-autonomous pairing partners, our workstation and knowledge vault have accumulated specialized agent skills (`engineering-investigation`, `engineering-tutor`, `documentation-router`, `git-commit`). 

However, authoring new skills previously relied on informal, essayistic prompt writing. This approach suffered from two opposing failure modes:
1. **Under-specified Prompts**: Descriptive instructions that tell an agent to "be thorough", leading to premature completion, skipped verification steps, attention dilution, and conversational drift.
2. **Ceremonial Over-Engineering**: Attempting to force every capability into an elaborate phased state machine with task graphs, rigid airlocks, and excessive file fragmentation.

Furthermore, our knowledge vault lacked a governed epistemic home for general engineering methodologies, leaving durable understanding without a distinct container or authoring specification.

We needed an architectural standard for how agent skills are classified, bounded, authored, and verified, along with an interactive meta-capability to guide future skill creation.

---

## 2. Decision Drivers

* **Operational Reliability**: Ensuring multi-step procedural workflows enforce observable verification gates before advancing.
* **Proportional Structure**: Preventing simple reference or transformation capabilities from being saddled with unnecessary state-machine ceremony.
* **Epistemic Integrity**: Upholding the Brain's Cardinal Invariant (*documentation type is determined by the nature of the knowledge, not the activity*) by giving durable, reusable understanding an explicit container.
* **Human Architectural Authority**: Ensuring that skill creation remains an interactive engineering design process where the human decides intent and boundaries, rather than delegating blind prompt generation to an autonomous model.
* **Empirical Grounding**: Establishing that skill refinement must respond to observed trajectory variance and verify non-regression, rather than applying speculative optimizations.

---

## 3. Considered Options

* **Option 1: Informal Ad-Hoc Prompts**. Continue authoring skills as single-file markdown prompts when needed, relying on conversational steering to correct variance.
* **Option 2: Universal State-Machine Standard**. Mandate that all agent skills must be modeled as formal operational state machines with phased airlocks, externalized task graphs, and pre-condition gates.
* **Option 3: Four-Tier Architecture with Proportional Structural Sizing**. Classify skills into primary structural modes (Reference, Transformation, Procedural Workflow, Interactive Elicitation), enforce universal engineering invariants, apply contextual heuristics only where justified, and govern creation via an interactive meta-skill with an explicit human review gate.

---

## 4. Decision Outcome

Chosen option: **Option 3: Four-Tier Architecture with Proportional Structural Sizing**.

We adopt the following architectural commitments:

### 1. Four-Tier Epistemic Skill Taxonomy
Every skill in our ecosystem is governed across four distinct tiers:
* **Tier 1 — Universal Engineering Invariants**: Explicit responsibility, bounded scope with explicit handoffs, single authoritative owner per rule, behaviorally meaningful instructions (deletion test), and observable completion artifacts where state changes occur.
* **Tier 2 — Platform & Runtime Constraints**: Discovered platform realities (Gemini YAML frontmatter, `disable-model-invocation: true` for user-only skills, context pointer descriptions for model-invoked skills, co-located `references/` and `scripts/`).
* **Tier 3 — Contextual Design Heuristics**: Levers applied strictly when problem complexity warrants (operational state machines, hard anti-skipping gates, externalized state, progressive disclosure, asymmetric context pressure, behavioral anchors).
* **Tier 4 — Authoring Quality**: Side-by-side learner voice, rhetorical restraint, explanatory guidance, and clean markdown without em-dashes.

### 2. Proportional Structural Modes
Skills are sized according to their primary operational mode:
* **Reference & Framing**: Conceptual models and vocabulary. (No state machine).
* **Transformation & Synthesis**: Single-pass processing. (Preconditions + negative boundary + output schema).
* **Procedural Workflow**: High-friction execution disciplines. (Phases + hard pre-condition gates + proof artifacts).
* **Interactive Elicitation**: Collaborative dialogue and tutoring. (Batched rounds + fact/decision boundary).
* *Modes may blend where justified* (e.g. procedural execution with interactive human checkpoints).

### 3. Implementation of the `skill-builder` Meta-Skill
We deploy `skill-builder` (`~/.gemini/config/skills/skill-builder/SKILL.md` and `/build-skill`) as an **Interactive Elicitation skill**. 
* **Division of Labor**: The human decides architectural intent, approves boundaries, and owns the final design. `skill-builder` investigates friction, sizes structure, challenges overlap against the live skill catalog, proposes the formal design specification, scaffolds files, and guides regression testing.
* **Mandatory Review Gate**: `skill-builder` halts at a formal **Skill Design Specification** and requires explicit human approval before any files are authored.

### 4. Epistemic Integration of Knowledge Articles
We formalize **Knowledge Articles** (`04-learning/knowledge/`, `type: knowledge`) within [`documentation-router`](../../05-agents/skills/documentation-router.md):
* Governed by `references/knowledge-authoring.md` (in `documentation-router`).
* Captures generalized, reusable understanding and methodologies written in a side-by-side learner voice.
* Preserves canonical ownership: general lessons live in Knowledge; project explorations live in Discussions; point-in-time commitments live in ADRs; implementation steps live in Plans; incident RCAs live in Debug Records.

### 5. Investigation Invariant Refinements
We refine `engineering-investigation`:
* **Evidence Before Hypothesis**: Characterize the failure symptom with observable evidence (logs, error statuses, or reproductions) before forming implementation theories.
* **Traceable Diagnostic Mutations & Cleanup**: Every temporary diagnostic modification must have an identifiable cleanup boundary and verification method.
* **Sensitive Data Redaction & Zero Leakage**: Diagnostic evidence must be inspected for secrets before being surfaced or persisted.

---

## 5. Consequences

### Positive Consequences
* **Variance Reduction**: Procedural workflows gain enforceable gates that prevent models from skipping verification.
* **Anti-Overengineering**: Non-procedural skills remain lightweight without ceremonial boilerplate.
* **Cognitive Clarity**: Authors have an explicit 6-stage lifecycle and diagnostic questions to design new skills.
* **Vault Completeness**: General engineering methodologies now have a governed, first-class home in `04-learning/knowledge/`.
* **Safe Refinement**: Skills are adjusted using the smallest relevant mechanism and verified against regressions.

### Negative Consequences & Accepted Trade-offs
* **Initial Authoring Friction**: Designing a skill through `skill-builder` requires answering substantive architectural questions rather than instantly generating a prompt.
* **Catalog Maintenance**: Global skills and their Brain mirrors must be kept synchronized when authoring specifications evolve.
