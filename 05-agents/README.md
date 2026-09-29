# Agents Store & Specification Catalog

This directory serves as the durable repository of AI agent profiles, operational boundaries, behavioral contracts, and safety guardrails across all engineering projects and workstations.

---

## Purpose & Architecture

Rather than treating agent rulebooks (`AGENTS.md`) as transient, untracked local text files or allowing them to interfere with repository workflows, this directory documents each agent specification as a first-class engineering article:

1. **Context & Role**: Details the target workspace, repository ownership, problem domain, and intended agent role.
2. **Operational Scope & Guardrails**: Clarifies permission boundaries (e.g. read-only inspections, forbidden system switches, secret protection).
3. **Canonical Specification**: Preserves the complete, verbatim behavioral prompt deployed in the target environment.
4. **Cross-References**: Connects the agent profile to project overviews, incident journals, and architecture guides.

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

| Skill | Target Workspace | Primary Capability | Status |
| :--- | :--- | :--- | :--- |
| [Engineering Investigation](skills/engineering-investigation.md) | Global (`~/.gemini/config/skills/`) | Scientific investigation lifecycle, 6-part interactive checkpoints, and runtime verification | `active` |
| [Documentation Router](skills/documentation-router.md) | Global (`~/.gemini/config/skills/`) | Second-order knowledge evaluation, epistemic classification, anti-overlap invariants, and authoring modules | `active` |
| [Engineering Tutor](skills/engineering-tutor.md) | Global (`~/.gemini/config/skills/`) | Practice mode, Socratic graduated assistance, learner-as-primary-agent, and transfer verification | `active` |
| [Git Commit & History Hygiene](skills/git-commit.md) | Global (`~/.gemini/config/skills/`) | GitKeeper history construction, atomic commit slicing, 3-level CC messages, and readiness gates | `active` |
