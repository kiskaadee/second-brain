# 🧠 Brain

A personal knowledge graph organized by document lifecycle and epistemic role, not by subject.

---

## Structure

| Directory | Semantic Role | What it contains |
| :--- | :--- | :--- |
| [`00-inbox/`](00-inbox/) | **Capture** | Zero-friction, uncommitted staging zone. Write first, curate later. |
| [`01-plans/`](01-plans/) | **Intent** | Actionable implementation roadmaps, milestones, and design specs (`type: plan`). |
| [`02-discussions/`](02-discussions/) | **Exploration** | Prospective inquiries, architectural options evaluations, and trade-offs (`type: discussion`). |
| [`03-records/`](03-records/) | **History** | Historical memory: journals, incident post-mortems/RCAs, and ADRs (`type: journal \| debug \| decision`). |
| [`04-learning/`](04-learning/) | **Understanding** | Durable knowledge (`knowledge/`), operational SOPs/runbooks (`guides/`), and deliberate practice (`practice/`). |
| [`05-agents/`](05-agents/) | **Machine Context** | Canonical store of AI agent profiles (`profiles/`) and operational skills (`skills/`). |
| [`06-projects/`](06-projects/) | **System Hubs** | Project topology hubs, forge repository mappings, and cross-cutting index entrypoints (`type: project`). |

---

## 01. Plans

Actionable engineering roadmaps and execution blueprints:
- **Homelab**: Architecture consolidation, Appctl v2 engine, Stalwart email, Diun alerting, security hardening.
- **NixOS**: Workstation decoupling, secret restructuring, channel migrations.
- **Praxis**: Workout tracking software requirements and domain design baseline.
- **MagNetFlix**: Media indexing and browser extension pipeline.
- **Supervisor**: Engineering supervisory system and progress tracker.

---

## 02. Discussions

Permanent records of architectural inquiries and prospective options evaluations:
- [GitOps Dispatcher Architecture](02-discussions/homelab/gitops-dispatcher-architecture.md)
- [NixOS Monorepo vs. Multi-Repo](02-discussions/homelab/nixos-monorepo-vs-multirepo.md)
- [Stalwart vs. Hostinger Email Evaluation](02-discussions/homelab/hostinger-vs-stalwart-email-evaluation.md)
- [Assistant Chatbot Architecture](02-discussions/homelab/chatbot-assistant-design.md)
- [Brain Structural Validator Refactoring](02-discussions/brain/validate-brain-refactor-architecture.md)

---

## 03. Records

Historical memory and durable empirical records:
- **Journals (`03-records/journal/`)**: Dated daily engineering retrospectives (`YYYY-MM-DD.md`).
- **Incidents & Post-mortems (`03-records/debug/`)**: Empirical RCAs of system failures, regressions, and remediations.
- **Decisions (`03-records/decisions/`)**: Immutable Architectural Decision Records (ADRs).

---

## 04. Learning

Durable concepts, operational procedures, and deliberate practice:
- **Knowledge (`04-learning/knowledge/`)**:
  - `concepts/` — Algorithms, data structures (Binary Search, HashMaps).
  - `technologies/` — Tool and language understanding (Python, Docker, Nix, tmux).
  - `methods/` — Engineering methodologies (Testing, Auth, SQL, CI/CD, Tag extraction).
- **Guides (`04-learning/guides/`)**: Operational SOPs and standard runbooks (`appctl`, GitOps pipelines, rDNS relay, server maintenance).
- **Practice (`04-learning/practice/`)**: LeetCode writeups and Python solution suite with its own Nix flake environment.

---

## 05. Agents Store

Declarative specifications and behavioral guardrails for AI agents across workstations:
- [Homelab Operations](05-agents/profiles/homelab-operations.md)
- [Homelab Core Platform](05-agents/profiles/homelab-core.md)
- [NixOS Mobile Workstation](05-agents/profiles/nixos-workstation.md)
- [MagNetFlix Media Pipeline](05-agents/profiles/magnetflix.md)
- [NekoWeb Manga Platform](05-agents/profiles/nekoweb.md)
- [Second Brain Knowledge Graph](05-agents/profiles/second-brain.md)

---

## 06. Projects

Canonical entrypoints describing system topology, source code repositories, and cross-cutting index links:
- [Homelab Ecosystem Hub](06-projects/homelab/README.md)
- [NixOS Fleet Hub](06-projects/nixos/README.md)
- [Praxis Platform Hub](06-projects/praxis/README.md)
- [MagNetFlix Hub](06-projects/magnetflix/README.md)
- [NekoWeb Hub](06-projects/nekoweb/README.md)
- [New-Repo CLI Hub](06-projects/new-repo/README.md)
- [Supervisor Hub](06-projects/supervisor/README.md)
- [Second Brain Tooling Hub](06-projects/brain/README.md)

---

## Governance & Rules

See [AGENTS.md](AGENTS.md) for metadata conventions, directory structural contracts, link standards, and Git commit guidelines.
