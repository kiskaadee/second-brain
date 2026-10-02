# Agents Store & Specification Catalog

This directory serves as the durable repository of AI agent profiles, operational boundaries, behavioral contracts, and safety guardrails across all engineering projects and workstations.

---

## Purpose & Architecture

Rather than treating agent rulebooks (`AGENTS.md`) as transient, untracked local text files or allowing them to interfere with repository workflows, this directory documents each agent specification as a first-class engineering article:

1. **Context & Role**: Details the target workspace, repository ownership, problem domain, and intended agent role.
2. **Operational Scope & Guardrails**: Clarifies permission boundaries (e.g. read-only inspections, forbidden system switches, secret protection).
3. **Canonical Specification**: Preserves the complete, verbatim behavioral prompt deployed in the target environment.
4. **Cross-References**: Connects the agent profile to project overviews, incident journals, and architecture guides.

### Skill Package Architecture (Dual-Audience Separation)

Skills in `05-agents/skills/` are organized as encapsulated capability packages rather than flat, monolithic prompts:

```text
05-agents/skills/<skill-name>/
├── README.md              # Human API (Identity, Value, Invocation, Behavior, Outputs, Boundaries)
├── SKILL.md               # Agent Specification (Runtime engine, invariants, decision procedures)
└── references/            # Deep-dive modules loaded on demand (progressive disclosure)
```

- **`README.md` (Human API)**: The canonical Brain graph citizen (`type: agent`, `kind: skill`). Focuses strictly on the **capability contract**: what the skill is, why it matters, when to invoke it, expected outputs, negative boundaries, and package manifest.
- **`SKILL.md` (Operational Engine)**: The runtime prompt consumed by Antigravity (`~/.gemini/config/skills/`). Focuses strictly on **agent execution**: state machines, decision procedures, anti-skipping invariants, and behavioral anchors.
- **`references/` (Modular Contracts)**: Modular specifications loaded by the agent on demand, preventing attention dilution.

---

## Catalog of Agent Specifications

| Agent | Target Workspace | Primary Role | Status |
| :--- | :--- | :--- | :--- |
| [Homelab Operations](profiles/homelab-operations.md) | `/home/kiskaadee/Homelab` | Local-first server diagnostics, non-destructive triage, and post-incident journaling | `active` |
| [Homelab Core Platform](profiles/homelab-core.md) | `ssh://git@gitea.roadtotech.me:2223/kiskaadee/homelab-core` | Core platform foundation, NixOS server services, GitOps boundaries, Docker isolation | `active` |
| [NixOS Mobile Workstation](profiles/nixos-workstation.md) | `ssh://git@gitea.roadtotech.me:2223/kiskaadee/nixos-config` | Declarative NixOS/Home Manager laptop configuration with strict build-only safety barrier | `active` |
| [MagNetFlix Media Pipeline](profiles/magnetflix.md) | `git@github.com:kiskaadee/MagNetFlix.git` | Media acquisition backend (FastAPI, gRPC, Protobuf, SQLite3 WAL, UV workspaces) | `active` |
| [NekoWeb Manga Platform](profiles/nekoweb.md) | `git@github.com:kiskaadee/nekoweb.git` | Self-hosted manga web platform (FastAPI, UV, React/TanStack, HakuNeko Daemon) | `active` |
| [Second Brain Knowledge Graph](profiles/second-brain.md) | `ssh://git@gitea.roadtotech.me:2223/kiskaadee/second-brain` | Personal knowledge graph curation, epistemic validation, and artifact management | `active` |

## Catalog of Operational Skills

For the system-level architecture diagram, skill interaction matrix, and canonical transition workflows, see [skills/README.md](skills/README.md).

| Skill | Target Workspace | Primary Capability | Status |
| :--- | :--- | :--- | :--- |
| [Engineering Investigation](skills/engineering-investigation/README.md) | Global (`~/.gemini/config/skills/`) | Scientific investigation lifecycle, proportional checkpoints, and runtime verification | `active` |
| [Documentation Router](skills/documentation-router/README.md) | Global (`~/.gemini/config/skills/`) | Second-order knowledge evaluation, epistemic classification, anti-overlap invariants, and authoring modules | `active` |
| [Engineering Tutor](skills/engineering-tutor/README.md) | Global (`~/.gemini/config/skills/`) | Practice mode, Socratic graduated assistance, learner-as-primary-agent, and context-sensitive transfer verification | `active` |
| [Git Commit & History Hygiene](skills/git-commit/README.md) | Global (`~/.gemini/config/skills/`) | GitKeeper history construction, atomic commit slicing, 3-level CC messages, explicit authority precedence, and readiness gates | `active` |
| [Skill Builder](skills/skill-builder/README.md) | Global (`~/.gemini/config/skills/`) | Interactive skill design, proportional sizing, boundary review, and empirical refinement | `active` |

