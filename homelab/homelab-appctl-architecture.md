# 📦 Homelab Architecture: Appctl & Decentralized Repositories

## 🎯 Architecture Model & Goals
1. **Decoupled Application Repositories (`~/Sites`)**: Each application lives in an isolated, independently version-controlled Git repository containing its own Docker Compose stack and self-describing `app.yaml` manifest.
2. **Hardened Control Plane (`~/Core`)**: Core reverse proxy (Traefik v3.6), authentication gateway (Authelia), container isolation (`socket-proxy`), management GUI (Portainer), and real-time logs (Dozzle).
3. **Decentralized Metadata & Orchestration (`appctl`)**: Unified CLI tool powered by Python/Bash that dynamically parses `app.yaml` manifests, manages aliases, injects environment configurations, inspects core infrastructure, and auto-compiles the Homepage dashboard (`services.yaml`).

---

## 🏛️ Directory Layout

```text
/home/kiskaadee/
├── Core/                      # Control Plane (Traefik, Authelia, Socket-Proxy, Portainer, Dozzle)
│   ├── docker-compose.yml
│   ├── config/
│   └── scripts/
│       ├── appctl             # Bash entrypoint wrapper
│       └── appctl_engine.py   # Python metadata & orchestration engine
└── Sites/                     # Data Plane (User Applications & Stacks)
    ├── homelab-dashboard/     # Homepage portal & Learning API (app.yaml)
    ├── homelab-doc2site/      # Reactive Obsidian/Markdown viewer (app.yaml)
    ├── homelab-excalidraw/    # Collaborative whiteboard (app.yaml)
    ├── homelab-gitea/         # Git service & code repository (app.yaml)
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

Every repository under `~/Sites` defines its identity and parameters via `app.yaml`:

```yaml
name: "docs"                         # Canonical service name
aliases: ["doc2site", "notes"]       # CLI shortcut aliases
domain: "docs.roadtotech.me"         # Primary routed domain
description: "Reactive Obsidian Docs Viewer"
visible: true                        # Whether visible in dashboard (Homepage)
auth: false                          # Authelia ForwardAuth protection
networks:
  - proxy-net

env:
  PROJECT_PATH: "/home/kiskaadee/Brain"

homepage:
  title: "Docs-Viewer"
  group: "Knowledge & Notes"
  icon: "files.png"
  container: "docs"
  weight: 10
```

---

## ⚙️ `appctl` CLI Commands

* `appctl list`: Formatted table showing `SERVICE`, `STATUS`, `DOMAIN`, and `DIRECTORY`.
* `appctl list --core` (or `-a` / `--all`): Includes the Core infrastructure stack from `~/Core`.
* `appctl info <service>`: Detailed inspection of runtime status, security, domains, environment defaults, and dashboard cards.
* `appctl up <service>`: Start an application stack using short names, aliases, or directory names.
* `appctl down <service>`: Gracefully stop and tear down an application stack.
* `appctl restart <service>`: Restart an application stack.
* `appctl pull <service>`: Pull latest container images and recreate the stack.
* `appctl logs <service>`: Stream live container logs.
* `appctl config <service>`: Validate and inspect resolved Compose configurations.
* `appctl sync`: Compile `Sites/*/app.yaml` manifests where `visible: true` directly into `homelab-dashboard/config/services.yaml`.
