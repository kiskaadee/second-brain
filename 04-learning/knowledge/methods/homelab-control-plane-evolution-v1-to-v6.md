---
type: knowledge
status: stable
topics:
  - homelab
  - architecture
  - control-plane
  - gitops
  - systems-evolution
tags:
  - homelab
  - architecture
  - appctl
  - evolution
  - systems-engineering
project: homelab
related:
  - ../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v6.md
  - ../../../03-records/decisions/homelab-appctl-control-plane-architecture.md
  - ../../../03-records/decisions/homelab-3tier-architecture-and-provenance.md
  - ../../../02-discussions/homelab/control-plane-and-engine-modernization.md
---

# The Architectural Evolution of the Homelab Control Plane: From Ad-Hoc Scripts to a Unified Fail-Closed Daemon (v1 to v6)

Building a self-hosted platform usually begins with a familiar set of developer conveniences: a handful of Docker Compose files, reverse-proxy routing via Traefik, an identity provider like Authelia, and bash shell scripts to stitch container lifecycles together. 

For a single server running a few hobby services, ad-hoc automation feels sufficient. However, as workloads multiply, GitOps webhooks enter the loop, multi-tenant networking hardens, and AI coding agents execute inside developer sessions, shell-based shortcuts quickly collapse under the weight of implicit trust, escaping environment variables, unvalidated states, and uncoordinated mutations.

Over the course of six distinct architectural iterations (v1 through v6), the **Homelab Core** platform (`roadtotech.me`) evolved from a collection of imperative bash scripts into a formal, declarative, fail-closed **Operational Control Plane**. 

This article chronicles that evolutionary journey—documenting the architectural friction, hard decisions, mental model shifts, and design invariants established across each phase.

---

## 🗺️ Evolutionary Timeline: The Six Eras at a Glance

| Version | Architectural Paradigm | Primary Catalyst | Key Breakthrough / Invariant |
| :--- | :--- | :--- | :--- |
| **v1** | **Ad-Hoc Imperative Automation** | Initial deployment consolidation | Traefik edge ingress + Authelia SSO; bash CLI (`scripts/appctl`) wrapping `docker compose`. |
| **v2** | **Structural Discipline & Invariant Testing** | Reviewer scrutiny & trust boundary leaks | Separation of Roadmap from Implementation Guide; automated invariant testing (`./scripts/test`). |
| **v3** | **Mail Realignment & State Isolation** | SnappyMail zero-data-loss cutover | Decoupling state from code: persistent application data strictly resides under `~/var/lib/homelab/`. |
| **v4** | **3-Tier Architecture & Dual-Axis Truth** | Multirepo friction & drift ambiguity | Decoupling Software vs. Deployment vs. Platform; two-axis inspection (`✓ Synced` local vs. upstream `ls-remote`). |
| **v5** | **The Control Plane Daemon Vision** | Shell execution limits & AI agent risks | Transitioning `appctl` from a script to a daemon (`homelab-appctl.service`); 5-stage `DeploymentModel` lifecycle. |
| **v6** | **Operational Truth & Fail-Closed Reality** | Pre-P4 implementation audit (`DEC-01–05`) | Single typed `POST /v1/operations`; token-gated auth over UDS & HTTP; OS user isolation; fail-closed audit guard. |

---

## Act I: The Ad-Hoc Era (v1) — The "Make It Run" Baseline

### The Starting Point
The homelab infrastructure originated with three distinct functional layers:
1. **Edge Ingress**: Traefik handling automated Let's Encrypt wildcard TLS (`*.roadtotech.me`) alongside Authelia for ForwardAuth single sign-on.
2. **Platform Appliance (`~/Core`)**: Core services (Gitea forge, CI runner, Vaultwarden, Nextcloud, Homepage).
3. **Decentralized Workloads (`~/Sites`)**: Standalone user applications (media servers, invite apps, custom APIs) each managed via their own compose files.

To simplify orchestration, a bash utility named `appctl` was written. Operators could SSH into the server and type:
```bash
appctl up jellyfin
appctl restart authelia
appctl sync
```

