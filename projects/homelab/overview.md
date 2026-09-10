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

## 📑 Plans & Roadmap

### 🖥️ Server 24/7 & Infrastructure
1. [**NixOS Server & Laptop Migration**](plans/server-24-7/nixos-server-laptop-migration.md)
   - Converting the desktop into a 24/7 headless production server.
   - Setting up the laptop as the primary graphical development workstation.
   - Decoupling visual configurations (Niri, Hyprland, Waybar, GUI apps) from the server.
2. [**Domain Migration (`roadtotech.me`)**](plans/server-24-7/domain-migration-roadtotech.md)
   - Step-by-step strategy for cutting over from `arch-services.mywire.org` to `roadtotech.me`.
   - DNS delegation options (Dynu vs. Cloudflare), Traefik ACME wildcard SSL, and Authelia session cookie updates.
3. [**Production Folder Structure Reorganization**](plans/server-24-7/folder-structure-reorganization.md)
   - Establishing strict directory boundaries (`~/Core`, `~/Sites`, `~/Projects`).
   - Removing development traces and non-production scratchpads from the server.
4. [**LVM Storage Optimization & Partition Resizing Strategy**](plans/server-24-7/lvm-storage-optimization-and-resizing.md)
   - Storage topology analysis, desktop indexer cache reclamation, and zero-data-loss LVM resize runbook.

### 📦 Orchestration (`appctl`)
1. [**Core & Sites Cutover and Testing Plan**](plans/appctl/core-sites-cutover-testing-plan.md)
   - Zero-downtime, progressive testing and safe cutover guide from `~/Deployments` to `~/Core` and `~/Sites`.
   - Complete pre-flight verification matrix, rollback commands, and post-validation cleanup.
2. [**appctl Refactor & Decentralized `app.yaml` Metadata Architecture**](plans/appctl/refactor-and-metadata-sync.md)
   - Decentralizing service configurations into individual app repositories.
   - Clean service aliases, enhanced status listing, and dynamic Homepage `services.yaml` generation.
3. [**appctl Git Synchronization & Full-Stack Lifecycle Strategy**](plans/appctl/git-sync-and-lifecycle.md)
   - Real-time Git sync status in `appctl list` (`✓ Synced`, `⬆ Ahead`, `⬇ Behind`, `* Dirty`).
   - Network fetch support (`--fetch`) and atomic stack upgrade workflow (`appctl update`).

### 🍵 Gitea & GitOps
1. [**CI/CD & Deployment Strategy**](plans/gitea/deployment-and-cicd-strategy.md)
   - Automating image builds, GitOps updates, Gitea Actions/GitHub Actions, and production rollouts.
2. [**Real-Time Brain Synchronization & Gitea Push Mirroring**](plans/gitea/brain-sync-and-gitea-mirroring.md)
   - Zero-overhead markdown synchronization architecture between laptop and server using Gitea push mirroring.
   - Systemd timer reconciliation, instant `doc2site` reflection, and GitHub offsite backup.
3. [**Discussion: Gitea Git Credential Helper & Hybrid Backup Architecture**](plans/gitea/gitea-git-helper-and-backup-strategy.md)
   - Trade-offs between `tea`, `gh`, SSH transport, and Gitea-to-GitHub push mirroring.

---

## 📑 Guides & Incident Runbooks

1. [**Homelab Infrastructure & Appctl Architecture**](guides/homelab-appctl-architecture.md)
   - Making `appctl` a first-class homelab orchestrator.
   - Decoupling monolithic deployments into individual standalone Git repositories.
2. [**Dynu DDNS Domain Configuration Troubleshooting Runbook**](guides/dynu-ddns-troubleshooting.md)
   - Root cause analysis and step-by-step resolution for WAN IP rotations, SOPS key authorization, and `ddclient` domain updates.
3. [**Custom API Security Hardening & Threat Analysis**](guides/custom-api-security-and-hardening.md)
   - Attack surface review and actionable hardening roadmap for custom endpoints (`learning-hub`, `minecraft-web-admin`).
   - Authelia ForwardAuth integration, rate limiting, and JWT fail-fast validation.
4. [**WhatsApp & Telegram AI Assistant Backend Architecture**](guides/chatbot-assistant-backend-architecture.md)
   - Architecture, channel trade-offs (Telegram vs WhatsApp), APScheduler cron triggers, and Brain vault RAG integration.
5. [**Dynamic Decentralized GitOps Dispatcher Architecture**](guides/homelab-gitops-dispatcher-architecture.md)
   - Zero-Core-restart webhook architecture, dynamic `app.yaml` discovery, and self-describing deployment primitives.
6. [**Brain GitOps & Auto-Sync Deployment Pipeline**](guides/brain-gitops-deployment-pipeline.md)
   - Zero-delay knowledge graph synchronization, 9-phase pre-commit validation, Gitea Actions CI, and live `doc2site` reflection.

