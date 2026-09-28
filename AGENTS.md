# Brain — AI Agent Guide

This repository is a personal knowledge graph organized strictly around the **epistemic role** of information in the engineering lifecycle. It is a durable store of structured information across discrete cognitive categories.

---

## Repository Purpose

The Brain organizes information into seven numbered lifecycle directories:

| Directory | Semantic Role | Contains |
| :--- | :--- | :--- |
| `00-inbox/` | **Capture** | Unprocessed, ephemeral captures — no classification or metadata required. |
| `01-plans/` | **Intent** | Actionable implementation roadmaps, specifications, and execution blueprints (`type: plan`). |
| `02-discussions/` | **Exploration** | Prospective inquiries, architectural options evaluations, and trade-offs (`type: discussion`). |
| `03-records/` | **History** | Historical memory: journals, incident RCAs, and ADRs (`type: journal \| debug \| decision`). |
| `04-learning/` | **Understanding** | Durable knowledge (`knowledge/`), operational SOPs (`guides/`), and deliberate practice (`practice/`). |
| `05-agents/` | **Machine Context** | Canonical store of AI agent profiles (`profiles/`) and operational skills (`skills/`). |
| `06-projects/` | **System Hubs** | Project topology hubs, forge repository mappings, and cross-cutting index entrypoints (`type: project`). |

---

## Semantic Contracts

### `00-inbox/`
Local, uncommitted zero-friction capture zone. If the type or destination of a document is not immediately obvious, or while drafting/capturing raw thoughts, it belongs here. Documents in `00-inbox/` sit outside the committed knowledge graph and are completely exempt from frontmatter, type, and link validation until curated and moved.

### `01-plans/`
Actionable engineering roadmaps, milestone breakdowns, and phased technical executions answering: *"What do we intend to build or execute?"*
- *Project Locality*: Placed in `01-plans/<project>/[subsystem/]<filename>.md` (e.g. `01-plans/homelab/appctl/smart-deployment-pipeline.md`).
- *Frontmatter*: `type: plan`, `status: draft | active | completed | abandoned`, `project: <name>`.
- *Invariant*: **Lifecycle state is metadata, not folder placement.** Completed or abandoned plans remain in `01-plans/` with `status: completed` or `status: abandoned`. There is no `archive/` directory.

### `02-discussions/`
Architectural inquiries, problem statements, exploratory trade-off analyses, and evaluation of alternative paths (Model A vs. Model B) answering: *"Why and what if?"*
- *Format*: Problem Statement → Context & Analysis → Options Evaluation (Pros & Cons) → Consensus / Resolution.
- *Lifecycle*: Discussions are **permanent historical explorations**. When consensus is reached, the document is updated to `status: resolved` and explicitly links forward to the resulting plan (`01-plans/...`) or decision (`03-records/decisions/...`). It is never deleted or moved into an archive.
- *Frontmatter*: `type: discussion`, `status: open | resolved`, `project: <name>`, `date: YYYY-MM-DD`.

### `03-records/`
Historical memory and durable empirical records answering: *"What happened, when, and what was decided?"*
- **`journal/`** — Chronological personal/engineering daily logs (strictly named `YYYY-MM-DD.md`, `type: journal`).
- **`debug/`** — Empirical incident post-mortems, regressions, and root-cause analyses of broken systems (strictly dated `YYYY-MM-DD-<slug>.md`, `type: debug`).
- **`decisions/`** — Architectural Decision Records (ADRs) capturing point-in-time commitments and consequences (`type: decision`, `status: proposed | accepted | superseded`).

### `04-learning/`
Durable understanding, operational procedures, and deliberate drills answering: *"What do we understand and how do we operate it?"*
- **`knowledge/`** — Durable theoretical, technological, and methodological understanding:
  - `concepts/` — Disciplinary ideas (algorithms, data structures).
  - `technologies/` — Tool and language references (Python, Docker, Nix).
  - `methods/` — Backend engineering practices (testing, auth, SQL).
- **`guides/`** — Practical standard operating procedures (SOPs) and runbooks explaining how to **use and maintain** existing capabilities (`04-learning/guides/<project>/<slug>.md`, `type: guide`).
- **`practice/`** — Deliberate algorithm implementation drills (LeetCode writeups and Python test fixtures with isolated Nix devShell).

### `05-agents/`
Canonical store of AI agent profiles, instructions, operational boundaries, and guardrails across projects and workstations.
- **`README.md`** — Structural catalog of all configured agents and target workspaces.
- **`profiles/`** — Machine-readable agent persona specifications and safety guardrails (`05-agents/profiles/<name>.md`, `type: agent`, `kind: profile`).
- **`skills/`** — Reusable agent operational capabilities, instructions, and prompt modules (`05-agents/skills/<name>.md`, `type: agent`, `kind: skill`).

### `06-projects/`
Canonical project entrypoints and navigation hubs.
- **Structural Contract**: Every project hub is strictly located at `06-projects/<project>/README.md` (`max_depth=2`, `require_filename="README.md"`). No arbitrary documents or subfolders live in `06-projects/`.
- **Role**: A project hub is a **graph navigation and index node**, not a document container. It describes system topology, source forge repositories, and indexes active plans, open discussions, and canonical guides across the vault.

---

## Metadata Convention