### The Architectural Friction
While `v1` successfully unified service execution, it suffered from foundational security and architectural vulnerabilities:
- **Implicit SSH Trust**: Anyone with SSH access could invoke `appctl` and mutate running workloads with zero identity validation or telemetry.
- **Shell Sourcing Hazards**: Workload environment variables were injected using shell `source "$APP_DIR/.env"`. Any syntax error broke the CLI, and any unescaped command substitution (`$(...)`) executed arbitrary code with the operator's privileges.
- **Split Authority**: Portainer ran alongside CLI scripts, allowing containers to be modified out-of-band without version control or Git tracking.
- **Entangled State**: Stateful service data, configuration templates, and Git repositories were co-located under `Core/config/` and `Sites/`, making clean backups and rollbacks perilous.

---

## Act II: The First Hardening (v2) — Structural Discipline & Invariant Testing

### The Catalyst
As homelab infrastructure became the backbone for personal production workflows, arbitrary shell scripts were deemed unacceptable. A formal architectural review exposed significant trust boundary leaks: webhook payloads from Git repositories could trigger host shell executions without sufficient containment.

### The Evolution
Roadmap `v2` transformed the consolidation effort from an ad-hoc cleanup into an engineering discipline:
1. **Separation of Intent from Runbook**: The architecture split into a strategic roadmap ([`architecture-consolidation-roadmap-v2.md`](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v2.md)) and an executable tactical runbook ([`architecture-consolidation-implementation-guide-v2.md`](../../../01-plans/homelab/consolidation/architecture-consolidation-implementation-guide-v2.md)).
2. **Automated Invariant Testing**: Introduced `./scripts/test`, requiring every change to pass a suite of Pytest unit and security tests before merging.
3. **Privilege Boundary Enforcement**: Webhook listeners were restricted from running raw shell strings; arguments were tokenized and passed via fixed parameter lists.

---

## Act III: Topology Realignment (v3) — Decoupling State from Code

### The Catalyst: The SnappyMail Migration Challenge
In milestone P1, platform mail routing needed separation from webmail: Stalwart mail server was re-homed to `smtp.roadtotech.me`, while SnappyMail was evicted from the Core stack and migrated to a standalone application workload under `~/Sites/snappymail`. 

The requirement was absolute: **zero data loss**. Address books, user configurations, and preferences could not be dropped.

### The Breakthrough: The Clean State Root Invariant
During the migration, the team confronted a major antipattern: application databases and persistent user storage were living directly inside Git working trees (`Core/config/snappymail/data`). Committing state into Git bloated history, while ignoring it with `.gitignore` created fragile directories that could be wiped out during branch switches or cleanups.

Roadmap `v3` codified the **Clean State Root Invariant**:
> *Persistent, mutable application runtime data must reside strictly under `~/var/lib/homelab/<app>/`, entirely decoupled and isolated from version-controlled Git repositories.*

By snapshotting state, verifying byte-for-byte parity (`diff -r`), and mounting the isolated host directory into the container, SnappyMail migrated with zero data loss.

---

## Act IV: The 3-Tier Architecture & Dual-Axis Truth (v4)

### The Problem: Multirepo Friction & Ambiguous Drift
By iteration `v4`, application development was plagued by repository confusion:
- Should an application's source code live in the same repository as its Docker Compose file?
- When `appctl list` reported an application as "out of sync," did that mean the local deployment directory had uncommitted edits, or that upstream software had a new Git commit?

### The Solutions: ADR-0001 & Two-Axis Inspection
1. **The 3-Tier Architecture**:
   Decoupled the platform into three strictly bounded layers:
   - **Tier 1 (Software Tier)**: Upstream application source code (`~/Projects/*`), producing versioned OCI container images or release tags.
   - **Tier 2 (Deployment Tier)**: Declarative deployment manifests and Compose configurations (`~/Sites/*`), tracking *how* software is wired.
   - **Tier 3 (Platform Tier)**: Host appliance configuration, OS kernel, and control plane (`~/Core`), managing reverse proxy routing and host security.
