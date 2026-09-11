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
Each project lives in its own sub-folder (e.g., `projects/homelab/`, `projects/magnetflix/`). The canonical entrypoint and landing page for any project must always be named `README.md` (e.g., `projects/homelab/README.md`) so that documentation renderers (such as `doc2site`) automatically compile it as the directory's index/landing page. Do not use `overview.md`.

Projects may have their own `plans/`, `guides/`, `decisions/`, or `research/` sub-directories.

The folder establishes context (ownership/locality). The document's `type` field establishes its semantic role.

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

- Use standard relative Markdown links: `[text](../relative/path.md)`
- Do not use Obsidian `[[double-bracket]]` syntax. The repository must be valid Markdown without Obsidian.
- For links to files in separate repositories (e.g., `bitetrack-api`), use their public GitHub URLs.
- When reorganizing files, run `python scripts/validate-brain.py` to catch broken links before committing.

---

## Git Commit Standards

All commits must follow Conventional Commits format:

```
<type>(<scope>): <short description>

<body explaining what changed and why>
```

Types: `feat`, `docs`, `fix`, `refactor`, `chore`
Scopes (optional): `knowledge`, `projects`, `records`, `practice`, `inbox`, `brain`

Examples:
```
docs(knowledge): add PostgreSQL indexing guide
refactor(brain): move homelab docs into projects/homelab/
feat(practice): add LeetCode 0075 sort colors writeup
```

Keep commits atomic: one logical change per commit.

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

