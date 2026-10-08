---
type: decision
status: accepted
project: homelab
date: 2026-10-07
tags:
  - homelab
  - architecture
  - decisions
  - adr
  - appctl
  - control-plane
  - security
  - identity
  - provenance
---

# Homelab Operational Control Plane & Deployment Model Architecture

## Context and Problem Statement

The `roadtotech.me` platform historically relied on `appctl` as a local, procedural Bash CLI wrapper (`scripts/appctl`) coupled with a Python metadata engine (`scripts/appctl_engine.py`). Operational commands (`up`, `down`, `restart`, `update`, `logs`, `sync`) executed as ad-hoc subprocesses on the server host, sourcing environment files from `/run/secrets/`.

This model created several architectural tensions:

1. **Coupled Unix Authority**: Executing operational commands required SSH access to the server with Unix user credentials and sudo privileges, conflating platform operations with host administration.
2. **Interface Fragmentation**: The local CLI, the GitOps webhook dispatcher, and dashboard synchronization tools independently implemented or invoked deployment actions, risking divergent operational behavior.
3. **Secret Lifecycle Coupling**: Workload secrets were coupled to the operator's laptop via SOPS and Age keys, requiring encrypted diffs in Git history and full NixOS rebuilds for every secret rotation.
4. **Manual Workload Authoring Friction**: Adding a new application required manually creating directories under `~/Sites`, configuring Docker Compose files, and handwriting Traefik ingress labels and network bindings.
5. **Absence of Unified Auditability**: Operational commands lacked an authenticated, centralized ledger capturing operator identity, client IP, action, target revision, and execution outcome.

How should Homelab Core transition its operational architecture to provide a centralized operational control plane, robust identity boundaries, clean secret distribution, and safe deployment authoring without introducing distributed cloud complexity?

## Decision Drivers

* **Control Plane Centralization**: Exactly one authoritative implementation of every operational action (`deploy`, `restart`, `inspect`, `sync`, `validate`).
* **Identity Decoupling & Least Privilege**: Operating the homelab platform must not require host Unix administrative credentials. Host access does not confer appctl authority.
* **Declarative Git Ground Truth**: Git remains the authoritative source of truth for deployment state, maintaining provenance, rollback capability, and version history.
* **Separation of Intent from Materialization**: Differentiate candidate deployment suggestions (`DeploymentProposal`) from validated, implementation-agnostic intent (`DeploymentModel`), and both from materialized runtime descriptors (`app.yaml`, Compose files).
* **KISS Primitives & Minimal Control Paths**: Avoid distributed message brokers, microservice meshes, or deployment databases. Preserve linear, synchronous, and observable execution.
* **Secret Reference Invariant**: Deployment definitions must contain secret references, never plaintext or encrypted secret material.
* **Client / Control-Plane Boundary**: The control plane owns operational logic; user interfaces (CLI, dashboard, AI authoring) are downstream clients.

## Considered Options

* **Option 1: Status Quo with Modernized Local CLI (appctl-v2)** — Modernize `appctl_engine.py` into a type-safe Python engine while keeping it strictly a local command-line tool executed over SSH.
* **Option 2: Cloud-Native Micro-Platform (Kubernetes / Nomad / ArgoCD)** — Replace `appctl` with enterprise orchestration frameworks and distributed control loops.
* **Option 3: Homelab Operational Control Plane with Stable Deployment Model** — Evolve `appctl` into a centralized, command-oriented control plane daemon exposed via Unix socket and HTTP. Git remains the authoritative deployment ledger. Introduce a formal `DeploymentModel` validated against Core capabilities and invariants.

## Decision Outcome

Chosen option: **Option 3: Homelab Operational Control Plane with Stable Deployment Model**, because it centralizes operational authority, decouples operator identity from Unix credentials, preserves Git as declarative ground truth, and establishes a secure deployment authoring seam while preserving the lightweight, appliance-based foundation of Homelab Core.

---

### Summary of Architectural Commitments

```text
                        Human Operator / Automation
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
           Operations UI                                CLI (Local & Remote)
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     │
                             appctl Control Plane API
                       (One Logical API across Transports)
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                   Unix Socket               HTTP Listener
                  (Host Clients)            (Remote/LAN Clients)
                        │                         │
                        └────────────┬────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
    Authentication             Deployment Model              Operations
    & Authorization                  Plane                     Execution
         │                           │                           │
  Token Validation &          ┌──────┴──────┐              Docker Compose
  LLDAP Directory RBAC        │             │              Traefik Routing
                       AI Investigation   Human            Host Secrets
                              │          Approval          Reconciliation
                              ▼             │
                      DeploymentProposal    │
                              │             ▼
                              └─────▶ DeploymentModel
                                            │
                                            ▼ (Committed to Git)
                                  Deployment Repository
                                       (Git Truth)
                                            │
                                            ▼ (appctl validates & materializes)
                                  Deployment Definition
                               (Sites app.yaml + compose)
                                            │
                                            ▼
                                   Runtime Reconciliation
```

