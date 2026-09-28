---
type: project
status: active
tags:
  - second-brain
  - tooling
  - knowledge-graph
  - automation
---

# 🧠 Second Brain Platform & Tooling (`brain`)

The **Second Brain Platform** comprises the core infrastructure, structural validators, automation toolchains, and metadata extraction pipelines that maintain the personal knowledge graph and compile documentation artifacts.

---

## 🏛️ Overview & System Topology

The Second Brain platform operates through declarative schema enforcement, automated pre-commit integrity hooks, and downstream static site compilation:

```mermaid
graph TD
    CLI["Developer / Agent Workspace (`~/Brain`)"] --> PreCommit["Git Pre-Commit Hook (`validate-brain.py`)"]
    PreCommit --> Validation["Structural Validation (AST, Frontmatter, Links, Linters)"]
    Validation -->|Pass| Commit["Atomic Semantic Commit"]
    Commit --> PostCommit["Post-Commit Hook"]
    PostCommit --> Forge["Gitea Origin Push (`ssh://git@gitea.roadtotech.me:2223/kiskaadee/second-brain`)"]
    Forge --> DocsEngine["docs2site Compiler & Search Indexer"]
```

1. **Schema & Integrity Engine**: Python-based structural validation enforcing frontmatter presence, type contracts, relative link resolution, and Ruff/Pyright quality.
2. **Deterministic Extraction & Indexing Pipeline**: Planned standalone extraction utilities providing lexical signals, BM25/AST weights, and key terms without external API dependencies.
3. **Distribution & GitOps Pipeline**: Automated post-commit synchronization with the private Gitea forge and downstream documentation publishers.

---

## 📍 Source Code & Locations

| Target | Location / URL | Description |
| :--- | :--- | :--- |
| **Local Workspace** | `/home/kiskaadee/Brain` | Version-controlled knowledge repository and tooling scripts |
| **Gitea Forge** | `ssh://git@gitea.roadtotech.me:2223/kiskaadee/second-brain` | Canonical remote Git repository on Homelab Core |
| **Agent Spec** | [Second Brain Agent Spec](../../05-agents/profiles/second-brain.md) | Behavioral contract and curation protocol for Brain agents |

---

## 💬 Open Discussions

*None currently open.*

---

## 🚧 Work in Progress (Active Plans)

1. 🟡 [**Deterministic Term Extraction for Brain Documents**](../../01-plans/brain/deterministic-term-extraction.md) `[Active]`
   - Cheap, reproducible, auditable lexical extraction pipeline (`scripts/extract-terms.py`, `scripts/patch-terms.py`, `scripts/stopwords.txt`) to replace non-deterministic tag generation with structural AST weighting.
2. 🟡 [**Structural Refactoring for validate-brain.py Pipeline**](../../01-plans/brain/validate-brain-refactoring.md) `[Active]`
   - Multi-phase refactoring of the pre-commit integrity validator into a single-pass `Document`/`Issue` pipeline with line-numbered diagnostics and robust Markdown fence handling. (Phase 1 complete).

---

## 🛠️ Canonical Guides & Runbooks

* [**Deterministic Tag & Key Term Extraction Guide**](../../04-learning/knowledge/methods/deterministic-tag-extraction.md) — Algorithmic approaches and architectural comparison across statistical heuristics, AST parsers, and taxonomy matchers.

---

## 🏛️ Completed Milestones & Resolved Discussions

* 🟢 **Validation & Taxonomy Foundation** — Implementation of `scripts/validate-brain.py`, pre-commit hook enforcement, and five-category semantic schema.
* 🟢 **Multi-Agent Catalog** — Formalization of `agents/` store and operational profiles.
* 🟢 [**Brain Taxonomy & Lifecycle Migration**](../../01-plans/brain/taxonomy-lifecycle-migration.md) — Reorganized repository from organic structure into 7 numbered lifecycle directories (`00-inbox/` through `06-projects/`), introduced declarative `DirectoryContract` validation, executed 188-file migration and 199-link rewrites, and synchronized distributed `AGENTS.md` integration surfaces.
  - Companion Discussion: [Brain Epistemic Lifecycle Taxonomy](../../02-discussions/brain/taxonomy-and-lifecycle-architecture.md)
* 🟢 [**Incident Debug Records & Daily Journal Workflow Reorganization**](../../01-plans/brain/incident-debug-and-journal-workflow.md) — Established first-class `type: debug` records in `03-records/debug/`, strictly one daily journal per date in `03-records/journal/YYYY-MM-DD.md`, and automated inbox curation protocol.
