# 🚀 appctl Refactor & Decentralized `app.yaml` Metadata Architecture

## 🎯 Overview & Objectives
Transform `appctl` into a modular, metadata-driven homelab orchestrator where each application repository in `~/Sites` is fully self-describing via a standardized `app.yaml` manifest.

### Key Goals:
1. **Decentralized Application Manifests (`app.yaml`)**: Move service definitions, domain names, network requirements, environment defaults, and presentation metadata into each app's repository.
2. **Seamless Service Aliasing**: Enable invoking commands using canonical names (e.g., `appctl up docs`, `appctl up jellyfin`), directory names (`appctl up homelab-jellyfin`), and custom short aliases (e.g., `appctl up dash`).
3. **Enhanced Output & Inspection**:
   - `appctl list` displays `SERVICE`, `STATUS`, `DOMAIN`, and `DIRECTORY`.
   - `appctl list --core` (or `--all` / `-a`) displays core stack services from `~/Core`.
   - `appctl info <service>` displays full metadata (description, domains, auth status, containers, environment, homepage cards).
4. **Automated Homepage Integration**: An `appctl sync` command (and automated sync hooks) will scan all `Sites/*/app.yaml` files and generate `homelab-dashboard/config/services.yaml` dynamically.

---

## 📋 Standardized `app.yaml` Schema

Each application stack in `~/Sites` maintains an `app.yaml` at its root:

```yaml
name: "jellyfin"                     # Canonical service name for appctl CLI
aliases: ["media", "movies"]         # Optional CLI shortcut aliases
domain: "jellyfin.roadtotech.me"     # Primary routed domain
description: "Media Server & Streaming Platform"
auth: true                           # Protected by Authelia ForwardAuth
networks:
  - proxy-net

# Optional stack-specific default environment variables
env:
  MEDIA_PATH: "/media"
  RATE_LIMIT_AVG: "100"

# Metadata for Homepage (dashboard) compilation
homepage:
  enabled: true                      # Whether to display on Homepage
  title: "Jellyfin"                  # Card title
  group: "Media & Productivity"      # Homepage section
  icon: "jellyfin.png"               # Icon in Homepage
  container: "jellyfin"              # Container name for health/widget ping
  weight: 10                         # Sorting weight within group
```

---

## 🏗️ Architecture & Changes

### 1. Applications (`Sites/*/app.yaml`)
All 11 homelab applications will include an `app.yaml` defining their identity, domains, aliases, and Homepage presentation metadata:

- `homelab-dashboard`: `name: "dashboard"`, `aliases: ["dash"]`
- `homelab-doc2site`: `name: "docs"`, `aliases: ["doc2site", "notes"]`
- `homelab-excalidraw`: `name: "excalidraw"`, `aliases: ["draw", "sketch"]`
- `homelab-mermaid`: `name: "mermaid"`, `aliases: ["diagrams"]`
- `homelab-jellyfin`: `name: "jellyfin"`, `aliases: ["media"]`
- `homelab-landing`: `name: "landing"`, `aliases: ["root", "portal"]`
- `homelab-gitea`: `name: "gitea"`, `aliases: ["git"]`
- `homelab-minecraft`: `name: "minecraft"`, `aliases: ["mc", "server"]`
- `homelab-ollama`: `name: "ollama"`, `aliases: ["ai", "llm"]`
- `homelab-pgsql`: `name: "pgsql"`, `aliases: ["postgres", "db-sql"]`
- `homelab-mongodb`: `name: "mongodb"`, `aliases: ["mongo", "db-nosql"]`

### 2. Orchestrator Engine (`Core/scripts/appctl`)
- **Dynamic Resolver**: Match user input against `app.yaml -> name`, `aliases`, or directory basename.
- **`appctl list [--core | --all | -a]`**: Clean tabular output with `SERVICE`, `STATUS`, `DOMAIN`, and `DIRECTORY`. Core services from `~/Core` inspected on `--core`.
- **`appctl info <service>`**: Formatted overview of all service metadata, container statuses, and network attachments.
- **`appctl sync`**: Compiles `Sites/*/app.yaml` into `homelab-dashboard/config/services.yaml`.

---

## 🔄 Verification & Testing
- Validate all short and aliased names (`appctl config docs`, `appctl config dash`, etc.).
- Validate `appctl list` and `appctl list --core`.
- Validate `appctl info <service>`.
- Validate dynamic `services.yaml` generation via `appctl sync`.