#### 1. One Logical Control-Plane API across Dual Transports
* `appctl` transitions from a collection of local shell scripts into the authoritative **operational control plane service** for Homelab Core, managed as a systemd service (`homelab-appctl.service`).
* The control plane exposes **one logical, command-oriented API** (e.g. `POST /operations/deploy`, `POST /operations/restart`, `GET /workloads`, `GET /workloads/{id}/status`, `POST /operations/sync`).
* Transport is decoupled from contract:
  * **Unix Domain Socket** (`/run/homelab/appctl.sock`): Used by local host clients (local CLI).
  * **HTTP Listener** (Localhost / LAN fronted by Traefik): Used by remote clients (remote CLI, Operations UI, GitOps dispatcher).
* Both local and remote clients invoke the exact same logical API schema.

#### 2. Identity, Authentication & Host Authority Decoupling
* **Host Access Does Not Confer Appctl Authority**: Entering the server via SSH is merely host access; it does not substitute for appctl authentication. **Every mutating appctl operation requires an explicit, authenticated user-scoped token**, regardless of transport.
* **Authentication Modes**:
  * *Interactive Web / Operations UI*: Ingress routes via Traefik and Authelia (ForwardAuth). The control plane accepts identity from trusted headers (`Remote-User`, `Remote-Groups`).
  * *Remote & Local CLI*: Authenticates via explicit user-scoped API tokens (`Authorization: Bearer <token>`) mapped to an LLDAP user profile.
  * *GitOps Dispatcher*: Authenticates via cryptographic HMAC-SHA256 signatures with the webhook shared secret.
* **Role-Based Access Control (RBAC)**: Maps LLDAP groups to permissions (`homelab-admin`, `homelab-operator`, `homelab-viewer`).
* **Telemetry & Append-Only Audit Log**: Every operation records an append-only audit entry distinguishing four orthogonal dimensions:
  * `Principal`: Human username (e.g. `fabian`) or service account (`gitops-bot`).
  * `Action` & `Target`: The requested operation and workload.
  * `Transport`: `unix_socket` vs. `http`.
  * `Network Origin`: `local`, `internal_network`, `external_network`.
  * `Client`: `local_cli`, `remote_cli`, `web_ui`, `gitops`.
  * `Timestamp`, `Duration`, and `Result`.
* Filesystem permissions on `audit.jsonl` are restricted (`0600`), daemon-only writeable, with optional cryptographic hash chaining (`prev_hash`) for tamper evidence.

#### 3. Declarative Git Truth as Authoritative Deployment State
* **Git is the Authoritative Source of Deployment State**:
  * When a human operator approves a `DeploymentModel`, that model is committed to the version-controlled deployment catalog (Git).
  * `appctl` does not bypass version control. Git maintains immutable revision history, commit provenance, peer reviews, and rollback capability (`git revert`).
  * `appctl` serves as the authoritative reconciliation engine: it validates the versioned `DeploymentModel`, compiles/materializes the concrete platform descriptors (`app.yaml` + `docker-compose.yml`), provisions isolated state roots (`~/var/lib/homelab/<app>/`), and reconciles running containers.

#### 4. Five-Stage Deployment Lifecycle (Intent vs. Implementation)
* We separate candidate investigation, validated intent, and implementation artifacts into a clean progression:
  $$\text{Repository} \xrightarrow{\text{Investigation}} \text{Application Profile} \xrightarrow{\text{Proposal}} \text{DeploymentProposal} \xrightarrow{\text{Human Selection}} \text{DeploymentModel} \xrightarrow{\text{Git Commit}} \text{Deployment Definition} \xrightarrow{\text{Reconcile}} \text{Runtime Containers}$$
  1. **Application Profile**: Factual evidence gathered from repository inspection (detected ports, dependencies, persistence needs).
  2. **`DeploymentProposal`**: Candidate architectural options generated by the authoring agent (e.g. Model A Minimal, Model B Persistent, Model C Full Stack).
  3. **`DeploymentModel`**: The operator-selected, implementation-agnostic representation of desired intent (ports, domain routing, persistent storage, dependencies, environment references). Free of Docker Compose or Traefik label boilerplate.
  4. **Deployment Definition**: Ground-truth platform descriptors (`app.yaml` + `docker-compose.yml`) materialized and enforced by `appctl`.
  5. **Runtime Reconciliation**: Deterministic container recreation and health verification.

#### 5. AI Workflow as a Disconnected Authoring Client
* The AI authoring agent is strictly an upstream client with **zero execution or mutation authority**:
  * The AI analyzes repositories and drafts `DeploymentProposal` candidates.
  * The operator edits, selects, and approves the proposal into a `DeploymentModel`.
  * **After human approval, the AI is completely out of the loop.**
  * The control plane API exposes standard endpoints (`POST /models/validate`, `POST /operations/deploy`), giving the AI zero special administrative endpoints.

