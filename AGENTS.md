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
Zero-friction capture zone. If the type or destination of a document is not immediately obvious, it belongs here. No metadata required. No naming perfection required. Documents are processed from inbox → knowledge / projects / records / plans during maintenance.

### `knowledge/`
Documents that answer: *"If I read this six months from now, will this help me understand something?"*

Sub-directories:
- `concepts/` — Disciplinary concepts and algorithms (e.g., binary search, data structures).
- `technologies/` — Tool- and language-specific knowledge (e.g., Python, Docker, tmux).
- `methods/` — Backend engineering practices and methodologies (e.g., testing, auth, SQL).

Knowledge documents do not become the canonical location for project-specific information. A knowledge document describes *what something is*; a project document describes *how this project uses it*.

### `projects/`
Each project lives in its own sub-folder (e.g., `projects/homelab/`, `projects/magnetflix/`). Projects may have their own `plans/`, `guides/`, `decisions/`, or `research/` sub-directories.

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

Every markdown document must have a YAML frontmatter block. `type` is the only universally required field. All other fields are type-specific.

```yaml
# knowledge
---
type: knowledge
status: draft | stable
topics: [list, of, topics]
related: [optional, relative, paths]
---

# project (overview files only)
---
type: project
status: planned | active | paused | completed
---

# plan
---
type: plan
status: draft | active | completed | abandoned
project: project-name
---

# guide
---
type: guide
project: project-name
---

# decision
---
type: decision
status: proposed | accepted | superseded
project: project-name
---

# journal (no status field — journals are historical by definition)
---
type: journal
date: YYYY-MM-DD
---

# practice
---
type: practice
status: completed | active
topics: [list, of, topics]
---

# inbox (no status — classification happens during processing)
---
type: inbox
created: YYYY-MM-DD
---
```

Valid `type` values: `knowledge`, `project`, `plan`, `guide`, `decision`, `journal`, `discussion`, `experiment`, `practice`, `inbox`, `reference`.

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
