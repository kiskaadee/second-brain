# 📁 Server Folder Structure & Production Hygiene

## 🎯 Objective
Establish clear, unambiguous directory boundaries across both the Server and Laptop to prevent development clutter from mixing with 24/7 production services.

---

## 🗺️ Standardized Directory Layout

### 🖥️ Production Server Layout
```text
/home/kiskaadee/
├── Config/                # NixOS declarative configuration for this host
├── Deployments/           # Or Production/ - Live Docker compose services (Git tracked)
│   ├── core/              # Ingress (Traefik, Authelia, Socket-Proxy)
│   ├── apps/              # Individual standalone services
│   └── data/              # Persistent volumes or bind-mount configs
├── Media/                 # Jellyfin media libraries, recordings, storage
└── second-brain/          # Synced knowledge base & operational docs
```

*Rule for Server*:
- **No** active development trees, compiler build caches (`target/`, `node_modules/` in home), or transient scratchpads.
- All running services run as containers or declarative systemd units.

---

### 💻 Laptop Workstation Layout
```text
/home/kiskaadee/
├── Config/                # Shared NixOS repository (laptop configuration)
├── Projects/              # Active source code repositories
├── Learn/                 # Backend residency and study coursework
├── Experiments/           # Prototypes, spike tests, scratchpads
├── second-brain/          # Personal notes & architecture plans
└── Downloads/ / Pictures/ # Standard user directories
```
