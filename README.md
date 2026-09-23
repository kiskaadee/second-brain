# 🧠 Brain

A personal knowledge graph organized by document type, not by subject.

---

## Structure

| Directory | What it contains |
| :--- | :--- |
| [`inbox/`](inbox/) | Zero-friction capture. Write here when you don't know where something belongs yet. |
| [`knowledge/`](knowledge/) | Durable understanding — things you know and want to keep. |
| [`projects/`](projects/) | Contextual documents that belong to a specific project. |
| [`records/`](records/) | Historical artifacts — things that happened. |
| [`practice/`](practice/) | Algorithm exercises and implementation drills. |
| [`agents/`](agents/) | Canonical agent specifications, behavioral guardrails, and role profiles. |

---

## Knowledge

```
knowledge/
├── concepts/       ← Disciplinary ideas: algorithms, data structures
├── technologies/   ← Tool and language knowledge: Python, Docker, Nix, tmux
│   └── python/
└── methods/        ← Backend practices: testing, auth, SQL, CI/CD, ADRs
```

**Key documents:**
- [Binary Search](knowledge/concepts/binary-search.md)
- [HashMap](knowledge/concepts/hashmap.md)
- [Pydantic](knowledge/technologies/python/pydantic.md)
- [Docker](knowledge/technologies/docker.md)
- [Authentication & JWT](knowledge/methods/auth.md)
- [SQL](knowledge/methods/sql.md)
- [Testing](knowledge/methods/testing.md)
- [CI/CD & GitOps](knowledge/methods/cicd-fundamentals-and-gitops.md)
- [Deterministic Tag Extraction](knowledge/methods/deterministic-tag-extraction.md)

---

## Projects

```
projects/
├── nixos/          ← Declarative multi-machine OS fleet & flake architecture
│   └── plans/      ← Migration and optimization roadmaps
├── homelab/        ← Infrastructure, Docker services, appctl, GitOps, networking
│   ├── plans/      ← Migration and strategy documents
│   └── guides/     ← Architecture and runbook documents
├── dynu-monitor/   ← Smart DDNS change detection daemon (Python/Rust)
├── new-repo/       ← Automated repository provisioning CLI
├── magnetflix/     ← Media indexing and streaming application
├── nekoweb/        ← Web showcase and static site generation
└── supervisor/     ← Personal engineering progress tracking & supervisory system
```

**Key documents:**
- [NixOS Fleet Overview](projects/nixos/README.md)
- [Homelab Overview](projects/homelab/README.md)
- [Dynu Monitor Overview](projects/homelab/plans/dynu-monitor/README.md)
- [New-Repo CLI Overview](projects/nixos/new-repo/README.md)
- [MagNetFlix Overview](projects/magnetflix/README.md)
- [Nekoweb Overview](projects/nekoweb/README.md)
- [Supervisor Overview](projects/supervisor/README.md)

---

## Records

```
records/
└── journal/        ← Dated engineering retrospectives
```

---

## Practice

```
practice/
└── LeetCode/
    ├── 00-practiced-patterns.md   ← Pattern index
    ├── 0001-two-sum.md
    └── Solutions/                 ← Python solution files
```

---

## Agents Store

```
agents/
├── homelab-operations.md   ← Homelab operational workstation & diagnostics agent
├── homelab-core.md         ← Homelab Core platform & deployment invariants agent
├── nixos-workstation.md    ← Laptop declarative NixOS/Home Manager configuration agent
├── magnetflix.md           ← MagNetFlix automated media acquisition pipeline agent
├── nekoweb.md              ← NekoWeb manga platform & full-stack agent
└── second-brain.md         ← Personal knowledge graph curation & validation agent
```

---

## Conventions

Every document has a `type` field in its YAML frontmatter. See [AGENTS.md](AGENTS.md) for the full metadata convention, directory semantics, link standards, and git commit format.

---

## Inbox

Documents that haven't been classified yet live in [`inbox/`](inbox/). See [`inbox/README.md`](inbox/README.md) for the capture rule.
