---
type: discussion
status: resolved
project: brain
date: 2026-09-28
tags:
  - brain
  - architecture
  - taxonomy
  - epistemic-lifecycle
  - governance
---

# Architectural Discussion: Brain Epistemic Lifecycle Taxonomy

## Problem Statement

As the Second Brain vault grew organically beyond 180 files, the repository's initial organizational model began to break down under daily usage. Documents were grouped primarily by target technology or broad topic containers (`homelab/`, `learning/`, `practice/`, `projects/`, `records/`).

This organic structure suffered from several fundamental failure modes:

1. **Taxonomy Conflation (Epistemic Role vs. Project Scope)**: A document concerning Homelab might be an actionable implementation roadmap, an exploratory architectural debate, an operational runbook, an incident post-mortem, or an ADR. Because folders were treated as subject-matter buckets (`projects/homelab/`, `homelab/`, `learning/`), documents with fundamentally different cognitive roles sat alongside one another.
2. **The "Archive" Anti-Pattern**: Projects and roadmaps maintained local `archive/` subdirectories (e.g. `projects/homelab/archive/`). Moving a completed or abandoned plan into an archive folder broke incoming relative Markdown links across journals and ADRs, created duplicate parallel directory trees, and treated lifecycle progression as a filesystem move rather than document state.
3. **Ambiguity Between Retrospective and Prospective Analysis**: Exploratory architectural inquiries (debating alternatives before deciding) were mixed with daily journals or incident post-mortems under `records/` or scattered across project folders. Prospective uncertainty ("Why and what if?") was structurally conflated with retrospective empirical fact ("What happened and what failed?").
4. **Project Hubs as Document Containers**: Directories under `projects/` functioned simultaneously as navigational entry points and arbitrary document dumping grounds. There was no clear structural rule determining whether a document belonged inside `projects/<name>/` or in a functional directory like `learning/guides/` or `records/decisions/`.
5. **Tooling & Agent Drift**: AI agents and automated scripts navigating the vault lacked deterministic paths. When generating artifacts, agents struggled to choose between `inbox/`, project-specific folders, and top-level directories.

The vault needed a structural refactoring centered on a durable organizing principle: **the epistemic role of information in the engineering lifecycle**.

---

## Context and Analysis

### 1. Epistemic Role as the Primary Organizing Axis

Information in an engineering system is not defined solely by what technology it touches; it is defined by **its role in human and system cognition**:

* **Capture (`00-inbox/`)**: Unprocessed, ephemeral observations and rough drafts requiring zero-friction capture without classification barriers.
* **Intent (`01-plans/`)**: Forward-looking, actionable roadmaps, phased specifications, and execution blueprints answering: *"What do we intend to build?"*
* **Exploration (`02-discussions/`)**: Prospective inquiries, architectural trade-offs, and alternative analyses answering: *"Why and what if?"*
* **History (`03-records/`)**: Immutable historical memory answering: *"What happened, when did it happen, and what was decided?"* (journals, empirical debug RCAs, ADRs).
* **Understanding (`04-learning/`)**: Durable knowledge, operational SOPs, and deliberate practice answering: *"What do we understand and how do we operate it?"*
* **Machine Context (`05-agents/`)**: Machine-readable agent profiles, prompt modules, behavioral boundaries, and operational skills.
* **System Hubs (`06-projects/`)**: Canonical navigation nodes, topology mappings, forge links, and cross-cutting index entry points.

### 2. State as Metadata, Not Folder Placement

A central insight of the refactor is that **lifecycle status belongs in YAML frontmatter, never in directory placement**:

```text
# Anti-pattern: Moving files breaks the link graph
01-plans/homelab/feature.md  ──(completed)──>  01-plans/homelab/archive/feature.md  ❌

# Correct: Status changes, path remains immutable
01-plans/homelab/feature.md  [status: active] ──> [status: completed]               ✅
```

Eliminating `archive/` preserves every relative link throughout the knowledge graph. A plan referenced in an ADR or daily journal remains at its permanent URI regardless of whether it is `draft`, `active`, `completed`, or `abandoned`.

### 3. The Boundary Between Discussions and Records

A critical distinction debated during the design was the separation between `02-discussions/` and `03-records/`:

* **`02-discussions/` (Prospective Exploration)**: Documents open problem spaces where the solution is not yet determined. Multiple competing options (Option A vs. Option B) are evaluated with trade-offs. When consensus is reached, the discussion is marked `status: resolved` and explicitly links forward to the resulting plan (`01-plans/`) or decision (`03-records/decisions/`). It is a permanent record of *why* choices were made.
* **`03-records/debug/` (Retrospective Empirical Reality)**: Incident investigations and root cause analyses (RCAs) document system failures that actually occurred. They follow the scientific method: observation, hypotheses tested against logs and system facts, declarative fix, and recovery proof. They are empirical history, not prospective option design.
* **`03-records/decisions/` (Architectural Commitments)**: ADRs capture point-in-time commitments. While discussions explore options, ADRs record the chosen option and its lasting consequences.

