# Brain — AI Agent Guide

This repository is a personal knowledge graph. It is not a residency dashboard, a project tracker, or an Obsidian vault. It is a durable store of structured information across multiple types.

---

## Repository Purpose

The Brain stores five fundamentally different kinds of information:

| Directory | Contains |
| :--- | :--- |
| `inbox/` | Unprocessed captures — no classification required. Write first, classify later. |
| `knowledge/` | Durable understanding: concepts, technologies, and methods. |
| `projects/` | Contextual, project-specific documents. Each project owns its own sub-folder. |
| `records/` | Historical artifacts: journals, discussions, decisions, experiments. |
| `practice/` | Algorithm exercises, LeetCode writeups, and implementation drills. |

---

## Semantic Contracts

### `inbox/`
Local, uncommitted zero-friction capture zone. If the type or destination of a document is not immediately obvious, or while drafting/capturing raw thoughts, it belongs here. No metadata or classification is required at capture time. Documents in `inbox/` sit outside the committed knowledge graph until curated and moved into `knowledge/`, `projects/`, `records/`, or `practice/`.

### `knowledge/`
Documents that answer: *"If I read this six months from now, will this help me understand something?"*

Sub-directories:
- `concepts/` — Disciplinary concepts and algorithms (e.g., binary search, data structures).
- `technologies/` — Tool- and language-specific knowledge (e.g., Python, Docker, tmux).
- `methods/` — Backend engineering practices and methodologies (e.g., testing, auth, SQL).

Knowledge documents do not become the canonical location for project-specific information. A knowledge document describes *what something is*; a project document describes *how this project uses it*.

### `projects/`
Each project lives in its own sub-folder (e.g., `projects/homelab/`, `projects/nixos/`, `projects/magnetflix/`). The canonical entrypoint and landing page for any project must always be named `README.md` (e.g., `projects/homelab/README.md`) so that documentation renderers (such as `doc2site`) automatically compile it as the directory's index/landing page. Do not use `overview.md`.

#### Project Landing Page (`README.md`) Invariant
A project `README.md` is the user-facing entrypoint for that specific engineering project.
- **Never describe Brain conventions in a project README**: Do not explain vault taxonomies, frontmatter rules, or note-taking philosophies.
- **Required Sections**:
  1. **Overview & System Topology**: Broad architectural explanation of the system, its layers, and core capabilities.
  2. **Source Code & Locations**: Direct URLs to Git forge repositories (Gitea/GitHub), clone URLs, local workspace paths, and deployment targets.
  3. **💬 Open Discussions**: Links *strictly* to unresolved discussions that have not yet produced an active implementation plan.
  4. **🚧 Work in Progress (Active Plans)**: Links *strictly* to active plans (`status: active`) currently in progress or scheduled for execution.
  5. **🛠️ Canonical Guides & Runbooks**: Operational procedures and step-by-step SOPs.
  6. **🏛️ Completed Milestones & Resolved Discussions**: Historical reference section keeping completed roadmaps and foundational discussions organized without cluttering active WIP.

#### Standard Project Directory Structure
Every project follows a three-part lifecycle structure under its folder:

1. **`discussions/` — "Why & What If?"**
   - Architectural inquiries, problem statements, exploratory trade-off analyses, and evaluation of alternative paths (Model A vs. Model B).
   - *Format*: Problem Statement → Context & Analysis → Options Evaluation (Pros & Cons) → Consensus / Resolution / Open Questions.
   - *Lifecycle*: Open discussions remain active until consensus is reached, at which point they produce an actionable implementation plan.
   - *Frontmatter*: `type: discussion`, `project: <name>`, `date: YYYY-MM-DD`.

2. **`plans/` — "How & When?"**
   - Actionable implementation roadmaps, milestone breakdowns, and phased technical executions.
   - *Prerequisite*: A plan should ideally be the concrete output of a resolved discussion.
   - *Frontmatter*: `type: plan`, `status: draft | active | completed | abandoned`, `project: <name>`.

3. **`guides/` — "How to Use & Operate?"**
   - Practical, operational runbooks and user-facing standard operating procedures (SOPs).
   - *Content*: Answers concrete operational questions: *How to deploy a new service*, *How to rotate secrets*, *How to troubleshoot WAN rotation*. A guide explains how to **use and maintain** existing capabilities, not how to architect or implement new ones.
   - *Frontmatter*: `type: guide`, `project: <name>`.

The folder establishes context (ownership/locality). The document's `type` field establishes its semantic role. Projects may reference documents in other projects via relative links.

### `records/`
Historical artifacts. The original messy thinking is worth preserving — often what you want to recover later is not just the conclusion, but *why* you reached it.

Sub-directories:
- `journal/` — Dated engineering journals and retrospectives.
- `discussions/` — Conversations that informed decisions or produced knowledge.
- `decisions/` — Architectural decision records.
- `experiments/` — Prototypes, runbooks, and technical investigations.

