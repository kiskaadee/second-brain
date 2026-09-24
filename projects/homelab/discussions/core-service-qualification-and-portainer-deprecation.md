---
type: discussion
project: homelab
date: 2026-09-23
tags:
  - homelab
  - architecture
  - core
  - portainer
  - gitea
  - deprecation
---

# Core Service Qualification & Portainer Deprecation

## Problem Statement

As part of ongoing architectural reflection and preparation for homelab consolidation, two critical components required architectural classification:
1. **Portainer**: What is its role in the project architecture? It was inherited early on, broke silently across iterations (only surfaced via Dozzle logs), and sits idle. Does Portainer solve an actual problem in this ecosystem, or should it be deprecated?
2. **Gitea & Runner**: Should Gitea and its CI runner be moved from standalone applications (`Sites/gitea`) into `Core` alongside platform services, or remain decoupled?

---

## Architectural Analysis & Inquiries

### 1. What Qualifies a Service for Core Ownership?

A component does not acquire platform status merely because it is placed in the platform compose stack, nor because it sits "close to" multiple applications. 

Rather, a service qualifies for **Core** if:
* It provides foundational host lifecycle, container isolation, or network/routing primitives (NixOS, systemd, Traefik, `socket-proxy`).
* It provides identity, authentication, or secrets infrastructure (Authelia, LLDAP, SOPS).
* It provides a cross-cutting platform capability that the ecosystem inherently depends upon (Mail delivery via Stalwart, central service catalog via Homepage, log inspection via Dozzle).

Services that do not own an indispensable, cross-cutting responsibility in the system's operational model do not belong in Core.

---

### 2. Case Evaluation: Portainer

#### The Operational Reality
* Portainer was inherited during early Core consolidation. 
* Architecturally, the Docker daemon access was deliberately hardened by introducing `socket-proxy` with `POST=0`, `DELETE=0`, `BUILD=0`, `EXEC=0`.
* Portainer’s primary reason for being is **active container management and mutation via the Docker API**. With a hardened read-only proxy, Portainer cannot manage, create, restart, or alter containers without weakening the security boundary.
* The homelab's management philosophy is strictly **declarative and GitOps-driven**:
  - `appctl` orchestrates workloads and lifecycle from Git.
  - Automated webhooks trigger deployments via `gitops_dispatcher`.
  - Traefik dynamically discovers routes.
  - Dozzle provides real-time container log observation.
  - Homepage catalogs services and links.
* Any manual GUI modification done through Portainer violates repository state and breaks declarative invariants.

#### Conclusion
Portainer owns no unique operational responsibility that another tool does not already own better. Therefore, Portainer is slated for clean deprecation and complete removal across the codebase and runtime.

---

### 3. Case Evaluation: Gitea vs. The CI Runner

#### Gitea Forge
* Gitea provides source code control, webhook emission for GitOps, and package/code hosting.
* While Gitea is central to self-hosting, the homelab's GitOps dispatcher is forge-agnostic (it processes webhooks whether they originate from Gitea or GitHub).
* Moving Gitea into Core introduces bootstrap questions (recovering Core when Core depends on Gitea for its repository).
* Keeping Gitea capable of bootstrapping independently ensures high operational resilience.

#### The CI Runner (`act_runner`)
* Even if Gitea were considered developer infrastructure, **the CI runner is an entirely separate security domain**.
* The runner executes arbitrary, repository-controlled code and requires execution privileges (Docker-in-Docker or host socket mounts).
* Merging the runner into Core would violate the principle of least privilege for platform-trusted infrastructure.

#### Conclusion
Both Gitea and the Gitea Runner will remain separate from `Core` for the present, retaining their standalone workload boundaries under `Sites/gitea`.

---

## Consensus & Decisions

1. **Deprecate Portainer cleanly**:
   - Remove from `Core/docker-compose.yml` (service and volume).
   - Remove from `Core/nixos/modules/homeserver.nix` and prune `portainer.admin_password` from `Core/nixos/secrets.yaml`.
   - Remove from `Core/scripts/appctl_engine.py` and `Core/config/homepage/services.yaml`.
   - Add regression/absence invariant test in `Core/tests/security/test_security_invariants.py`.
   - Clean up documentation references across Core.
   - Purge residual Docker data volumes on the server post-deployment.
2. **Preserve Isolation for Gitea and Runner**:
   - Keep Gitea and `act_runner` decoupled in `Sites/gitea`.
   - Revisit developer infrastructure taxonomy during future architecture consolidation phases.

---

## Related Documentation & Plans

* Implementation Plan: [portainer-deprecation-plan.md](../plans/portainer-deprecation-plan.md)
* Security Invariants: `Core/tests/security/test_security_invariants.py`