### 4. Project Hubs as Navigation Nodes, Not Containers

Earlier iterations allowed projects to own extensive subtrees under `projects/`. This created a dual-hierarchy dilemma: should a NixOS guide live in `learning/guides/nixos/` or `projects/nixos/guides/`?

The resolution was to strictly constrain `06-projects/`:
* Every project hub is strictly located at `06-projects/<project>/README.md` (`max_depth=2`, `require_filename="README.md"`).
* No arbitrary documents or subfolders live in `06-projects/`.
* A project hub is an **index and topology node**, pointing outward across the numbered taxonomy to active plans in `01-plans/<project>/`, open discussions in `02-discussions/<project>/`, runbooks in `04-learning/guides/<project>/`, and historical debug logs in `03-records/debug/`.

### 5. Why `00-inbox/` Is Exempt from Validation

Zero-friction capture is paramount. If an engineer or agent must determine the exact frontmatter type, valid tags, and verified links before jotting down a thought, capture will not happen.

Therefore, `00-inbox/` sits outside the validated knowledge graph:
* It has no frontmatter requirement (`allow_unclassified=True`).
* It has no type contract (`expected_type=None`).
* It is ignored by link validation until curated into directories `01` through `06`.

### 6. The Rejection of Root Symlinks (`inbox -> 00-inbox`)

During the migration planning, a proposal was made to create a root symlink `inbox -> 00-inbox` for backwards compatibility with existing capture tools.

This was explicitly **rejected**:
* Symlinks create aliasing and dual-path confusion for recursive filesystem traversals.
* Markdown links could resolve through either path, weakening validation guarantees.
* Agents could discover both paths and produce inconsistent references.
* The clean architectural path was to update the capture tools (`~/.gemini/config/scripts/inbox-capture.sh`, `user_global` rules) directly to target `00-inbox/`.

---

## Options Evaluation

| Architectural Question | Option A (Adopted) | Option B (Rejected) | Rationale |
| :--- | :--- | :--- | :--- |
| **Primary Organization** | Seven numbered lifecycle directories (`00-06`) | Technology / Project folders owning all sub-types | Projects change and overlap; the epistemic role of knowledge is invariant across engineering domains. |
| **Lifecycle Archiving** | Metadata-based (`status: completed` in frontmatter) | Physical `archive/` directories | Physical moves break incoming Markdown links across historical journals and ADRs. |
| **Investigation Artifacts** | `03-records/debug/` for empirical RCAs; `02-discussions/` for prospective design | Combined `records/discussions/` | Conflates retrospective debugging of broken systems with prospective evaluation of architectural options. |
| **Project Directories** | Constrained index hubs (`06-projects/*/README.md` only) | Deep project trees containing plans, guides, notes | Creates competing locations for guides and plans, fragmenting the vault. |
| **Validator Contract** | Declarative `DirectoryContract` enforcing type, depth, and filenames | Simple regex frontmatter check on all `.md` files | Regex checks cannot enforce directory shape, allowed nesting depths, or structural constraints like project README hubs. |
| **Inbox Compatibility** | Update all integration points to `00-inbox/` directly | Root symlink `inbox -> 00-inbox` | Avoids alias confusion, double traversals, and non-canonical path generation. |
| **Agent Assets** | Dedicated lifecycle category `05-agents/` (`profiles/`, `skills/`) | Embedded within project directories or root | Agents and skills are machine context that span multiple projects and workstations. |

---

## Consensus and Resolution

The numbered lifecycle taxonomy was adopted in full. The repository structure was reorganized into seven canonical directories governed by declarative contracts in `scripts/validate-brain.py`:

```text
~/Brain
├── 00-inbox/           # Capture: unvalidated staging
├── 01-plans/           # Intent: roadmaps & blueprints (status: draft | active | completed | abandoned)
├── 02-discussions/     # Exploration: architectural inquiries & trade-offs (status: open | resolved)
├── 03-records/         # History: journals, debug post-mortems, ADRs
├── 04-learning/        # Understanding: knowledge/, guides/, practice/
├── 05-agents/          # Machine Context: profiles/, skills/
└── 06-projects/        # System Hubs: <project>/README.md topology indices
```

### Forward Linkages
* **Execution Blueprint**: The migration was carried out according to the completed implementation plan at [Brain Taxonomy & Lifecycle Migration Plan](../../01-plans/brain/taxonomy-lifecycle-migration.md).
* **Governance**: The rules governing this taxonomy are codified in [Root AGENTS.md](../../AGENTS.md) and enforced deterministically by `scripts/validate-brain.py`.
