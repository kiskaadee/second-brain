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

# Homelab 3-Tier Architecture & Deployment Provenance Model

## Context and Problem Statement

The `roadtotech.me` homelab operates as a dedicated NixOS appliance hosting self-hosted productivity services and personal backend engineering projects. In early iterations (v1 through v3):

1. **Application & Deployment Coupling**: In-house applications (`doc2site`, `bitetrack`) co-located application source trees with host-specific Traefik labels, Docker bridge networks, and host path mounts inside individual Git repositories in `~/Sites/<app>`.
2. **Repository Inflation**: Off-the-shelf applications (`jellyfin`, `stirling`) required entire standalone Git repositories simply to store a minimal Compose file and manifest.
3. **Ambiguous Freshness**: Local Git status checks in `~/Sites/<app>` could only report if deployment descriptors had uncommitted edits, never whether running containers matched current upstream application source code.
4. **Orchestrator Sprawl Risk**: Scaling operational scripts threatened to introduce secondary distributed infrastructure (queues, databases, brokers) around basic container deployments.

How should we structure application code, deployment configuration, and platform orchestration to maintain strict separation of concerns, verifiable provenance, and KISS operations?

## Decision Drivers

* **Clean Separation of Concerns**: In-house software projects must be developable, testable, and publishable independently of private Homelab infrastructure.
* **Workload Simplicity**: Off-the-shelf applications should not incur standalone repository overhead.
* **Verifiable Provenance**: Operators must be able to independently verify deployment configuration freshness versus upstream software code freshness.
* **KISS Primitives & Minimal Control Paths**: Operational reconciliation must remain bounded, deterministic, and linear without distributed brokers, queues, or deployment databases.
* **Filesystem State Hygiene**: Mutable runtime data must never reside inside version-controlled Git trees.

## Considered Options

* **Option 1: Monolithic / Single-Repo Deployment (Status Quo v1–v3)** — Co-locate application code, Dockerfiles, Compose files, and mutable runtime state inside a single Git repository per application.
* **Option 2: Miniature Cloud Platform** — Introduce message brokers (RabbitMQ/Redis), a Postgres deployment database, multi-environment controllers, and asynchronous rollback daemons.
* **Option 3: Bounded 3-Tier Platform with OCI Provenance Labels & Linear Control Path** — Decouple Software, Deployment, and Platform tiers; connect them via OCI image artifacts carrying source revision labels and content-addressed digests; enforce linear deployment reconciliation and isolated host state roots.

## Decision Outcome

Chosen option: **Option 3: Bounded 3-Tier Platform with OCI Provenance Labels & Linear Control Path**, because it addresses the identified coupling and provenance problems while retaining a bounded operational control path.

### Summary of Architectural Commitments

1. **3-Tier Separation of Concerns**:
   * **Software Layer (Application Repositories)**: Standalone Git repositories on Gitea/GitHub owning application code, tests, Dockerfiles, and CI workflows. Zero Homelab coupling.
   * **Intermediate Artifacts**: OCI container images produced by CI act as provenance objects; the immutable identity of the deployed artifact is its OCI digest, with source commit provenance carried via the `org.opencontainers.image.revision` label.
   * **Deployment Layer (Sites Workload Plane)**: Declarative catalog in `~/Sites/*` owning environment-specific `app.yaml` manifests and Compose definitions.
   * **Platform Layer (Homelab Core Appliance)**: NixOS appliance (`~/Core`) owning edge routing, SSO, shared capabilities, and operational controllers (`appctl`, GitOps receiver).
2. **Two Workload Deployment Classes**:
   * *Class A (Source-Backed)*: Declares explicit upstream `source:` pointer (canonical Git URL and ref); tracks upstream Git revisions against container image labels.
   * *Class B (Image-Only)*: Omits `source:`; deployment freshness relies strictly on container registry image tags and digests.
