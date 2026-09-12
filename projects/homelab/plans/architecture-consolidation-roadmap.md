---
type: plan
status: active
project: homelab
tags: [homelab, architecture, gitops, security, roadmap]
---

# Architectural Discussion & Phased Implementation Plan: Homelab Core Appliance

## Executive Summary

The homelab infrastructure has evolved across several distinct design eras:
1. **Era 1 (Edge Ingress)**: Docker Compose with Traefik and Authelia.
2. **Era 2 (Multi-app Workloads)**: Decentralized apps in `~/Sites` coordinated by `appctl`.
3. **Era 3 (Dynamic GitOps)**: Webhook-driven auto-deployments via `gitops_dispatcher.py`.
4. **Era 4 (NixOS Appliance)**: Turnkey host system management encapsulated directly within `homelab-core`.

The system functions reliably, but carries architectural residue, blurred boundaries, and implicit trust assumptions. This plan formalizes the four-layer architecture, remedies the high-risk GitOps trust boundary, validates manifests through schemas, and establishes machine-enforced invariants.

---

## Part 1: Architectural Discussion & Synthesis

### 1. The Four-Tier Topology Model
The legacy documentation depicts a 2-tier system (`Control Plane -> Data Plane`). In practice, the system operates across four discrete layers:

```
                            ┌───────────────────────────┐
                            │        INTERNET           │
                            └─────────────┬─────────────┘
                                          │
                                 ┌────────▼────────┐
                                 │     Traefik     │  Layer 1:
                                 │  Edge / Ingress │  Edge Gateway
                                 └────────┬────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    │                                           │
           ┌────────▼────────┐                         ┌────────▼─────────┐
           │   Core Plane    │                         │  Workload Plane  │
           │                 │                         │                  │
 Layer 2:  │ Authelia        │               Layer 3:  │ ~/Sites/*        │
 Control   │ socket-proxy    │               Workload  │ app.yaml         │
 Services  │ Portainer       │               Apps      │ Compose stacks   │
           │ Dozzle          │                         │                  │
           │ Watchtower/Diun │                         └──────────────────┘
           └────────┬────────┘
                    │
           ┌────────▼──────────────────────────────────┐
           │           Host Control Plane              │  Layer 4:
           │ NixOS, systemd, SOPS, DDNS, appctl/GitOps │  Host Foundation
           └───────────────────────────────────────────┘
```

#### Layer Responsibilities & Strict Boundaries
| Layer | Owns | Must NOT Own |
| :--- | :--- | :--- |
| **Host Foundation (NixOS)** | OS, kernel, systemd services, firewall, secret decryption, host CLI tools | Workload-specific container logic or direct compose files |
| **Control Services (Core Compose)** | Edge proxy, identity gateway, socket isolation, telemetry | Workload deployment policy or app-specific environment variables |
| **Workload Plane (`~/Sites/*`)** | Application code, compose manifest, self-describing `app.yaml` | Host configuration, direct Docker socket, root/sudo execution |
| **Orchestration (`appctl` & GitOps)** | Deployment sequencing, health checks, dashboard metadata sync | Arbitrary shell script execution |

---

### 2. Resolution of Key Architectural Issues

#### A. GitOps Dispatcher Security & Trust Boundary (Critical)
* **Problem**: `gitops_dispatcher.py` currently executes arbitrary commands when `action["custom"]` is defined in `app.yaml`. Running as user `kiskaadee` (member of `wheel` and `docker`) means write access to any repository under `~/Sites` grants arbitrary host-level execution and container compromise.
* **Resolution**:
  1. **Abolish `custom` commands completely**. Deployment actions must be a closed, hardcoded enum: `git_pull`, `compose_config`, `compose_pull`, `compose_up`, `healthcheck`.
  2. **Webhook Authentication**: Require Gitea HMAC-SHA256 signature verification (`X-Gitea-Signature`) using a secret token stored via SOPS.
  3. **Strict Target Containment**: Validate that target paths are strictly canonicalized under `/home/kiskaadee/Sites/<allowed-repo>` with no path traversal (`..`) permitted.

#### B. Manifest Ownership & Schema Contract
* **Problem**: `app.yaml` is parsed with a lightweight, forgiving manual parser. Certain fields like `auth: false` or `networks: [proxy-net]` appear declarative, yet actual enforcement lives inside Docker Compose labels.
* **Resolution**:
  * Adopt an explicit schema (e.g. JSONSchema or Pydantic/dataclass validator) defining valid keys, types, and constraints.
  * Clearly split **metadata** (title, icon, group) from **enforced deployment policy** (branch, allowed actions).

#### C. Secrets & Deployment Projection
* **Problem**: `traefik-deployments.nix` acts as a monolithic repository of application environment variables, and `dynu.nix` holds `pdf_decrypt_password`.
* **Resolution**:
  * Formally document `traefik-deployments.nix` as the **Host Secret Projection Layer** (injecting credentials into `/run/secrets/rendered/traefik-deployments.env`).
  * Re-home miscellaneous secrets (like PDF password) into `nixos/modules/shell.nix` or a dedicated system utility block rather than the DDNS updater.

#### D. Operational State vs. Declarative Configuration
* **Problem**: `nixos-install --flake ~/Core#server` reconstructs configuration, but does not recover operational state.
* **Resolution**: Explicitly split disaster recovery documentation into **Declarative Recovery** (NixOS, Flake, Compose, manifests) and **State Recovery** (Docker volumes, Authelia SQLite DB, ACME `acme.json`, dynamic IP history).

---

## Part 2: Phased Implementation Plan

### Phase 1: GitOps Hardening & Closed Dispatcher Protocol (P0 — Urgent)
**Goal**: Neutralize the remote execution attack vector on the GitOps webhook receiver.
- [ ] Eliminate `custom` action execution in `gitops_dispatcher.py`.
- [ ] Implement closed allowlisted action dispatcher (`git_pull`, `compose_config`, `compose_pull`, `compose_up`, `healthcheck`).
- [ ] Webhook signature verification (`X-Gitea-Signature`).
- [ ] Deployment serialization lock to prevent race conditions on concurrent webhooks.

### Phase 2: Formalize `app.yaml` Schema & Validator (P1 — Core Foundation)
**Goal**: Turn `app.yaml` from an informal hint into a strict, validated API contract.
- [ ] Define rigorous schema (JSONSchema / Pydantic).
- [ ] Add pre-flight validation in both `appctl` and `gitops_dispatcher.py`.

### Phase 3: Machine-Enforced Invariant & Architecture Tests (P1 — Continuous Verification)
**Goal**: Convert written architectural invariants into automated test suites running locally and in CI.
- [ ] Automated assertions: `socket-proxy` POST=0/DELETE=0, zero direct `/var/run/docker.sock` mounts, valid firewall ports, `app.yaml` linting.
- [ ] Integrate into Gitea Actions CI workflow.

### Phase 4: Documentation Overhaul & Historical Archiving (P2 — Clarity)
**Goal**: Align repository documentation with current reality and banish legacy contradictions.
- [ ] Restructure `docs/` (`architecture/`, `operations/`, `security/`, `disaster-recovery/`, `adr/`, `archive/`).
- [ ] Move active ADRs to root `docs/adr/`.
- [ ] Correct documentation claims: Watchtower scope, firewall port inventory, wildcard TLS transparency scope.

### Phase 5: Deployment Lifecycle & Verification (P3 — Reliability)
**Goal**: Replace best-effort execution with validated, traceable deployment transactions.
- [ ] Pre-flight `docker compose config -q`.
- [ ] Post-deployment health verification.
- [ ] Append-only deployment audit log.