2. **Dual-Axis Deployment Truth**:
   Engine inspection was split into two independent axes:
   - **Axis 1 (Local Deployment Checkout)**: Evaluates working-tree cleanliness (`✓ Synced`, `* Dirty`, `⬆ Ahead`, `⬇ Behind`).
   - **Axis 2 (Upstream Software Provenance)**: Queries upstream remote repositories via bounded `git ls-remote` (with a 10s timeout) to determine if newer commits or release tags exist.
3. **Document Consolidation**:
   Recognizing that maintaining separate "Roadmap" and "Implementation Guide" documents caused synchronization drift, Roadmap `v4` unified both into a single authoritative blueprint.

---

## Act V: The Control Plane Paradigm Shift (v5) — From Scripts to Daemon

### The Catalyst: The Threat Model of AI Agents and Shell Execution
In mid-2026, AI coding agents became standard tools within the developer's workstation and SSH sessions. This introduced a critical new security boundary:
- If an AI coding agent running in an operator SSH session has shell access, and `appctl` relies on local host permissions, a rogue command or misinterpreted prompt could reconfigure reverse proxy routing or delete persistent state volumes.
- Host shell scripts lack centralized authorization, request validation, structured audit trails, and concurrency locks.

### The Architecture: Roadmap v5
Roadmap `v5` fundamentally reimagined `appctl`:
- It ceased to be a bash script.
- It was defined as a standalone Systemd daemon (`homelab-appctl.service`) exposing **One Logical API** across dual transports: a Unix Domain Socket (`/run/homelab/appctl.sock`) and an HTTP listener.
- It established the **5-Stage DeploymentModel Lifecycle**:
  $$\text{Repository} \xrightarrow{\text{Inspection}} \text{Application Profile} \xrightarrow{\text{Proposal}} \text{DeploymentProposal} \xrightarrow{\text{Human Selection}} \text{DeploymentModel (Git)} \xrightarrow{\text{appctl Materialize}} \text{Containers}$$
- **AI Authoring Boundary**: The AI was restricted to acting strictly as a proposal generator. Zero execution authority was granted to automated agents; every mutating deployment model required explicit human operator approval.

---

## Act VI: Operational Truth & Fail-Closed Hardening (v6)

### The Pre-Implementation Reality Check
Before writing a single line of daemon code for Milestone P4, the architecture underwent an exhaustive, evidence-based exploratory audit (`2026-10-16`). 

Comparing the high-level vision in Roadmap `v5` against the production codebase revealed several critical architectural gaps:
- *Endpoint Proliferation*: Designing separate REST endpoints (`GET /workloads`, `POST /operations/deploy`, `POST /operations/restart`) introduced URL-vs-body routing ambiguities and complicated transport equivalence.
- *The Local Trust Fallacy*: Assuming Unix Domain Socket connections were inherently trusted because they originated on localhost violated the principle of least privilege.
- *Duplicated GitOps Execution*: Both `gitops_dispatcher.py` and `scripts/appctl` maintained independent, divergent implementations of `git pull` and `docker compose up`.
- *Insecure Environment Sourcing*: The bash CLI still parsed environment variables via shell `source`, failing to run Compose AST security pre-flight checks on operator commands.