### `practice/`
Unchanged in structure. Contains LeetCode writeups and Python solution files with their own Nix devShell environment. Do not reorganize this directory without reading its `flake.nix`.

---

## Metadata Convention

Every committed markdown document in the knowledge graph must have a YAML frontmatter block. `type` is the only universally required field. All other fields are type-specific or optional metadata extensions. (Documents in `inbox/` are uncommitted staging drafts and are exempt from metadata enforcement until curated).

### Core & Optional Fields

- **`type`** *(Required)*: `knowledge`, `project`, `plan`, `guide`, `decision`, `journal`, `discussion`, `experiment`, `practice`, `inbox`, `reference`.
- **`tags`** *(Optional)*: List of keyword tags (e.g., `tags: [homelab, ddns, networking]` or YAML list format) applicable to any document type for cross-cutting discovery.
- **`project`** *(Optional)*: Project identifier (e.g., `project: homelab`, `project: dynu-monitor`, `project: bitetrack`) indicating context ownership.
- **`status`** *(Conditional)*: Lifecycle status for plans (`draft`, `active`, `completed`, `abandoned`), decisions (`proposed`, `accepted`, `superseded`), projects (`planned`, `active`, `paused`, `completed`), knowledge (`draft`, `stable`), and practice (`active`, `completed`).

### Frontmatter Templates

```yaml
# knowledge
---
type: knowledge
status: draft | stable
topics: [list, of, topics]
tags: [optional, tags]
related: [optional, relative, paths]
project: optional-project-name
---

# project (README.md landing pages)
---
type: project
status: planned | active | paused | completed
tags: [list, of, tags]
---

# plan
---
type: plan
status: draft | active | completed | abandoned
project: project-name
tags: [list, of, tags]
---

# guide
---
type: guide
project: project-name
tags: [list, of, tags]
---

# decision
---
type: decision
status: proposed | accepted | superseded
project: project-name
tags: [list, of, tags]
---

# journal (historical record)
---
type: journal
date: YYYY-MM-DD
tags: [list, of, tags]
project: optional-project-name
---

# experiment (prototypes, investigations, runbooks)
---
type: experiment
status: draft | active | completed
project: project-name
tags: [list, of, tags]
date: YYYY-MM-DD
---

# discussion (conversations, architectural evaluations)
---
type: discussion
project: project-name
tags: [list, of, tags]
date: YYYY-MM-DD
---

# practice
---
type: practice
status: completed | active
topics: [list, of, topics]
tags: [optional, tags]
---

# inbox (unprocessed captures)
---
type: inbox
created: YYYY-MM-DD
tags: [optional, tags]
project: optional-project-name
---
```

**Important:** Folder location does not automatically determine every metadata field. A document inside `projects/homelab/plans/` is a `plan`, not a `project`. The folder establishes context. The `type` field establishes semantic role.

---

## Link Conventions

- Use standard relative Markdown links for intra-vault files: `[text](../relative/path.md)`.
- Do not use Obsidian `[[double-bracket]]` syntax. The repository must be valid Markdown without Obsidian.
- **Cross-Repository Portability**: For links to files in separate repositories (e.g., `homelab-core`, `bitetrack-api`), use their public/forge Git URLs (e.g., `https://gitea.roadtotech.me/...` or `https://github.com/...`) or semantic code blocks. **Never use machine-specific absolute file URIs (`file:///...`)**.
- When reorganizing files, run `python scripts/validate-brain.py` to catch broken links before committing.


---

## Git Commit Standards

In this repository, commit types directly reflect the Brain's semantic taxonomy rather than generic code forge types (`docs:`). Every commit must follow this format:

```
<type>(<scope>): <short description>

<optional body explaining context and rationale>
```

### Semantic Commit Types

| Type | Used For | Example |
| :--- | :--- | :--- |
| `knowledge` | Concepts, technologies, and backend methods | `knowledge(pytest): add fixture DI guide` |
| `plan` | Project roadmaps and implementation specs | `plan(homelab): define Stalwart mail server rollout` |
| `guide` | Practical SOPs, runbooks, and operation procedures | `guide(nixos): add terminal workspace walkthrough` |
| `discussion` | Architectural inquiries, evaluations, trade-offs | `discussion(homelab): evaluate LLDAP vs Stalwart auth` |
| `decision` | Architectural Decision Records (ADRs) | `decision(nixos): adopt standalone workstation model` |
| `journal` | Dated journals, post-mortems, RCA logs | `journal(homelab): record Gitea mirror DNS RCA` |
| `practice` | Algorithm writeups and LeetCode drills | `practice(leetcode): add 0075 sort colors solution` |
| `meta` | Brain governance, `AGENTS.md`, taxonomies, root docs | `meta(agents): establish inbox curation protocol` |
| `infra` | Repository tooling, validator scripts, Nix flakes | `infra(validator): add broken link check` |
| `refactor` | Structural reorganization, directory restructurings | `refactor(homelab): move archive docs to project root` |

