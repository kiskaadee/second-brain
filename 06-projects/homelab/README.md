---
type: project
status: active
tags:
  - architecture
  - operations
  - security
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
| **Workstation Path** | `~/Homelab/Core` | Active local development checkout on workstation (`~/Homelab/Core` and `~/Homelab/Sites`) |
| **Production Target** | `server-remote:~/Core` | Production deployment checkout on the 24/7 server host |

---

## 💬 Open Discussions

Architectural inquiries and problem statements currently under evaluation that have **not yet produced an active implementation plan**:

* ❓ [**WhatsApp & Telegram AI Assistant Backend Architecture**](../../02-discussions/homelab/chatbot-assistant-design.md)
  - **Focus**: Evaluates architecture, webhook ingress, and trade-offs between Telegram Bot API and WhatsApp Cloud API for a personal AI assistant microservice (`~/Sites/homelab-assistant`) connected to the Brain vault.
  - **Current Status**: Open inquiry examining authorization models, message formatting, cron triggers, and RAG search capabilities before formalizing an implementation plan.

---

## 🚧 Work in Progress (Active Plans)

Implementation roadmaps currently in progress (`status: active`) that are actively being executed or scheduled for deployment:

1. 🟡 [**Architecture Consolidation & Hardening Roadmap & Execution Plan v4**](../../01-plans/homelab/architecture-consolidation-roadmap-v4.md) `[Active]`
   - Unified roadmap and execution blueprint: 3-tier architecture (Software vs. Deployment vs. Platform), OCI provenance model, two workload deployment classes, authoritative Core registry, Stalwart vs. SnappyMail zero-data-loss relocation, workload Compose security policy, unified typed manifest engine, linear control path (KISS), and two operational inspection axes with three revision identities.
   - 🏛️ *Architectural Decision Record*: [**Homelab 3-Tier Architecture & Provenance**](../../03-records/decisions/homelab-3tier-architecture-and-provenance.md)
2. 🟡 [**Rust Daemon Migration Plan: Standalone `dynu-monitor`**](../../01-plans/homelab/dynu-monitor-rust-daemon.md) `[Active]`
   - Implementing a standalone Rust daemon with 30-second polling and round-robin public DNS resolution across 5 independent providers (Cloudflare, Quad9, Google, OpenDNS, Dynu).
3. 🟡 [**Custom API Security Hardening & Threat Analysis**](../../01-plans/homelab/api-security-hardening.md) `[Active]`
   - Defense-in-depth security hardening for custom microservice APIs (Learning Hub and Minecraft dashboard) using Authelia ForwardAuth, token validation, and rate limiting.
4. 🟡 [**Smart Selective Deployment Pipeline for Homelab Core**](../../01-plans/homelab/appctl/smart-deployment-pipeline.md) `[Active]`
   - Enhancing `appctl` and Gitea Actions with change-aware selective container restarts to prevent unnecessary service interruptions during routine deployments.
5. 🟡 [**appctl Engine V2: Architectural Modernization & Type-Safe Refactoring Plan**](../../01-plans/homelab/appctl/appctl-engine-v2-refactoring.md) `[Active]`
   - Modernizing the homelab control utility into a clean, typed Python 3 engine with PyYAML parsing, explicit domain models, and a TDD test suite.
6. 🟡 [**GitHub to Gitea Automated Batch Migration Plan**](../../01-plans/homelab/gitea/github-to-gitea-migration-plan.md) `[Active]`
   - Automated migration tooling using `gh` and `tea` APIs to migrate ~35 repositories from GitHub to self-hosted Gitea with push mirrors for redundancy.
7. 🟡 [**LVM Storage Optimization & Partition Resizing Strategy**](../../01-plans/homelab/server-24-7/lvm-storage-optimization-and-resizing.md) `[Active]`
   - Storage space audit, disk cleanup runbooks, and a non-destructive LVM logical volume expansion procedure for the server's root filesystem.

---

## 🛠️ Canonical Guides & Runbooks

Operational runbooks and procedures for daily administration:

