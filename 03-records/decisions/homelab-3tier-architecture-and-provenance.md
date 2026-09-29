---
type: decision
status: accepted
project: homelab
date: 2026-09-28
tags:
  - homelab
  - architecture
  - decisions
  - adr
  - provenance
  - gitops
  - kiss
---

# Architectural Decision Record: Homelab 3-Tier Architecture & Deployment Provenance Model

## 1. Context & Problem Statement

The `roadtotech.me` homelab operates as a dedicated NixOS appliance hosting self-hosted productivity services and personal backend engineering projects. In early iterations (v1 through v3):
1. **Application & Deployment Coupling**: In-house applications (e.g., `doc2site`, `bitetrack`) co-located application source trees, test suites, and Dockerfiles with host-specific Traefik routing labels, bridge network names, and host path mounts inside individual Git repositories in `~/Sites/<app>`.
2. **Repository Inflation**: Off-the-shelf applications (e.g., `jellyfin`, `stirling`) required full standalone Git repositories merely to store a 20-line `docker-compose.yml` and an `app.yaml` manifest.
3. **Ambiguous Freshness**: Local Git status checks in `~/Sites/<app>` could only report if deployment files had uncommitted local edits or diverged from their origin tracking branch; they could not determine whether running containers were built from the latest upstream application source code.
4. **Risk of Orchestrator Sprawl**: The growth of operational scripts (`appctl`, webhooks) risked adding secondary distributed systems (brokers, queues, databases) around basic container deployments.

A solid architectural boundary is required to decouple application development from deployment configuration, establish verifiable provenance, and strictly enforce the **KISS ("Keep It Simple, Stupid")** principle.

---

## 2. Decision

We formally adopt the **3-Tier Architecture, Two-Axis Provenance Model, and Linear Control Path** as the canonical architectural baseline for the homelab.

### A. Redefining KISS: Fewest Independent Concepts & Control Paths
In systems design, KISS does not mean the fewest files or single-repository shortcuts. The monolithic single-repo model pushed fundamentally orthogonal concerns together. 

True simplicity is achieved by defining a small, bounded set of **seven platform primitives** where each boundary has a single unambiguous owner:

| Primitive | Epistemic Role | Operational Responsibility |
| :--- | :--- | :--- |
| **Software Repository** | Source | Application code, unit tests, `Dockerfile`, CI workflows. Zero Homelab coupling. |
| **CI Engine (Gitea Actions)** | Build | Compiles code, runs tests, injects `org.opencontainers.image.revision`, publishes OCI images. |
| **OCI Container Image** | Artifact | Immutable intermediate build product and provenance object linking commit SHA to image digest. |
| **Sites Catalog (`~/Sites`)** | Desired Deployment | Environment-specific manifests (`app.yaml`) and Compose definitions (`docker-compose.yml`). |
| **GitOps Dispatcher** | Ingress & Admission | HMAC webhook authentication, Core registry admission control, and deployment serialization. |
| **`appctl` Engine** | Inspection & Reconciliation | Manifest parsing, two-axis inspection, and declarative deployment reconciliation (`appctl update`). |
| **Core Appliance (`~/Core`)** | Platform & Runtime | Declarative NixOS host, edge ingress (Traefik), Docker API proxy, SSO (Authelia/LLDAP), and shared capabilities (Stalwart). |

### B. 3-Tier Separation of Concerns
1. **Tier 1: Software Layer (Application Repositories)**: In-house software projects live in standalone Git repositories on Gitea/GitHub, completely decoupled from Homelab deployment configuration.
2. **Intermediate Artifacts**: The OCI container image is treated as an intermediate build product / provenance artifact carrying `org.opencontainers.image.revision`, linking source commit to container digest.
3. **Tier 2: Deployment Layer (Sites Workload Plane)**: `~/Sites/*` catalog owning environment-specific `app.yaml` manifests and `docker-compose.yml` stacks.
4. **Tier 3: Platform Layer (Homelab Core Appliance)**: NixOS host, edge primitives (Traefik, socket-proxy, Authelia, LLDAP), shared platform capabilities (Stalwart), and controllers (`appctl`, GitOps receiver).

### C. Two Workload Deployment Classes
1. **Class A: Source-Backed Workloads**: Declare a `source:` block in `app.yaml` (`type: git`, canonical `url:`, and `ref:`). Freshness inspects upstream Git refs against container image revision labels.
2. **Class B: Image-Only Workloads**: Omit `source:` entirely. Deployment freshness relies solely on container registry image tags and digests.

