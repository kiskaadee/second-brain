---
type: guide
project: homelab
tags:
  - homelab
  - appctl
  - architecture
  - devops
  - git
---

# 📦 Homelab Architecture: Appctl & Decentralized Repositories

## 🎯 Architecture Model & Goals
1. **Decoupled Application Repositories (`~/Sites`)**: Each application lives in an isolated, independently version-controlled Git repository containing its own Docker Compose stack and self-describing `app.yaml` manifest.
2. **Hardened Control Plane (`~/Core`)**: Core reverse proxy (Traefik v3.6), authentication gateway (Authelia), container isolation (`socket-proxy`), management GUI (Portainer), and real-time logs (Dozzle).
3. **Decentralized Metadata & Orchestration (`appctl`)**: Unified CLI tool powered by Python/Bash that dynamically parses `app.yaml` manifests, manages aliases, injects environment configurations, monitors Git repository synchronization, and auto-compiles the Homepage dashboard (`services.yaml`).

---

## 🏛️ Directory Layout

```text
/home/kiskaadee/
├── Core/                      # Control Plane (Traefik, Authelia, Socket-Proxy, Portainer, Dozzle)
│   ├── docker-compose.yml
│   ├── config/
│   └── scripts/
│       ├── appctl             # Bash entrypoint wrapper
│       ├── appctl_engine.py   # Python metadata & orchestration engine
│       └── gitops_dispatcher.py # Dynamic webhook receiver engine
└── Sites/                     # Data Plane (User Applications & Stacks)
    ├── homelab-dashboard/     # Homepage portal & Learning API (app.yaml)
    ├── homelab-doc2site/      # Reactive Obsidian/Markdown viewer (app.yaml)
    ├── homelab-excalidraw/    # Collaborative whiteboard (app.yaml)
    ├── homelab-gitea/         # Git service, CI runner & code repository (app.yaml)
    ├── homelab-jellyfin/      # Media streaming platform (app.yaml)
    ├── homelab-landing/       # Apex domain portfolio portal (app.yaml)
    ├── homelab-mermaid/       # Mermaid live diagramming editor (app.yaml)
    ├── homelab-minecraft/     # PaperMC server & BlueMap (app.yaml)
    ├── homelab-mongodb/       # Mongo database & Express GUI (app.yaml)
    ├── homelab-ollama/        # Local LLM inference engine (app.yaml)
    └── homelab-pgsql/         # PostgreSQL database & Adminer (app.yaml)
```

---

## 📋 Self-Describing Manifest Standard (`app.yaml`)

Every repository under `~/Sites` defines its identity, routing, environment, and deployment parameters via `app.yaml`:

```yaml
name: "docs"                         # Canonical service name
aliases: ["doc2site", "notes"]       # CLI shortcut aliases
domain: "docs.roadtotech.me"         # Primary routed domain
description: "Reactive Obsidian Docs Viewer"
visible: true                        # Whether visible in dashboard (Homepage)
auth: false                          # Authelia ForwardAuth protection
networks:
  - proxy-net

# Stack-specific default environment variables
env:
  PROJECT_PATH: "/home/kiskaadee/Brain"

# Optional dynamic GitOps deployment configuration
deployment:
  branch: "main"
  actions:
    - git_pull
    - compose_up

# Presentation metadata for Homepage (dashboard) compilation
homepage:
  title: "Docs-Viewer"
  group: "Knowledge & Notes"
  icon: "files.png"
  container: "docs"
  weight: 10
```

---

## 🔄 Git Synchronization & Lifecycle Model

In a decentralized topology where each service is an independent Git repository, `appctl` surfaces real-time repository tracking status alongside container health:

```text
SERVICE            STATUS           GIT SYNC         DOMAIN                         DIRECTORY
-------            ------           --------         ------                         ---------
dashboard          🟢 Running (2)    ✓ Synced         dashboard.roadtotech.me        ~/Sites/homelab-dashboard
docs               🟢 Running (1)    ✓ Synced         docs.roadtotech.me             ~/Sites/homelab-doc2site
excalidraw         🟢 Running (2)    ✓ Synced         excalidraw.roadtotech.me       ~/Sites/homelab-excalidraw
gitea              🟢 Running (2)    ✓ Synced         gitea.roadtotech.me            ~/Sites/homelab-gitea
jellyfin           🟢 Running (1)    ✓ Synced         jellyfin.roadtotech.me         ~/Sites/homelab-jellyfin
...
```

### Git Sync Badge Legend:
* `✓ Synced`: Local branch is clean and fully in sync with upstream.
* `⬆ N Ahead`: Local branch has `N` unpushed commits.
* `⬇ N Behind`: Remote tracking branch has `N` new commits ready to pull.
* `⚡ N⬆ M⬇`: Local and remote branches have diverged.
* `* Dirty`: Working tree has uncommitted or modified files (e.g. `✓ Synced *`, `⬆ 1 Ahead *`).
* `⚪ Untracked`: No upstream remote tracking branch configured.

---

## ⚙️ `appctl` CLI Command Reference

### Status & Inspection:
* `appctl list` (or `appctl status`): Display formatted table of user applications with container status, Git sync status, routed domain, and path.
* `appctl list --fetch` (or `-f`): Concurrently run `git fetch` across all repositories before reporting sync status.
* `appctl list --core` (or `-c` / `--all`): Include Core infrastructure services (`~/Core`) in the output table.
* `appctl info <service>`: Detailed diagnostic inspection including Git remotes, tracking branches, Authelia status, container ports, environment defaults, and dashboard cards.

### Stack Lifecycle:
* `appctl up <service>`: Start an application stack using short names, aliases, or directory names. Injects SOPS secrets from `/run/secrets/traefik-deployments.env` and triggers Homepage re-sync.
* `appctl down <service>`: Gracefully stop and tear down an application stack.
* `appctl restart <service>`: Gracefully restart an application stack.
* `appctl pull <service>`: Pull latest container images and recreate containers (`--remove-orphans`).
* `appctl update <service>`: **Full atomic update**: validates clean working tree $\rightarrow$ `git pull --ff-only` $\rightarrow$ `docker compose pull` $\rightarrow$ `docker compose up -d --remove-orphans` $\rightarrow$ `appctl sync`.
* `appctl logs <service>`: Stream live container logs (`-f`).
* `appctl config <service>`: Validate and inspect resolved Compose configuration.
* `appctl sync`: Compile `Sites/*/app.yaml` manifests where `visible: true` directly into `homelab-dashboard/config/services.yaml`.

---

## 🔗 Related Plans & Implementation Runbooks
- [Core & Sites Cutover and Testing Plan](../plans/appctl/core-sites-cutover-testing-plan.md) — Completed zero-downtime cutover runbook from `~/Deployments` to `~/Core` and `~/Sites`.
- [appctl Refactor & Metadata Sync Plan](../plans/appctl/refactor-and-metadata-sync.md) — Architectural design for `app.yaml` manifests and Homepage auto-compilation.
- [appctl Git Synchronization & Lifecycle Plan](../plans/appctl/git-sync-and-lifecycle.md) — Design specification for Git tracking badges, `--fetch`, and `appctl update`.
