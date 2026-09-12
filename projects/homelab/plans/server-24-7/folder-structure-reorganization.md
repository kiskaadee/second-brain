---
type: plan
status: completed
project: homelab
tags:
  - homelab
  - server
  - storage
  - hygiene
---

# 📁 Server Folder Structure & Production Hygiene

## 🎯 Objective
Establish clear, unambiguous directory boundaries across both the Server and Laptop to prevent development clutter from mixing with 24/7 production services.

---

## 🗺️ Realized Production Layout

> [!NOTE]
> The initial proposal for a monolithic `~/Deployments` directory was superseded by the decoupled `~/Core` and `~/Sites` architecture documented in [Homelab Architecture: Appctl & Decentralized Repositories](../../guides/appctl-operations-and-manifest-guide.md) and executed in [Core & Sites Cutover and Testing Plan](../appctl/core-sites-cutover-testing-plan.md).

### 🖥️ Production Server Layout (`/home/kiskaadee/`)
```text
/home/kiskaadee/
├── Core/                      # Hardened Ingress & Gateway (Traefik, Authelia, Socket-Proxy)
├── Sites/                     # Decentralized micro-repositories for each container stack
├── Brain/                     # Synced personal knowledge base & operational docs
├── Config/                    # NixOS declarative configuration (hosts/server)
└── Media/                     # High-capacity media storage for Jellyfin (/media)
```

*Rules for Server*:
- **No** active development trees, compiler build caches (`target/`, `node_modules/` in home root), or transient scratchpads.
- All running services run as containers orchestrated via `appctl` or declarative systemd units.

---

### 💻 Laptop Workstation Layout (`/home/kiskaadee/`)
```text
/home/kiskaadee/
├── Projects/                  # Active source code repositories
│   └── active/                # Current work trees (e.g. homelab micro-repos, new-repo, dynu-monitor)
├── Learn/                     # Backend residency and study coursework
├── Experiments/               # Prototypes, spike tests, scratchpads
├── Brain/                     # Local canonical knowledge graph vault
├── Config/                    # NixOS configuration repository (hosts/laptop)
└── Downloads/ / Pictures/     # Standard user directories
```

---

## 🔗 Related Documents
* [Homelab Architecture: Appctl & Decentralized Repositories](../../guides/appctl-operations-and-manifest-guide.md)
* [Core & Sites Cutover and Testing Plan](../appctl/core-sites-cutover-testing-plan.md)