#### 6. Platform Capability Model & Architectural Invariants
Authoring workflows reason against an explicit platform contract:
* **Exposed Capabilities**:
  * HTTP edge ingress routing via Traefik (automatic TLS, domain mapping).
  * Persistent storage attachments to `/home/kiskaadee/var/lib/homelab/<app>/`.
  * Dedicated bridge network attachments (`proxy-net`).
  * Deterministic healthchecks (HTTP, TCP, container).
  * Resource limits (CPU, memory).
  * Secret references resolved at runtime.
  * Provenance classes: Class A (Source-Backed) vs. Class B (Image-Only).
* **Non-Negotiable Invariants**:
  * Zero privileged containers (`privileged: false`).
  * Zero direct Docker socket mounts (`/var/run/docker.sock` restricted to `socket-proxy`).
  * Zero arbitrary host mounts (state strictly isolated to dedicated state root).
  * Zero arbitrary shell commands or custom lifecycle scripts.
  * Zero plaintext secrets in manifests or Compose files.
  * Application state isolated from Git deployment descriptors.
  * Explicit provenance tracking (`source.url`, `source.ref`, and OCI image digest).

#### 7. Secret Reference & SecretProvider Boundary
* **Architectural Invariant**: Deployment definitions contain **secret references**, never secret material.
* `appctl` defines a clean `SecretProvider` interface. At deployment reconciliation time, `appctl` resolves references through the provider and projects secrets into the workload runtime.
* **Domain Segregation**:
  * Host platform secrets remain declaratively managed via `sops-nix` in `nixos/secrets.yaml`.
  * Workload application secrets are referenced by key and resolved dynamically, eliminating Git history pollution and laptop-key coupling without turning `appctl` into an ad-hoc cryptographic vault.

#### 8. Client Decoupling & UI Boundary
* `appctl` owns the control-plane contract, not its clients.
* **Homepage**: Remains the read-only service portal and status aggregator, consuming status data from `appctl`. It does not become an interactive deployment console.
* **Operations UI**: A dedicated, lightweight web client for interactive approvals, token generation, and log viewing, deployed as a client of the `appctl` API.
* **CLI (Local & Remote)**: Command-line clients consuming the `appctl` API.

---

## Pros and Cons of the Options

### Option 1: Status Quo with Local CLI Modernization
* Good: Requires no new daemons or networking listeners.
* Bad: Perpetuates host SSH credential sharing for basic operations.
* Bad: Provides no programmatic API for web dashboards or AI workflows.
* Bad: Remote management requires interactive SSH terminal access.

### Option 2: Cloud-Native Micro-Platform
* Good: Kubernetes/ArgoCD natively provide declarative control planes, RBAC, and APIs.
* Bad: Resource overhead and operational complexity are disproportionate for a single-node homelab appliance.
* Bad: Violates the KISS principle and introduces complex distributed failure modes.

### Option 3: Homelab Operational Control Plane with Stable Deployment Model (Adopted)
* Good: Unifies all operations behind a single authoritative implementation.
* Good: Enforces directory-backed RBAC and produces a verifiable audit trail without exposing host Unix credentials.
* Good: Preserves Git as declarative ground truth for deployment state.
* Good: Introduces a clean authoring boundary (`DeploymentProposal` $\to$ `DeploymentModel`) that makes AI-assisted deployments safe and reviewable.
* Good: Decouples secret management from Git history pollution.
* Bad: Requires running and monitoring an additional Core systemd daemon (`homelab-appctl.service`).
* Bad: Requires managing API tokens for remote and local CLI clients.

---

## Consequences

### Positive Consequences
* **Principle of Least Privilege**: Routine operations (deploying apps, viewing logs, restarting services) no longer require host root/sudo SSH access.
* **Single Operational Truth**: Local CLI, remote CLI, GitOps, and web clients invoke identical control-plane logic.
* **Declarative Reproducibility**: Deployments remain 100% reproducible and auditable through version-controlled Git history.
* **Safe AI Authoring**: AI agents can inspect repositories and generate rich proposals, but can never directly mutate the host.
* **Clean Auditability**: Every operational state change is attributable to a specific identity and recorded with transport and origin telemetry.

### Negative Consequences & Accepted Trade-offs
* **Daemon Availability Dependency**: Operations depend on the health of the `homelab-appctl` service. (Emergency fallback: direct Docker Compose commands remain available to host administrators via SSH).
* **Explicit Token Discipline**: Host execution over SSH requires an explicit token rather than inheriting shell user privileges.

---

## More Information

* **Companion Architecture Decision**: [`homelab-3tier-architecture-and-provenance.md`](homelab-3tier-architecture-and-provenance.md)
* **Governed Implementation Roadmap**: [`01-plans/homelab/consolidation/architecture-consolidation-roadmap-v5.md`](../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v5.md)
* **Project Hub**: [`06-projects/homelab/README.md`](../../06-projects/homelab/README.md)
