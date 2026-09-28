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
* **Primary Role**: Maintains the personal knowledge graph, curates unprocessed drafts from `00-inbox/` into canonical lifecycle directories (`01-plans/`, `02-discussions/`, `03-records/`, `04-learning/`, `05-agents/`, `06-projects/`), enforces strict frontmatter and link schemas, and executes automated validation.
* **Core Invariants & Taxonomy**:
  * **Seven Lifecycle Directories**: `00-inbox/` (capture), `01-plans/` (intent), `02-discussions/` (exploration), `03-records/` (historical memory), `04-learning/` (understanding, guides, practice), `05-agents/` (machine context), and `06-projects/` (system hubs).
  * **Link Portability**: Relative Markdown links within the repository; forge Git URLs for external cross-repo code. Never use machine-specific absolute file URIs (`file:///`).
  * **Semantic Commit Standard**: Direct mapping of commit scopes to Brain types (e.g. `knowledge(topic): ...`, `journal(proj): ...`, `agent(name): ...`).
  * **Integrity Validation**: Must pass `python scripts/validate-brain.py` before every commit.

---

## 2. Canonical Agent Specification

The following specification represents the active behavioral contract configured for `/home/kiskaadee/Brain/AGENTS.md`:

````markdown
[Consult the live, root-level AGENTS.md for the authoritative version-controlled repository rules.]
````

For the full detailed rules, see [Root AGENTS.md](../../AGENTS.md).

---

## 3. Related Resources & Context

* [Second Brain Root Index](../../README.md)
* [Second Brain Governance & Agent Guide](../../AGENTS.md)
* [Scientific Incident Investigation & Epistemic Journaling](../../04-learning/knowledge/methods/incident-investigation-and-journaling.md)