### The Locked Architectural Decisions (`DEC-01` through `DEC-05`)
To eliminate ambiguity, five binding architectural decisions were codified:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ROADMAP v6: LOCKED DECISIONS                          │
├─────────┬───────────────────────────────┬───────────────────────────────────┤
│ DEC-01  │ Unified Transport & Router    │ Single POST /v1/operations        │
│         │                               │ Strict HTTP/1.1 on UDS & TCP      │
├─────────┼───────────────────────────────┼───────────────────────────────────┤
│ DEC-02  │ Host Access != Mutation Auth  │ Mandatory Bearer token for writes │
│         │                               │ UDS SO_PEERCRED = viewer read only│
├─────────┼───────────────────────────────┼───────────────────────────────────┤
│ DEC-03  │ Service Identity & Isolation  │ User: homelab-appctl              │
│         │                               │ Fail-closed audit log (0600)      │
├─────────┼───────────────────────────────┼───────────────────────────────────┤
│ DEC-04  │ Unified GitOps Worker         │ Dispatcher delegates to daemon    │
│         │                               │ Single execution codepath         │
├─────────┼───────────────────────────────┼───────────────────────────────────┤
│ DEC-05  │ Pure-Python Pre-Flight & Env  │ No shell 'source' or 'eval'       │
│         │                               │ Mandatory Compose AST inspection  │
└─────────┴───────────────────────────────┴───────────────────────────────────┘
```

#### 1. Single Command-Oriented Operational Router (`DEC-01`)
Instead of dozens of disparate REST endpoints, the daemon exposes **one canonical endpoint**:
- `POST /v1/operations`: Dispatches all 13 canonical domain operations (both read-only and mutating) using strict Pydantic v2 schemas (`extra="forbid"`, `strict=True`).
- `GET /v1/health`: A simple convenience probe for orchestrator liveness.
- Logs are strictly bounded (`tail: 1..1000`, max 256 KiB output buffer); live SSE streaming is deferred to Milestone P7.

#### 2. Host Access Does Not Confer Mutation Authority (`DEC-02`)
Entering the server via SSH confers Unix access, but **zero operational control plane privileges**:
- Mutating operations (`workload.deploy`, `workload.update`, etc.) and sensitive reads (`workload.config`, `workload.logs`) strictly require an authenticated Bearer token validated against `/run/secrets/appctl/tokens.json` using constant-time hashing (`hmac.compare_digest`).
- Local Unix socket connections without a token leverage kernel peer credentials (`SO_PEERCRED`). If the calling UID belongs to an authorized operator, the caller is granted **`homelab-viewer` privileges only**—enabling zero-friction inspection (`appctl list`, `appctl info`) and tab-completion while blocking all mutations.

#### 3. Dedicated Service Identity & Fail-Closed Audit Guard (`DEC-03`)
The daemon executes under an isolated system user:
- `User = "homelab-appctl"`, `Group = "homelab-operators"`.
- Operator processes and AI sessions running as `<operator>` cannot read daemon token secrets (`mode 0400`) or forge/tamper with audit logs (`mode 0600`).
- **Fail-Closed Disk Guard**: Before any mutating subprocess (Docker/Git) executes, a `DISPATCHED` audit record must be written and flushed to disk. If the audit log fails to write (disk full, permissions error), **the operation immediately aborts with `500 ERR_EXECUTION_FAILED`**.

#### 4. Unified GitOps Execution Path (`DEC-04`)
The background worker in `gitops_dispatcher.py` no longer directly invokes `docker compose` or `git pull`. Instead, it admits the webhook push against `config/deployments.yaml`, manages the commit queue, and dispatches an authenticated `workload.update` command to the daemon over `/run/homelab/appctl.sock`.

#### 5. Inert Pure-Python Environment Assembly (`DEC-05`)
All shell sourcing is eradicated:
- Subprocess environments are assembled in memory using an inert pure-Python key-value parser.
- Variable keys are validated against strict regexes (`ENV_KEY_RE`) and forbidden from overriding reserved infrastructure parameters (`RESERVED_ENV_KEYS`).
- Every workload Compose file is passed through `validate_compose_security()` prior to execution, rejecting privileged containers, host networking, and arbitrary socket mounts.

---

## 🏛️ Comprehensive Architecture Comparison: v1 vs. v6

```text
┌──────────────────────┬───────────────────────────────┬────────────────────────────────┐
│ Dimension            │ Era 1 (v1 Baseline)           │ Era 6 (v6 Locked Target)       │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Runtime Engine       │ Bash wrapper script           │ Dedicated Python 3 daemon      │
│                      │ (`scripts/appctl`)            │ (`homelab-appctl.service`)     │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Transports           │ Local shell subprocesses only │ Dual HTTP/1.1:                 │
│                      │                               │ • /run/homelab/appctl.sock     │
│                      │                               │ • 127.0.0.1:9001               │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Authentication Gate  │ Host Unix user permissions    │ Mandatory SHA-256 Bearer token │
│                      │ (Entering via SSH = Admin)    │ (UDS peercred = Viewer only)   │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ RBAC Tiers           │ None (Binary host access)     │ 3-Role Hierarchy:              │
│                      │                               │ • homelab-admin (All targets)  │
│                      │                               │ • homelab-operator (Whitelisted│
│                      │                               │   Sites workloads only)        │
│                      │                               │ • homelab-viewer (Read-only)   │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ API Surface          │ Ad-hoc CLI subcommands        │ Single POST /v1/operations     │
│                      │ (Arbitrary flag parsing)      │ Strict Pydantic v2 schemas     │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Environment Parsing  │ Shell `source "$APP_DIR/.env"`│ Pure-Python inert key-value    │
│                      │ (Vulnerable to injection)     │ parser with reserved key locks │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Compose Security     │ Unvalidated direct execution  │ Pre-flight Compose AST validator│
│                      │                               │ (Blocks root/socket escapes)   │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ GitOps Engine        │ Disparate worker script with  │ Webhook ingress delegates to   │
│                      │ duplicated pull/up logic      │ daemon workload.update over UDS│
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Audit Telemetry      │ Ephemeral terminal stdout     │ Append-only RFC JSONL audit log│
│                      │                               │ with fail-closed disk guard    │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Persistent State     │ Mixed in Git working trees    │ Isolated under                 │
│                      │ (`Core/config/`, `Sites/`)    │ `~/var/lib/homelab/<app>/`     │
├──────────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Concurrency Control  │ Uncoordinated race conditions │ Per-target non-blocking flock  │
│                      │                               │ (Immediate 409 Conflict)       │
└──────────────────────┴───────────────────────────────┴────────────────────────────────┘
```

---

## 💡 Key Engineering Takeaways & Mental Models

### 1. Boundaries Must Precede Implementation
In the early days of a project, the temptation is to jump straight into writing daemon server loops. However, the pre-P4 audit proved that without explicit boundary contracts, developers end up making accidental architectural commitments during implementation (such as inventing multiple REST routes, exposing unredacted logs, or allowing tokenless mutations over Unix sockets). Resolving `DEC-01` through `DEC-05` before writing code ensured every implementation slice has an unambiguous Definition of Done.

### 2. The Illusion of Local Trust
A pervasive security trap in homelab and developer tooling is assuming that if a request originates on `localhost` or over a Unix domain socket, the caller can be trusted. In a modern environment where developers run complex dependency trees, automated pipelines, and autonomous AI coding assistants, **the host is a multi-tenant boundary**. Enforcing explicit Bearer tokens for all mutations over both network and socket transports guarantees that entering the machine via SSH does not give arbitrary tools free rein over infrastructure.

### 3. Fail-Closed by Design
Systems fail in messy, unpredictable ways: disks run out of space, DNS records fail to resolve, YAML manifests contain syntax errors. A resilient system does not attempt to "best-effort" its way through uncertainty. If the manifest does not strictly match the Pydantic schema, it fails. If Compose tries to mount `/var/run/docker.sock`, it aborts. If the audit log cannot append a `DISPATCHED` record to disk, the mutation halts immediately before any container is touched.

### 4. Evolutionary Design is Not Indecision
Progressing from v1 to v6 is not evidence of bad initial planning; it is the natural consequence of real-world learning. Systems must be built to solve today's operational problems while establishing the clear interfaces, automated regression suites, and architectural records necessary to safely refactor them tomorrow.

---

## 🔗 Related Knowledge & System Artifacts

- **Active Plan**: [Architecture Consolidation & Control Plane Roadmap v6](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v6.md)
- **Authoritative ADRs**:
  - [ADR: Homelab appctl Control Plane Architecture](../../../03-records/decisions/homelab-appctl-control-plane-architecture.md)
  - [ADR: Homelab 3-Tier Architecture & Provenance](../../../03-records/decisions/homelab-3tier-architecture-and-provenance.md)
- **Historical Lineage**:
  - [Roadmap v5 (Superseded)](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v5.md)
  - [Roadmap v4 (Superseded)](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v4.md)
  - [Roadmap v3 (Superseded)](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v3.md)
  - [Roadmap v2 (Superseded)](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap-v2.md)
  - [Roadmap v1 (Superseded)](../../../01-plans/homelab/consolidation/architecture-consolidation-roadmap.md)
