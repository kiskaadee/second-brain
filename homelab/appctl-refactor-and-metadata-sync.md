# 🚀 appctl Refactor & Decentralized `app.yaml` Metadata Architecture

## 🎯 Overview & Objectives
Transform `appctl` into a modular, metadata-driven homelab orchestrator where each application repository in `~/Sites` is fully self-describing via a standardized `app.yaml` manifest.

### Key Goals:
1. **Decentralized Application Manifests (`app.yaml`)**: Move service definitions, domain names, network requirements, environment defaults, visibility toggles, and presentation metadata into each app's repository.
2. **Seamless Service Aliasing**: Enable invoking commands using canonical names (e.g., `appctl up docs`, `appctl up jellyfin`), directory names (`appctl up homelab-jellyfin`), and custom short aliases (e.g., `appctl up dash`).
3. **Enhanced Output & Inspection**:
   - `appctl list` displays `SERVICE`, `STATUS`, `DOMAIN`, and `DIRECTORY`.
   - `appctl list --core` (or `--all` / `-a`) displays core stack services from `~/Core`.
   - `appctl info <service>` displays full metadata (description, domains, auth status, containers, environment, visibility, homepage cards).
4. **Automated Homepage Integration**: An `appctl sync` command (and automated sync hooks) will scan all `Sites/*/app.yaml` files and generate `homelab-dashboard/config/services.yaml` dynamically based on `visible: true`.

---

## 📋 Standardized `app.yaml` Schema

Each application stack in `~/Sites` maintains an `app.yaml` at its root:

```yaml
name: "jellyfin"                     # Canonical service name for appctl CLI
aliases: ["media", "movies"]         # Optional CLI shortcut aliases
domain: "jellyfin.roadtotech.me"     # Primary routed domain
description: "Media Server & Streaming Platform"
visible: true                        # Whether icon/card is displayed in dashboard
auth: true                           # Protected by Authelia ForwardAuth
networks:
  - proxy-net

# Optional stack-specific default environment variables
env:
  MEDIA_PATH: "/media"
  RATE_LIMIT_AVG: "100"

# Presentation metadata for Homepage (dashboard) compilation
homepage:
  title: "Jellyfin"                  # Card title
  group: "Media & Productivity"      # Homepage section
  icon: "jellyfin.png"               # Icon in Homepage
  container: "jellyfin"              # Container name for health/widget ping
  weight: 10                         # Sorting weight within group
```

---

## 🏗️ Architecture & Changes

### 1. Applications (`Sites/*/app.yaml`)
All 11 homelab applications will include an `app.yaml` defining their identity, domains, aliases, visibility, and Homepage presentation metadata:

- `homelab-dashboard`: `name: "dashboard"`, `aliases: ["dash"]`, `visible: false` (or self-link)
- `homelab-doc2site`: `name: "docs"`, `aliases: ["doc2site", "notes"]`, `visible: true`
- `homelab-excalidraw`: `name: "excalidraw"`, `aliases: ["draw", "sketch"]`, `visible: true`
- `homelab-mermaid`: `name: "mermaid"`, `aliases: ["diagrams"]`, `visible: true`
- `homelab-jellyfin`: `name: "jellyfin"`, `aliases: ["media"]`, `visible: true`
- `homelab-landing`: `name: "landing"`, `aliases: ["root", "portal"]`, `visible: false`
- `homelab-gitea`: `name: "gitea"`, `aliases: ["git"]`, `visible: true`
- `homelab-minecraft`: `name: "minecraft"`, `aliases: ["mc", "server"]`, `visible: true`
- `homelab-ollama`: `name: "ollama"`, `aliases: ["ai", "llm"]`, `visible: true`
- `homelab-pgsql`: `name: "pgsql"`, `aliases: ["postgres", "db-sql"]`, `visible: false`
- `homelab-mongodb`: `name: "mongodb"`, `aliases: ["mongo", "db-nosql"]`, `visible: false`

### 2. Orchestrator Engine (`Core/scripts/appctl`)
- **Dynamic Resolver**: Match user input against `app.yaml -> name`, `aliases`, or directory basename.
- **`appctl list [--core | --all | -a]`**: Clean tabular output with `SERVICE`, `STATUS`, `DOMAIN`, and `DIRECTORY`. Core services from `~/Core` inspected on `--core`.
- **`appctl info <service>`**: Formatted overview of all service metadata, container statuses, and network attachments.
- **`appctl sync`**: Scans `Sites/*/app.yaml`, filters for `visible: true`, and compiles `homelab-dashboard/config/services.yaml`.

---

## 🔄 Verification & Testing
- Validate all short and aliased names (`appctl config docs`, `appctl config dash`, etc.).
- Validate `appctl list` and `appctl list --core`.
- Validate `appctl info <service>`.
- Validate dynamic `services.yaml` generation via `appctl sync`.
