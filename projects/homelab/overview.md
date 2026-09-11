---
type: project
status: active
tags:
  - homelab
  - infrastructure
---
# 🌐 Homelab & Infrastructure Planning

This project documents the architectural roadmaps, infrastructure designs, deployment automation, and system administration workflows for the homelab ecosystem.

---

## 📑 Plans & Execution Roadmaps

### 🖥️ Server 24/7 & Infrastructure
1. 🟢 [**NixOS Server & Laptop Migration**](plans/server-24-7/nixos-server-laptop-migration.md) `[Completed]`
   - Headless conversion of the server host and laptop workstation provisioning.
   - Declarative Flake management across `hosts/server` and `hosts/laptop`.
2. 🟢 [**Domain Migration (`roadtotech.me`)**](plans/server-24-7/domain-migration-roadtotech.md) `[Completed]`
   - Cutover from legacy `arch-services.mywire.org` to apex `roadtotech.me`.
   - Wildcard SSL via Traefik ACME and Authelia cookie updates.
3. 🟢 [**Production Folder Structure Reorganization**](plans/server-24-7/folder-structure-reorganization.md) `[Completed]`
   - Established strict production boundaries: `~/Core`, `~/Sites`, `~/Brain`, and `~/Config`.
4. 🟡 [**LVM Storage Optimization & Partition Resizing Strategy**](plans/server-24-7/lvm-storage-optimization-and-resizing.md) `[Active]`
   - Storage topology analysis, desktop indexer cache reclamation, and zero-data-loss LVM resize runbook.

### 📦 Orchestration (`appctl`)
1. 🟢 [**Core & Sites Cutover and Testing Plan**](plans/appctl/core-sites-cutover-testing-plan.md) `[Completed]`
   - Zero-downtime, progressive cutover runbook from `~/Deployments` to decoupled `~/Core` and `~/Sites`.
2. 🟢 [**appctl Refactor & Decentralized `app.yaml` Metadata Architecture**](plans/appctl/refactor-and-metadata-sync.md) `[Completed]`
   - Decentralized service manifests, canonical aliasing, and Homepage `services.yaml` compilation.
3. 🟢 [**appctl Git Synchronization & Full-Stack Lifecycle Strategy**](plans/appctl/git-sync-and-lifecycle.md) `[Completed]`
   - Real-time Git tracking status (`✓ Synced`, `⬆ Ahead`, `⬇ Behind`, `* Dirty`), `--fetch`, and atomic `appctl update`.

### 🍵 Gitea & GitOps
1. 🟢 [**CI/CD & Deployment Strategy**](plans/gitea/deployment-and-cicd-strategy.md) `[Completed]`
   - Design of automated deployment pipelines, self-hosted Gitea runner, and dynamic webhook dispatching.
2. 🟢 [**Real-Time Brain Synchronization & Gitea Push Mirroring**](plans/gitea/brain-sync-and-gitea-mirroring.md) `[Completed]`
   - Pilot pipeline: zero-delay hooks, Gitea Actions CI, and instant reflection on `docs.roadtotech.me`.
3. 🟡 [**GitHub to Gitea Automated Batch Migration Plan**](plans/gitea/github-to-gitea-migration-plan.md) `[Active]`
   - Batch migration automation (~35 repos) via `gh` and `tea` API, visibility retention, and recovery runbook.

---

## 📑 Canonical Guides & Production References

1. [**Homelab Architecture: Appctl & Decentralized Repositories**](guides/homelab-appctl-architecture.md)
   - The authoritative reference for `appctl`, `app.yaml` manifests, and multi-repo orchestration.
2. [**Dynamic Decentralized GitOps Dispatcher Architecture**](guides/homelab-gitops-dispatcher-architecture.md)
   - Zero-Core-restart webhook architecture on port 9000, dynamic discovery, and deployment primitives.
3. [**Brain GitOps & Auto-Sync Deployment Pipeline**](guides/brain-gitops-deployment-pipeline.md)
   - End-to-end knowledge graph pipeline: local pre-commit gate, post-commit push, Gitea Actions CI, and live doc2site rendering.
4. [**Dynu DDNS Domain Configuration Troubleshooting Runbook**](guides/dynu-ddns-troubleshooting.md)
   - Root cause analysis and resolution for WAN IP rotations, SOPS key authorization, and `ddclient` updates.
5. [**Custom API Security Hardening & Threat Analysis**](guides/custom-api-security-and-hardening.md)
   - Attack surface review, Authelia ForwardAuth integration, rate limiting, and JWT fail-fast validation.
6. [**WhatsApp & Telegram AI Assistant Backend Architecture**](guides/chatbot-assistant-backend-architecture.md)
   - Architecture, channel trade-offs (Telegram vs WhatsApp), APScheduler cron triggers, and Brain vault RAG integration.

---

## 🏛️ Architectural Discussions & Records
* [Discussion: Gitea Git Credential Helper, Protocol Trade-Offs & Hybrid Backup Architecture](../../records/discussions/2026-09-gitea-git-helper-and-backup-strategy.md)