### D. Two Operational Inspection Axes with Three Revision Identities
To eliminate ambiguity between operational checks and concrete ledger facts:
* **Two Operational Inspection Axes**:
  1. *Deployment Configuration Axis*: Local `~/Sites/<app>` Git checkout status (`git status`, `git rev-list HEAD...@{u}`).
  2. *Software Provenance Axis*: Upstream source ref vs. deployed container image revision (`org.opencontainers.image.revision`).
* **Three Independent Revision Identities**:
  1. `deployment_config_revision`: Sites Git commit SHA.
  2. `source_revision`: Upstream application source Git commit SHA.
  3. `artifact_digest`: Immutable OCI registry SHA256 digest extracted from container `RepoDigests`.

### E. Minimal Linear Control Path (Anti-Sprawl Guardrail)
The deployment lifecycle is strictly linear:
$$\text{Source Push} \longrightarrow \text{CI Build} \longrightarrow \text{GitOps Ingress} \longrightarrow \text{appctl update} \longrightarrow \text{Compose Up}$$

The platform **strictly rejects** introducing secondary orchestration systems, message brokers (e.g. RabbitMQ/Redis), queues, deployment databases, or dynamic rollback daemons around `appctl`. `appctl update` operates purely as a local, deterministic deployment reconciliation primitive.

### F. Persistent State Root Isolation
Mutable application state (databases, upload caches, runtime media) is strictly decoupled from version-controlled directories and provisioned under `~/var/lib/homelab/<app>/`.

### G. Degraded Remote Revision Inspection
Ancestry analysis across remote repositories without local clones is explicitly downgraded to commit equality checks via `git ls-remote` (bounded by a 10-second timeout, gated behind `appctl list --fetch` or `appctl info`).

---

## 3. Options Considered & Trade-Offs

| Option | Architecture Model | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Model A: Monolithic Deployment Repos (v1–v3)** | Keep Compose and deployment config co-located in application Git repos. Single Git SHA. | Single repo per custom app. Familiar workflow. | Host config leaks into app code; cannot support off-the-shelf apps cleanly; ambiguous revision truth. | **Rejected** |
| **Model B: Miniature Cloud Platform** | Introduce message queues (RabbitMQ/Redis), Postgres deployment database, multi-environment controllers, rollback workers. | Replicates enterprise Kubernetes/ArgoCD workflows. | Extreme accidental complexity; excessive RAM/CPU footprint on single appliance; high operational maintenance. Violates KISS. | **Rejected** |
| **Model C: Bounded 3-Tier Platform (v4)** | Decoupled tiers, OCI provenance metadata, linear control path, filesystem state root, single manifest parser, two inspection axes. | Clean separation; testable domain models; clear ownership; minimal control paths; zero VPS costs; demonstrates systems design thinking. | Requires two Git repositories for custom apps (source repository + Sites catalog entry). | **Accepted** |

---

## 4. Consequences

### Positive
* **Decoupled Application Lifecycle**: Custom backend projects can be developed, tested, and shared independently of the private homelab infrastructure.
* **Precise Deployment Truth**: Operators and automation tools can independently verify whether deployment configuration, upstream source code, or container images are out of date.
* **Clean Filesystem Contracts**: Desired configuration in `~/Sites` remains purely declarative; runtime state lives exclusively under `~/var/lib/homelab/`.
* **Bounded Operational Surface**: Eliminates orchestrator sprawl by restricting reconciliation to a single deterministic primitive (`appctl update`).

### Negative / Trade-offs
* **Dual Repositories for In-House Workloads**: Updating in-house applications requires pushing to the source repository to build an artifact, followed by updating the Sites catalog when pinning explicit tags or SHAs.
* **No Ahead/Behind Counts for Remote Sources**: `git ls-remote` determines commit equality but cannot calculate commit distance without cloning the repository graph.

---

## 5. References & Successors
* **Authoritative Roadmap & Execution Plan**: [`01-plans/homelab/architecture-consolidation-roadmap-v4.md`](../../01-plans/homelab/architecture-consolidation-roadmap-v4.md)
* **Engine Modernization Plan**: [`01-plans/homelab/appctl/appctl-engine-v2-refactoring.md`](../../01-plans/homelab/appctl/appctl-engine-v2-refactoring.md)
* **Homelab Core Project Hub**: [`06-projects/homelab/README.md`](../../06-projects/homelab/README.md)
