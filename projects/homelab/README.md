---
type: project
status: active
tags:
  - homelab
  - infrastructure
---

# 🌐 Homelab Ecosystem & Core Infrastructure

The **Homelab** project encompasses the architecture, automation, deployment pipelines, and operational runbooks powering the 24/7 personal infrastructure ecosystem hosted at `roadtotech.me`.

The environment runs on dedicated hardware as a declarative NixOS appliance, providing self-hosted productivity tools, internal developer platforms, edge routing, and automated GitOps workflows.

---

## 🏛️ System Topology & Architecture

The homelab is organized into four decoupled architectural layers to isolate failures and maintain zero-downtime operations:

1. **Edge & Security Layer**:
   - **Traefik Reverse Proxy**: Dynamic ingress routing over HTTPS with automated Let's Encrypt wildcard TLS certificates (`*.roadtotech.me`).
   - **Authelia SSO**: ForwardAuth single sign-on with multi-factor authentication (2FA) protecting private services and dashboards.
   - **Dynu Dynamic DNS**: Automated WAN address synchronization and fallback monitoring.
2. **Core Control Plane (`~/Core`)**:
   - Central homelab services managed as a declarative NixOS appliance, including Gitea (Git forge & CI/CD runner), Nextcloud, Vaultwarden, Homepage dashboard, and deployment webhooks.
3. **Workload Plane (`~/Sites`)**:
   - Autonomous, containerized application stacks (Docker Compose) completely decoupled from Core infrastructure. Each service repository declares its own metadata, routing rules, and lifecycle via an `app.yaml` manifest.
4. **Host Foundation**:
   - Headless NixOS host system configured with encrypted secrets via SOPS-nix (`age`), strict firewall isolation, and standardized systemd timers for maintenance.

---

## 📍 Source Code & Repositories

