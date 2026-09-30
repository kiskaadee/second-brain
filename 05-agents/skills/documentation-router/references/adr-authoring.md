# ADR (MADR 4.0) Authoring Specification

## Epistemic Role & Core Purpose

An **Architectural Decision Record (ADR)** captures a point-in-time architectural or design commitment that constrains future engineering work. It answers:
> *"What did we decide, and why?"*

The ADR is a compact, durable historical contract. It establishes architectural boundaries, selected models, and accepted trade-offs. It is not an implementation runbook, an operational manual, or a record of diagnostic procedures.

---

## 1. Epistemic Invariants & Boundaries

1. **MADR 4.0 Structural Sequence**:
   Adheres to the standard sequence:
   $$\text{Context \& Problem Statement} \longrightarrow \text{Decision Drivers} \longrightarrow \text{Considered Options} \longrightarrow \text{Decision Outcome} \longrightarrow \text{Pros \& Cons} \longrightarrow \text{Consequences} \longrightarrow \text{More Information}$$
2. **Architectural Commitments, Not Implementation Procedure**:
   * *In the ADR*: "We adopt separate Software and Deployment layers; deployment configuration, upstream source provenance, and container artifact identity must be independently observable."
   * *In the Plan*: The exact 7 platform primitives table, internal JSON schema field names (`deployment_config_revision`, etc.), execution timeouts, and bash runbooks.
3. **Immutability vs. Artifact Identity**:
   Distinguish mutable identifiers (like image tags) from cryptographic ones. OCI images produced by CI act as provenance objects; the immutable identity of the deployed artifact is its content-addressed OCI digest, with source commit provenance carried via metadata labels.
4. **Neutral Systems Language**:
   Justify outcomes through clear trade-offs against the decision drivers, rather than subjective or promotional assertions (e.g. *"addresses the identified coupling while retaining a bounded operational control path"* rather than *"strictly preserves minimal complexity"*).
5. **Durable Historical Record**:
   Do not rewrite an accepted ADR merely because subsequent implementation evolves. If a fundamental architectural commitment changes, record a new ADR that explicitly supersedes the earlier record.

---

## 2. Standard MADR 4.0 Document Structure

```markdown
---
type: decision
status: proposed | accepted | superseded
project: <project-name>
date: YYYY-MM-DD
tags: [list, of, tags]
---

# <Short Architectural Decision Title>

## Context and Problem Statement
Concise framing of the problem, background forces, and the central architectural question.

## Decision Drivers
* Key operational, architectural, or organizational forces driving the choice.
* Criteria against which options are evaluated.

## Considered Options
* **Option 1: <Name>** — Brief description.
* **Option 2: <Name>** — Brief description.
* **Option 3: <Name>** — Brief description.

## Decision Outcome
Chosen option: **Option X: <Name>**, because <neutral trade-off rationale grounded in decision drivers>.

### Summary of Architectural Commitments
1. **Primary Structural Boundary**: Clean separation of concerns across tiers/components.
2. **Provenance & Identity**: Architectural requirement for observable identities (delegating exact schema fields to implementation plans).
3. **Reconciliation & Control Path**: Direction and constraints of the control flow.
4. **State Isolation**: Filesystem or database boundary rules.

## Pros and Cons of the Options

### Option 1: <Name>
* Good, because <argument>.
* Bad, because <argument>.

### Option 2: <Name>
* Good, because <argument>.
* Bad, because <argument>.

### Option 3: <Name> (Adopted)
* Good, because <argument>.
* Bad, because <accepted trade-off>.

## Consequences
### Positive Consequences
* Key benefits and unlocked capabilities resulting from the decision.

### Negative Consequences & Accepted Trade-offs
* Operational overhead, constraints, or limitations accepted as part of the choice.

## More Information
* **Informing Discussion & Rationale**: Link to companion Discussion (if one exists).
* **Governed Implementation Roadmap**: Link to companion Plan (if one exists).
* **Project Hub**: Link to the relevant system or project landing page.
```