Every committed Markdown document in the knowledge graph must have a YAML frontmatter block adhering to `DirectoryContract`:

### Valid Types:
`knowledge`, `project`, `plan`, `guide`, `decision`, `journal`, `discussion`, `experiment`, `practice`, `reference`, `agent`, `debug`.

### Frontmatter Templates

```yaml
# 01-plans
---
type: plan
status: draft | active | completed | abandoned
project: project-name
tags: [list, of, tags]
---

# 02-discussions
---
type: discussion
status: open | resolved
project: project-name
tags: [list, of, tags]
date: YYYY-MM-DD
---

# 03-records/journal
---
type: journal
date: YYYY-MM-DD
tags: [list, of, tags]
project: optional-project-name
---

# 03-records/debug
---
type: debug
date: YYYY-MM-DD
tags: [list, of, tags]
project: optional-project-name
---

# 03-records/decisions
---
type: decision
status: proposed | accepted | superseded
project: project-name
tags: [list, of, tags]
---

# 04-learning/knowledge
---
type: knowledge
status: draft | stable
topics: [list, of, topics]
tags: [optional, tags]
related: [optional, relative, paths]
project: optional-project-name
---

# 04-learning/guides
---
type: guide
project: project-name
tags: [list, of, tags]
---

# 04-learning/practice
---
type: practice
status: completed | active
topics: [list, of, topics]
tags: [optional, tags]
---

# 05-agents/profiles & skills
---
type: agent
status: active | draft | archived
name: agent-slug
kind: profile | skill
target_workspace: /path/to/workspace
project: optional-project-name
tags: [optional, tags]
---

# 06-projects (README.md only)
---
type: project
status: planned | active | paused | completed
tags: [list, of, tags]
---
```

---

## Link Conventions

- Use standard relative Markdown links for intra-vault files: `[text](../relative/path.md)`.
- Do not use Obsidian `[[double-bracket]]` syntax. The repository must be valid Markdown without Obsidian.
- **Cross-Repository Portability**: For links to files in separate repositories (e.g., `homelab-core`, `bitetrack-api`), use their public/forge Git URLs (e.g., `https://gitea.roadtotech.me/...` or `https://github.com/...`) or semantic code blocks. **Never use machine-specific absolute file URIs (`file:///...`)**.
- Always verify links before committing: `python scripts/validate-brain.py`.

---

## Git Commit Standards

In this repository, commit types directly reflect the Brain's semantic taxonomy rather than generic code forge types (`docs:`):

```
<type>(<scope>): <short description>

<optional body explaining context and rationale>
```

### Semantic Commit Types

| Type | Used For | Example |
| :--- | :--- | :--- |
| `plan` | Roadmaps, execution blueprints, milestones | `plan(homelab): define Stalwart mail server rollout` |
| `discussion` | Architectural inquiries, evaluations, trade-offs | `discussion(homelab): evaluate LLDAP vs Stalwart auth` |
| `journal` | Dated daily engineering journals | `journal: record daily log for 2026-09-28` |
| `debug` | Epistemic incident reports, postmortems, RCA logs | `debug(homelab): record gitops webhook signature mismatch rca` |
| `decision` | Architectural Decision Records (ADRs) | `decision(nixos): adopt standalone workstation model` |
| `knowledge` | Concepts, technologies, and backend methods | `knowledge(pytest): add fixture DI guide` |
| `guide` | Practical SOPs, runbooks, and operation procedures | `guide(nixos): add terminal workspace walkthrough` |
| `practice` | Algorithm writeups and LeetCode drills | `practice(leetcode): add 0075 sort colors solution` |
| `agent` | Agent specifications, behavioral guardrails, and role profiles | `agent(homelab): document homelab operations agent spec` |
| `project` | Project landing pages (`06-projects/*/README.md`) | `project(homelab): update active plans index` |
| `meta` | Brain governance, `AGENTS.md`, root docs | `meta(agents): establish numbered lifecycle taxonomy` |
| `infra` | Repository tooling, validator scripts, Nix flakes | `infra(validator): add DirectoryContract validation` |

---

## Structural Validator & Tests

Run before committing changes:

```bash
python scripts/validate-brain.py
python scripts/test_validator.py
```

Checks: directory-type contracts, max depth, filename requirements, frontmatter presence, link resolution, code fences, Mermaid syntax, Ruff linting, and Pyright typing.

---

## Inbox Curation Protocol

When curating the `00-inbox/` staging area:

1. **Verify Baseline**: Ensure `python scripts/validate-brain.py` passes cleanly.
2. **Classify**: Map the captured draft into its target directory based on epistemic role:
   - Implementation roadmap $\to$ `01-plans/<project>/` (`type: plan`)
   - Architectural trade-off $\to$ `02-discussions/<project>/` (`type: discussion`)
   - Incident post-mortem $\to$ `03-records/debug/` (`type: debug`)
   - Knowledge note $\to$ `04-learning/knowledge/` (`type: knowledge`)
   - Operational SOP $\to$ `04-learning/guides/<project>/` (`type: guide`)
3. **Format & Frontmatter**: Add valid YAML frontmatter matching the target directory contract.
4. **Remove Staging File**: Delete from `00-inbox/`.
5. **Atomic Commit**: Commit with semantic commit type matching the document role.