Keep commits atomic: one logical document addition or document + linked cross-reference update per commit.

---

## Structural Validator

Run before committing structural changes:

```bash
python scripts/validate-brain.py
```

Checks: frontmatter presence, valid `type` fields, relative link resolution, no deprecated directories, required root files.

---

## AI Agent Artifact & Inbox Capture Protocol

To avoid draft fragmentation, shadow duplication, and excessive inbox maintenance:

1. **Skip Inbox Capture for Canonical Brain Documents**:
   If an agent is creating or modifying a document that already has a designated home in `knowledge/`, `projects/`, `records/`, or `practice/`, **DO NOT** write a shadow copy or duplicate draft to `inbox/`. The document in the repository tree is the canonical source of truth.

2. **One Topic, One Draft (In-Place Evolution)**:
   When generating artifacts for research, plans, or session summaries that belong in `inbox/`:
   - Search `inbox/` for an existing file covering the current topic or session (e.g., `inbox/<topic>-notes.md`).
   - If one exists, **update/overwrite that single file in-place** rather than creating new fragmented files (e.g., evolve the plan into the finalized walkthrough/summary).
   - Never create parallel variations (such as `topic-plan.md`, `topic_plan.md`, `topic-walkthrough.md`, `walkthrough.md`).

3. **Session Consolidation**:
   At the conclusion of any agentic workflow or task, ensure there is at most **one** comprehensive capture document in `inbox/` representing the session.

---

## Inbox Curation Protocol

When the user requests an inbox curation or maintenance pass (e.g., *"Curate the inbox"*, *"Process inbox"*, *"It's time to curate"*), agents must execute the following deterministic workflow:

### Step 1: Baseline Integrity Verification
Run the structural validator to verify a clean working state before making any modifications:
```bash
python scripts/validate-brain.py
```
If existing errors are found, address them or establish baseline awareness before proceeding.

### Step 2: Inbox Inventory & Draft Clustering
1. Inspect all pending files in `inbox/` (excluding `inbox/README.md` and `.gitignore`).
2. **Cluster by Topic & Session**: Identify multiple drafts or evolutionary iterations created for the same subject.
3. **Consolidation & Deduplication**:
   - Consolidate iterative drafts into **one single comprehensive document** representing the final canonical knowledge.
   - Keep multiple documents only when there is a distinct semantic separation across Brain types (e.g., an active `plan` vs. an architectural `discussion` vs. a retrospective `journal`).
   - If ambiguous whether to merge or separate, **prompt the user** before proceeding.

### Step 3: Semantic Classification & Target Resolution
Map each consolidated document to its canonical destination following the [Semantic Contracts](#semantic-contracts):
- **`knowledge/`** — Durable concepts, tools, languages, and backend engineering methods.
  - `concepts/` (algorithms, data structures, abstract theory)
  - `technologies/` (tools, libraries, languages, CLI utilities)
  - `methods/` (architecture patterns, testing, auth, SQL)
- **`projects/<project>/`** — Project-specific context. Place under `discussions/`, `plans/`, `guides/`, or update `README.md`.
- **`records/`** — Historical artifacts (`journal/`, `discussions/`, `decisions/`, `experiments/`).
- **`practice/`** — Algorithm drills and LeetCode writeups.

> [!NOTE]
> **Ambiguous Documents**: If a capture is incomplete or its target destination is ambiguous, propose the most logical target path to the user. Leave unconfirmed items in `inbox/` until clarified.

### Step 4: Frontmatter & Content Normalization
Transform the staging frontmatter into a valid schema-compliant metadata block:
1. Replace `type: inbox` with the canonical type (`knowledge`, `guide`, `plan`, `decision`, etc.).
2. Add appropriate `status` (`draft` or `stable`), `topics`, `tags`, `project`, or `date` identifiers.
3. Fix markdown parsing errors, heading levels, invalid code fences, or malformed links.
4. Ensure all internal links use standard relative Markdown paths (never `file:///` URIs).

### Step 5: Directory Placement & Cross-Reference Linking
1. Write the document to its designated canonical directory (create new directories when needed).
2. Remove the staging file(s) and any superseded drafts from `inbox/`.
3. Update relevant parent indices (e.g., project `README.md` sections) and link related existing knowledge notes (e.g., adding `related: [...]` and cross-reference links in sibling documents).

### Step 6: Atomic Git Commit
Create an isolated atomic commit for each curated document and any adjacent modified files using the [Semantic Commit Taxonomy](#git-commit-standards):
```bash
git add <target-file> [adjacent-modified-files...]
git commit -m "<type>(<scope>): <short description>"
```
*(Note: The Git pre-commit hook automatically executes `scripts/validate-brain.py` during `git commit`, ensuring schema and link integrity before each commit).*

### Step 7: Curation Summary
Present a clear summary of all curated documents, their target paths, and associated commit references to the user.