| Target | Location / URL | Description |
| :--- | :--- | :--- |
| **Gitea Forge** | [homelab-core](https://gitea.roadtotech.me/kiskaadee/homelab-core) | Primary Git repository housing the NixOS appliance and Core services |
| **Clone (SSH)** | `ssh://git@gitea.roadtotech.me:2223/kiskaadee/homelab-core.git` | Developer clone URL using SSH port 2223 |
| **Workstation Path** | `/home/kiskaadee/Projects/active/homelab/Core` | Active local development checkout on laptop workstation |
| **Production Target** | `server-remote:~/Core` | Production deployment checkout on the 24/7 server host |

---

## 💬 Open Discussions

Architectural inquiries and problem statements currently under evaluation that have **not yet produced an active implementation plan**:

* ❓ [**WhatsApp & Telegram AI Assistant Backend Architecture**](discussions/chatbot-assistant-design.md)
  - **Focus**: Evaluates architecture, webhook ingress, and trade-offs between Telegram Bot API and WhatsApp Cloud API for a personal AI assistant microservice (`~/Sites/homelab-assistant`) connected to the Brain vault.
  - **Current Status**: Open inquiry examining authorization models, message formatting, cron triggers, and RAG search capabilities before formalizing an implementation plan.

---

## 🚧 Work in Progress (Active Plans)

Implementation roadmaps currently in progress (`status: active`) that are actively being executed or scheduled for deployment:

1. 🟡 [**Architecture Consolidation & Hardening Roadmap v2**](plans/architecture-consolidation-roadmap-v2.md) `[Active]`
   - Formalizing the three-layer architectural model, closing the GitOps trust boundary, codifying `app.yaml` v1 schema contracts, and establishing machine-enforced invariants.
   - 📋 *Execution Guide*: [**Architecture Consolidation Implementation Guide**](plans/architecture-consolidation-implementation-guide.md)
2. 🟡 [**Rust Daemon Migration Plan: Standalone `dynu-monitor`**](plans/dynu-monitor-rust-daemon.md) `[Active]`
   - Implementing a standalone Rust daemon with 30-second polling and round-robin public DNS resolution across 5 independent providers (Cloudflare, Quad9, Google, OpenDNS, Dynu).
3. 🟡 [**Custom API Security Hardening & Threat Analysis**](plans/api-security-hardening.md) `[Active]`
   - Defense-in-depth security hardening for custom microservice APIs (Learning Hub and Minecraft dashboard) using Authelia ForwardAuth, token validation, and rate limiting.
4. 🟡 [**Smart Selective Deployment Pipeline for Homelab Core**](plans/appctl/smart-deployment-pipeline.md) `[Active]`
   - Enhancing `appctl` and Gitea Actions with change-aware selective container restarts to prevent unnecessary service interruptions during routine deployments.
5. 🟡 [**GitHub to Gitea Automated Batch Migration Plan**](plans/gitea/github-to-gitea-migration-plan.md) `[Active]`
   - Automated migration tooling using `gh` and `tea` APIs to migrate ~35 repositories from GitHub to self-hosted Gitea with push mirrors for redundancy.
6. 🟡 [**LVM Storage Optimization & Partition Resizing Strategy**](plans/server-24-7/lvm-storage-optimization-and-resizing.md) `[Active]`
   - Storage space audit, disk cleanup runbooks, and a non-destructive LVM logical volume expansion procedure for the server's root filesystem.

---

## 🛠️ Canonical Guides & Runbooks

Operational runbooks and procedures for daily administration:

* [**Onboarding a New Application Stack**](guides/onboarding-a-new-service.md) — Step-by-step procedure for deploying new Docker Compose services in `~/Sites` with `app.yaml` and Traefik routing.
* [**Managing Secrets and Authelia Users**](guides/managing-secrets-and-authelia-users.md) — Guide for editing SOPS-encrypted secrets and managing user authentication credentials.
* [**Server Maintenance and System Updates Runbook**](guides/server-maintenance-and-updates.md) — Standard operating procedure for NixOS updates, garbage collection, and container pruning.
* [**Appctl & Application Manifests (`app.yaml`) User Guide**](guides/appctl-operations-and-manifest-guide.md) — Comprehensive reference for the `appctl` CLI tool and `app.yaml` schema.
* [**Brain GitOps & Auto-Sync Deployment Pipeline**](guides/brain-gitops-deployment-pipeline.md) — Technical runbook on how Brain commits automatically validate and publish to `docs.roadtotech.me`.
* [**Dynu DDNS Domain Configuration Troubleshooting Runbook**](guides/dynu-ddns-troubleshooting.md) — Diagnostic and recovery steps for WAN address synchronization issues.

---

## 🏛️ Completed Roadmaps & Resolved Discussions

Archived and foundational documentation for completed milestones:

### Resolved Architectural Discussions
* [**NixOS Monorepo vs. Multi-Repo Architecture**](discussions/nixos-monorepo-vs-multirepo.md) — Evaluated workstation and server decoupling; resolved via appliance migration.
* [**Decoupling `nixos-config` and `homelab-core`**](discussions/nixos-monorepo-decoupling.md) — Migration inventory and separation plan; resolved via repository split.
* [**Dynamic Decentralized GitOps Dispatcher Architecture**](discussions/gitops-dispatcher-architecture.md) — Decoupled deployment webhook design; implemented in production.
* [**Gitea Git Credential Helper and Backup Strategy**](discussions/gitea-credentials-and-backup-strategy.md) — Evaluated credential helpers and push mirroring; resolved via Git credential helper configuration.
* [**Dynu DDNS Polling Frequency and Rust Migration**](discussions/dynu-monitor-polling-and-language-tradeoffs.md) — Investigated polling intervals and language trade-offs; resolved via `dynu-monitor-rust-daemon.md` plan.

### Completed Plans
* 🟢 [**Architecture Consolidation & Hardening Roadmap v1**](archive/architecture-consolidation-roadmap.md) (Superseded by v2)
* 🟢 [**Turn `homelab-core` into a Declarative NixOS Appliance**](archive/nixos-appliance-migration.md)
* 🟢 [**Core & Sites Cutover and Testing Plan**](archive/core-sites-cutover-testing-plan.md)
* 🟢 [**appctl Refactor & Decentralized `app.yaml` Metadata Architecture**](archive/refactor-and-metadata-sync.md)
* 🟢 [**appctl Git Synchronization & Full-Stack Lifecycle Strategy**](archive/git-sync-and-lifecycle.md)
* 🟢 [**CI/CD & Deployment Strategy**](plans/gitea/deployment-and-cicd-strategy.md)
* 🟢 [**Real-Time Brain Synchronization & Gitea Push Mirroring**](archive/brain-sync-and-gitea-mirroring.md)
* 🟢 [**NixOS Server & Laptop Migration**](archive/nixos-server-laptop-migration.md)
* 🟢 [**Domain Migration (`roadtotech.me`)**](archive/domain-migration-roadtotech.md)
* 🟢 [**Production Folder Structure Reorganization**](plans/server-24-7/folder-structure-reorganization.md)