* [**Onboarding a New Application Stack**](../../04-learning/guides/homelab/onboarding-a-new-service.md) — Step-by-step procedure for deploying new Docker Compose services in `~/Sites` with `app.yaml` and Traefik routing.
* [**Jellyfin GPU Hardware Acceleration Guide**](../../04-learning/guides/homelab/jellyfin-gpu-hardware-acceleration.md) — Configuring `/dev/dri` device passthrough, host group permissions, and GPU telemetry for hardware transcoding.
* [**LLDAP & Authelia SSO Integration Runbook**](../../04-learning/guides/homelab/lldap-authelia-integration.md) — Dynamic user directory configuration, Authelia LDAP auth, and pre-commit quality gate checks.
* [**Mail Deliverability & Outbound Relay Guide**](../../04-learning/guides/homelab/mail-deliverability-rdns-relay-guide.md) — Solving residential IP/PTR blocks and Spamhaus PBL using Stalwart and Brevo SMTP relay.
* [**Homepage Dashboard Reintegration into Core**](../../04-learning/guides/homelab/homepage-core-reintegration.md) — Clean service discovery and configuration of gethomepage in Homelab Core.
* [**Managing Secrets and Authelia Users**](../../04-learning/guides/homelab/managing-secrets-and-authelia-users.md) — Guide for editing SOPS-encrypted secrets and managing user authentication credentials.
* [**Server Maintenance and System Updates Runbook**](../../04-learning/guides/homelab/server-maintenance-and-updates.md) — Standard operating procedure for NixOS updates, garbage collection, and container pruning.
* [**Appctl & Application Manifests (`app.yaml`) User Guide**](../../04-learning/guides/homelab/appctl-operations-and-manifest-guide.md) — Comprehensive reference for the `appctl` CLI tool and `app.yaml` schema.
* [**Brain GitOps & Auto-Sync Deployment Pipeline**](../../04-learning/guides/homelab/brain-gitops-deployment-pipeline.md) — Technical runbook on how Brain commits automatically validate and publish to `docs.roadtotech.me`.
* [**Dynu DDNS Domain Configuration Troubleshooting Runbook**](../../04-learning/guides/homelab/dynu-ddns-troubleshooting.md) — Diagnostic and recovery steps for WAN address synchronization issues.
* [**Diagnosing Unexpected Server Shutdowns Runbook**](../../04-learning/guides/homelab/server-unexpected-shutdown-diagnosis.md) — Diagnostic procedure and checklist for investigating hardware thermal trips, power loss, and unexpected crashes.

---

## 🏛️ Completed Roadmaps & Resolved Discussions

Archived and foundational documentation for completed milestones:

### Resolved Architectural Discussions
* [**Stalwart Mail Server Evaluation for Homelab Core**](../../02-discussions/homelab/mail-server-evaluation-stalwart.md) — Evaluated Stalwart vs Mailcow, Poste.io, and Postfix; resolved via Stalwart deployment.
* [**Hostinger Business Email vs. Self-Hosted Stalwart**](../../02-discussions/homelab/hostinger-vs-stalwart-email-evaluation.md) — Compared cloud SaaS mail vs self-hosted mail with smart host relay.
* [**Dual-Email Schema: Internal Mailboxes vs External Recovery**](../../02-discussions/homelab/dual-email-schema-lldap-stalwart.md) — Solved password recovery loops in identity directories with separate `mail` and `recovery_email` attributes.
* [**Decoupling User Management from Secrets via LLDAP**](../../02-discussions/homelab/authelia-dynamic-user-backend-lldap.md) — Migrated from static SOPS user databases to dynamic LDAP authentication.
* [**Authelia Session Lifetimes & Email Architecture**](../../02-discussions/homelab/authelia-session-email-architecture.md) — Configured 7d/3d session policies and email-based perimeter security.
* [**Homelab Repository Location & Placement Analysis**](../../02-discussions/homelab/homelab-repo-location-analysis.md) — Evaluated `~/Homelab` vs `~/Projects/homelab`; resolved via dedicated `~/Homelab` tree.
* [**Multirepo Refactor: Homepage & Learning Hub Separation**](../../02-discussions/homelab/multirepo-refactor-homepage-courses.md) — Decoupled dashboard infrastructure from domain applications.
* [**NixOS Monorepo vs. Multi-Repo Architecture**](../../02-discussions/homelab/nixos-monorepo-vs-multirepo.md) — Evaluated workstation and server decoupling; resolved via appliance migration.
* [**Decoupling `nixos-config` and `homelab-core`**](../../02-discussions/homelab/nixos-monorepo-decoupling.md) — Migration inventory and separation plan; resolved via repository split.
* [**Dynamic Decentralized GitOps Dispatcher Architecture**](../../02-discussions/homelab/gitops-dispatcher-architecture.md) — Decoupled deployment webhook design; implemented in production.
* [**Gitea Git Credential Helper and Backup Strategy**](../../02-discussions/homelab/gitea-credentials-and-backup-strategy.md) — Evaluated credential helpers and push mirroring; resolved via Git credential helper configuration.
* [**Dynu DDNS Polling Frequency and Rust Migration**](../../02-discussions/homelab/dynu-monitor-polling-and-language-tradeoffs.md) — Investigated polling intervals and language trade-offs; resolved via `dynu-monitor-rust-daemon.md` plan.
* [**Dozzle Forward-Proxy Authentication & Persistent Volume Architecture**](../../02-discussions/homelab/dozzle-auth-and-storage-architecture.md) — Evaluated Dozzle v2 login prompt vs ForwardAuth SSO; resolved via `DOZZLE_AUTH_PROVIDER=forward-proxy` and persistent `/data` volume.
* [**Core Service Qualification & Portainer Deprecation**](../../02-discussions/homelab/core-service-qualification-and-portainer-deprecation.md) — Evaluated platform service qualification criteria; resolved via complete deprecation of Portainer and retaining Gitea and CI runner decoupled.
* [**Migrating from Legacy Multirepo (v3) to 3-Tier Provenance Architecture (v4)**](../../02-discussions/homelab/architecture-migration-v3-to-v4.md) — Evaluated multirepo friction (source pollution, repo inflation, state co-location) vs 3-tier decoupling; resolved via Roadmap v4 adoption.