3. **Decoupled Deployment Configuration & Software Provenance**:
   * Distinguishes local deployment checkout state (`Sites/<app>`) from upstream software provenance (`source.url` vs. deployed container).
   * Mandates that deployment configuration, upstream source provenance, and container artifact identity must be independently observable (with exact schema fields defined in the implementation plan).
4. **Minimal Linear Reconciliation Path**:
   * The deployment lifecycle remains strictly linear:
     $$\text{Source Push} \longrightarrow \text{CI Build} \longrightarrow \text{GitOps Ingress} \longrightarrow \text{appctl update} \longrightarrow \text{Compose Up}$$
   * `appctl update` operates purely as a local, deterministic deployment reconciliation primitive. All secondary message queues, brokers, and deployment databases are strictly rejected.
5. **Isolated Host State Root**:
   * Mutable application runtime state (databases, caches, uploads) is decoupled from version-controlled directories and provisioned under `~/var/lib/homelab/<app>/`.

## Pros and Cons of the Options

### Option 1: Monolithic / Single-Repo Deployment

* Good, because it is familiar and requires only one Git repository per custom app.
* Bad, because host-specific configuration leaks into application source code, preventing reuse or open-sourcing.
* Bad, because off-the-shelf tools require empty "wrapper" repositories.
* Bad, because a single commit SHA conflates software revisions with deployment descriptor edits.
* Bad, because mutable state co-located in `Sites/<app>/data` risks accidental commits and creates dirty Git trees.

### Option 2: Miniature Cloud Platform

* Good, because it mirrors enterprise Kubernetes / ArgoCD continuous deployment capabilities.
* Bad, because running distributed brokers, queues, and databases on a single home appliance creates massive operational overhead and resource footprint.
* Bad, because it introduces complex failure modes and violates the KISS principle.

### Option 3: Bounded 3-Tier Platform with OCI Provenance Labels

* Good, because in-house software is completely decoupled from homelab infrastructure and can be open-sourced cleanly.
* Good, because off-the-shelf software incurs zero repository overhead.
* Good, because deployment inspection resolves both configuration status and code provenance unambiguously.
* Good, because runtime state is cleanly separated into `~/var/lib/homelab/<app>/`.
* Good, because it maintains the fewest independent concepts and control paths (KISS).
* Bad, because custom in-house applications require managing two Git repositories (source repository and Sites catalog entry).
* Bad, because verifying remote revisions without local clones is restricted to commit equality (`git ls-remote`), foregoing ahead/behind commit distance counts.

## Consequences

### Positive Consequences

* **Independent Software Lifecycle**: In-house applications (`bitetrack`, `doc2site`) can be shared, tested, or migrated without exposing homelab secrets, domain routing, or bridge networks.
* **Precise Diagnostic Truth**: Operators and automation tools can independently determine whether a deployment configuration changed, a new image was published, or upstream source code was updated.
* **Clean State Boundaries**: Git repositories in `~/Sites` contain only declarative manifests and compose files; databases and runtime media live exclusively in dedicated host state roots.
* **Operational Restraint**: Eliminates orchestrator sprawl by keeping reconciliation linear, synchronous, and local.

### Negative Consequences & Accepted Trade-offs

* **Dual Repositories for In-House Applications**: Deploying a change to an in-house app requires pushing code to CI, followed by updating or pinning the Sites catalog when tag/SHA pinning is desired.
* **Commit Equality Without Ancestry Graph**: Remote Git inspection confirms whether the running container matches the upstream ref HEAD, but cannot report commit distance without performing a full source clone.

## More Information

* **Informing Discussion & Rationale**: [`02-discussions/homelab/architecture-migration-v3-to-v4.md`](../../02-discussions/homelab/architecture-migration-v3-to-v4.md)
* **Governed Implementation Roadmap**: [`01-plans/homelab/consolidation/architecture-consolidation-roadmap-v4.md`](../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v4.md)
* **Project Hub**: [`06-projects/homelab/README.md`](../../06-projects/homelab/README.md)
