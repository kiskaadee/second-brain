# Skill Evaluation Checklist

This checklist is consulted during **Stage 5: Authoring & Scaffolding** and **Stage 6: Dogfooding & Refinement**. Tiers 1 and 2 are the mandatory baseline, verified at Stage 4 (Design Specification). Tiers 3 and 4 are applied judgment during authoring and dogfood refinement.

---

## Tier 1: Universal Engineering Invariants (Already Checked at Stage 4)

| Criterion | Question to Ask |
| :--- | :--- |
| Explicit Responsibility | Is there a single, recurring problem this skill owns? |
| Explicit Boundary & Handoff | Does it clearly state where it stops and what it hands off to? |
| One Authoritative Owner | Is every rule owned by exactly one document? Are there competing definitions? |
| Behaviorally Meaningful | Would deleting any individual instruction change agent behavior? |
| Observable Completion | Can you point to a concrete artifact, test status, or signal that proves the skill finished? |

---

## Tier 2: Platform & Runtime Constraints (Already Checked at Stage 4)

| Criterion | Question to Ask |
| :--- | :--- |
| Invocation Metadata | Is `disable-model-invocation: true` set for user-invoked skills? Is it absent for model-invoked skills? |
| Description Semantics | For model-invoked: does the description include explicit trigger conditions and behavioral anchors? |
| Directory Layout | Do all supporting files live under `references/` or `scripts/` relative to `SKILL.md`? |
| Interskill Calling | Are skill dependencies invoked via the harness tool, not via markdown links? |

---

## Tier 3: Contextual Design Heuristics (Applied During Stage 5 When Justified)

Apply these only when the diagnosed structural mode warrants them. Not every skill needs every heuristic.

| Heuristic | When to Apply |
| :--- | :--- |
| **Operational State Machine** | Multi-step procedural workflows where premature completion is observed. |
| **Hard Anti-Skipping Gates** | Stopping conditions ("No X, no Phase Y") when the model reliably rushes past tedious verification. |
| **Externalized State** | Workflows spanning multiple turns or subagents where progress tracking would otherwise be lost. |
| **Progressive Disclosure** | When the body of `SKILL.md` is diluting the primary procedure with schemas, examples, or branch rules. Move those into `references/`. |
| **Asymmetric Context Decoupling** | When a high-context exploration phase should be separated from a low-context review phase. |
| **Behavioral Anchors** | When compact pretrained terms (*tight*, *seam*, *airlock*, *frontier*) reliably steer the model without verbose essays. |

**Deletion Test for Heuristics**: Before adding a Tier 3 control, ask: "If I don't add this, what specific observed failure am I risking?" If you cannot name an observed failure mode, don't add it.

---

## Tier 4: Authoring Quality Heuristics (Applied During Stage 5 and Post-Dogfood Refinement)

These are style and clarity standards for both `SKILL.md` and `README.md`:

| Heuristic | Positive Form |
| :--- | :--- |
| **Side-by-Side Learner Voice** | Write as a developer sharing what they learned with another developer, not as an authority figure delivering instructions. |
| **Rhetorical Restraint** | Make ideas interesting through the quality of the explanation itself, not through dramatic transitions or manufactured enthusiasm. |
| **Explanatory Guidance** | Explain useful mechanisms and mental models directly. Avoid motivational pep talks and excessive negative bans. |
| **Formatting Conventions** | Clean GitHub-flavored markdown. No em-dashes. |

### The Behavioral Deletion Test

Before finalizing any `SKILL.md`, apply this test to every paragraph and every instruction:

> *"If I deleted this instruction, would the agent behave differently in a way that matters?"*

- If **no**: delete it.
- If **yes**: keep it, and verify it is placed where the agent reads it at the right moment in the workflow.

### The README/SKILL Separation Test

A README should answer: *"What is this skill, why does it exist, when do I invoke it, and what does it produce?"*

A SKILL.md should answer: *"What does the agent do step by step, what are the invariants, and when does it stop?"*

If the README is becoming a compressed copy of SKILL.md, strip it back to the capability contract:
1. Identity (what it is)
2. User Value (why it matters)
3. Invocation (when to use / when not to use)
4. Behavior (overview, not full procedure)
5. Outputs (concrete deliverables)
6. Boundaries (what it refuses to do)
7. Package Structure (manifest)