### Completed Plans
* 🟢 [**Architecture Consolidation & Hardening Roadmap v3**](../../01-plans/homelab/architecture-consolidation-roadmap-v3.md) (Superseded by v4; established controller authority, mail relocation plan, and manifest convergence)
* 🟢 [**Architecture Consolidation Implementation Guide v3**](../../01-plans/homelab/architecture-consolidation-implementation-guide-v3.md) (Superseded by v4)
* 🟢 [**Diun Load-Shaping, Workload Exemption & Authenticated SMTPS Delivery (2026-09-24)**](../../03-records/debug/2026-09-24-diun-workload-isolation-and-load-shaping.md) — Resolved 6 post-deployment issues: Portainer bcrypt `$` interpolation, high-concurrency DNS load mitigated via `WORKERS=6` + `JITTER=30s`, local-build exemptions decentralized to `Sites/*`, and Diun migrated to port 465 SMTPS with dedicated service account. 19 images clean, mail delivered authenticated.
* 🟢 [**Clean Deprecation of Portainer from Core**](../../01-plans/homelab/portainer-deprecation-plan.md)
* 🟢 [**Stalwart Mail Server & SnappyMail Webmail Deployment**](../../01-plans/homelab/stalwart-email-server-implementation-plan.md)
* 🟢 [**Multirepo Refactor of Homepage & Learning Hub**](../../01-plans/homelab/multirepo-refactor-homepage-courses.md)
* 🟢 [**Architecture Consolidation & Hardening Roadmap v2**](../../01-plans/homelab/architecture-consolidation-roadmap-v2.md) (Superseded by v3; P0 GitOps trust boundary & automated invariant testing completed)
* 🟢 [**Architecture Consolidation Implementation Guide v2**](../../01-plans/homelab/architecture-consolidation-implementation-guide-v2.md) (Superseded by v3)
* 🟢 [**Architecture Consolidation & Hardening Roadmap v1**](../../01-plans/homelab/architecture-consolidation-roadmap.md) (Superseded by v2)
* 🟢 [**Turn `homelab-core` into a Declarative NixOS Appliance**](../../01-plans/homelab/nixos-appliance-migration.md)
* 🟢 [**Core & Sites Cutover and Testing Plan**](../../01-plans/homelab/core-sites-cutover-testing-plan.md)
* 🟢 [**appctl Refactor & Decentralized `app.yaml` Metadata Architecture**](../../01-plans/homelab/refactor-and-metadata-sync.md)
* 🟢 [**appctl Git Synchronization & Full-Stack Lifecycle Strategy**](../../01-plans/homelab/git-sync-and-lifecycle.md)
* 🟢 [**CI/CD & Deployment Strategy**](../../01-plans/homelab/gitea/deployment-and-cicd-strategy.md)
* 🟢 [**Real-Time Brain Synchronization & Gitea Push Mirroring**](../../01-plans/homelab/brain-sync-and-gitea-mirroring.md)
* 🟢 [**NixOS Server & Laptop Migration**](../../01-plans/homelab/nixos-server-laptop-migration.md)
* 🟢 [**Domain Migration (`roadtotech.me`)**](../../01-plans/homelab/domain-migration-roadtotech.md)
* 🟢 [**Production Folder Structure Reorganization**](../../01-plans/homelab/server-24-7/folder-structure-reorganization.md)

