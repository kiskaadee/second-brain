---
type: agent
status: active
name: second-brain
target_workspace: ssh://git@gitea.roadtotech.me:2223/kiskaadee/second-brain
project: brain
tags:
  - knowledge-graph
  - second-brain
  - documentation
  - taxonomy
  - curation
  - validator
---

# Second Brain Knowledge Graph & Curation Agent

## 1. Overview & Operational Scope

* **Target Workspace**: `ssh://git@gitea.roadtotech.me:2223/kiskaadee/second-brain` (`/home/kiskaadee/Brain`)
* **Primary Role**: Maintains the personal knowledge graph, curates unprocessed drafts from `inbox/` into canonical knowledge/project/record types, enforces strict frontmatter and link schemas, and executes automated validation.
* **Core Invariants & Taxonomy**:
  * **Five Semantic Directories**: `inbox/` (staging), `knowledge/` (durable understanding), `projects/` (contextual docs), `records/` (historical logs), `practice/` (LeetCode drills), and `agents/` (agent catalog).
  * **Link Portability**: Relative Markdown links within the repository; forge Git URLs for external cross-repo code. Never use machine-specific absolute file URIs (`file:///`).
  * **Semantic Commit Standard**: Direct mapping of commit scopes to Brain types (e.g. `knowledge(topic): ...`, `journal(proj): ...`, `agent(name): ...`).
  * **Integrity Validation**: Must pass `python scripts/validate-brain.py` before every commit.

---

## 2. Canonical Agent Specification

The following specification represents the active behavioral contract configured for `/home/kiskaadee/Brain/AGENTS.md`:

````markdown
[Consult the live, root-level AGENTS.md for the authoritative version-controlled repository rules.]
````

For the full detailed rules, see [Root AGENTS.md](../AGENTS.md).

---

## 3. Related Resources & Context

* [Second Brain Root Index](../README.md)
* [Second Brain Governance & Agent Guide](../AGENTS.md)
* [Scientific Incident Investigation & Epistemic Journaling](../knowledge/methods/incident-investigation-and-journaling.md)
