---
type: plan
status: active
project: homelab
tags:
  - architecture
  - security
  - operations
  - homelab
  - gitops
  - implementation
  - migration
  - provenance
---

# Homelab Core — Architecture Consolidation & Hardening Implementation Guide v4

> **Companion Architecture Roadmap**: [`architecture-consolidation-roadmap-v4.md`](architecture-consolidation-roadmap-v4.md)
>
> **Target System**: `roadtotech.me` (NixOS appliance `Core/`, application workloads `Sites/`)
>
> **Execution Philosophy**: Local-first investigation, zero unverified state mutations, reversible staged migrations, atomic commit proposals.

---

## 1. Implementation Status & Execution Progress

| Phase / Workstream | Status | Target Scope / Key Deliverables | Verification Gates |
| :--- | :--- | :--- | :--- |
| **P0: Architecture Re-Baseline** | **📐 DRAFTED** | 3-Tier taxonomy, source vs image-only workload classes, controller authority matrix, resource ownership matrix, dependency graphs. | Documentation reviews, structural linting. |
| **P1: Mail Topology Realignment** | **🎯 UP NEXT** | Move Stalwart to `smtp.roadtotech.me`; move SnappyMail to `~/Sites/snappymail` (`mail.roadtotech.me`) with zero data loss. | Verified rollback archive, state parity proof, IMAP/SMTP auth, address book survival, Diun delivery test. |
| **P2: GitOps Privilege & Authority** | **⏳ PENDING** | Authoritative Core repository registry, decoupled CI vs deploy webhook routing, Brain pull-only policy, workload Compose security policy, systemd sandboxing. | Flake check, unit tests for admission and containment, path traversal tests, Compose policy validation tests. |
| **P3: Manifest Convergence** | **⏳ PENDING** | Schema v1.0, single typed parser library (`core_manifest.py`), `SourceConfig` domain model & ref semantics, integrate `appctl-v2`. | Manifest validation in CI, schema lint tests, unit tests for `SourceConfig`. |
| **P4: Platform Lifecycle & Health** | **⏳ PENDING** | Service readiness probes in Core Compose, `condition: service_healthy` startup gating, image update policy. | Docker health inspects, dependency startup ordering tests. |
| **P5: Deployment Truth & Ledger** | **⏳ PENDING** | Two operational inspection axes with three revision identities (`deployment_config_revision`, `source_revision`, `artifact_digest`), atomic status record, `appctl history`. | Dispatcher status test fixtures, ledger serialization accuracy tests. |

---

## 2. Mandatory Working Rules

### Rule 1 — One Production Transition at a Time (Parallel Refactoring Permitted)
Never combine mail infrastructure relocation, GitOps privilege modifications, and manifest schema refactors into single sweeping production changes. Keep each architectural phase isolated on dedicated git branches.

However, independent internal implementation refactors (specifically `appctl-v2` on branch `refactor/appctl-rework`) **may proceed concurrently in an isolated worktree**, provided they do not trigger production cutovers and strictly preserve the established architectural integration seams.

### Rule 2 — Absolute Preservation of Application State
State-bearing workloads must never be modified using destructive commands (`rm -rf`, `docker compose down -v`, or unverified moves). State directory migrations require an explicit pre-flight freeze, recursive archive with preserved timestamps/permissions, and parallel staging before live cutover.

### Rule 3 — Single Source of Truth
Never duplicate service definitions or trust boundaries across disparate files. Core owns the platform catalog; the authoritative registry owns admission paths; `core_manifest.py` owns workload manifest parsing.

### Rule 4 — The User Controls Production Transitions
Per Homelab Agent Guidelines: The agent investigates, crafts local code changes, and verifies tests locally. The user reviews atomic commit proposals, merges to `main`, and runs production deployments (`nixos-rebuild switch`, container recreation).

### Rule 5 — Immutable Integration Seams Across Tracks
The interfaces connecting Track A (`main`) and Track B (`appctl-v2`) must not undergo uncoordinated drift: CLI syntax, `resolve` JSON contract, canonical service identifiers, and Homepage generation semantics remain stable until Milestone P3 convergence.

### Rule 6 — Minimal Control Path & Orchestrator Restraint (KISS)
The deployment delivery pipeline must remain strictly linear and minimal:
$$\text{Source Push} \longrightarrow \text{CI Build} \longrightarrow \text{GitOps Ingress} \longrightarrow \text{appctl update} \longrightarrow \text{Compose Up}$$
Do not introduce secondary orchestration systems, message brokers, queues, deployment databases, or rollback controllers around `appctl`. `appctl update` operates strictly as a declarative, standalone deployment reconciliation primitive.

---

## 2.1 Concurrent Track Coordination: Homelab Architecture vs. appctl-v2

Two major engineering tracks are active concurrently:
- **Track A (Production Architecture)**: Based on `main` in `/home/kiskaadee/Homelab/Core`. Owns host configuration, service topology (P1 mail migration), GitOps privilege separation (P2), and platform readiness (P4).
- **Track B (Implementation Modernization)**: Based on `refactor/appctl-rework` in `/home/kiskaadee/Projects/active/appctl-refactor`. Implements typed domain hierarchy (`SitesApp`, `CoreService`, `SourceConfig`), PyYAML ingestion, Docker label inspection, and TDD unit tests.

### Operating Protocol Between Tracks

1. **Seam Isolation (Do Not Cross-Merge Branches Early)**:
   Do not continuously merge `main` into `refactor/appctl-rework` or vice versa.
2. **Phase 1 Coordination (Mail Topology)**:
   - **On `main`**: Apply the minimal required compatibility patch to legacy `scripts/appctl_engine.py`: change `stalwart` domain to `smtp.roadtotech.me`, remove `snappymail` from `get_core_services()`.
   - **On `refactor/appctl-rework`**: Update typed `CoreService` in `scripts/appctl_engine_v2.py` symmetrically. Requires zero branch merging.
3. **Phase 2 Coordination (GitOps Authority)**:
   Phase 2 operates on `Core/nixos` systemd units and `Core/scripts/gitops_dispatcher.py`. It has zero dependencies on `appctl` and can execute without touching Track B.
4. **Phase 3 Convergence (The Controlled Integration Seam)**:
   Phase 3 is the deliberate join point. `core_manifest.py` originates authoritatively on `main` (validated against `gitops_dispatcher.py`). That atomic commit is cherry-picked into `refactor/appctl-rework`, `appctl-v2` adapts its manifest ingestion to the shared module and verifies its unit tests, and finally `refactor/appctl-rework` merges into `main`.

---

## 3. Phase 0: Architecture Re-Baseline & Structural Catalog

### Deliverable 0.1: Service Taxonomy & 3-Tier Architecture
Update `Core/docs/architecture.md` and repository guidelines to formalize:
1. **Tier 1: Software Layer**: Application source repositories (Gitea/GitHub).
2. **Intermediate Artifacts**: OCI images tagged with `org.opencontainers.image.revision`.
3. **Tier 2: Deployment Layer**: `~/Sites/*` catalog owning `app.yaml` and `docker-compose.yml`.
4. **Tier 3: Platform Layer**: Homelab Core appliance (NixOS, Traefik, Authelia, LLDAP, Stalwart, controllers).
5. **Workload Classification**:
   - Class A: Source-Backed (`source:` block present in `app.yaml`).
   - Class B: Image-Only (`source:` block omitted).

### Deliverable 0.2: Controller Authority Matrix
Document authoritative control loops across systemd, Docker Compose, GitOps, CI runners, and `appctl` in `Core/docs/architecture.md`.

### Deliverable 0.3: Resource & State Ownership Matrix
Formalize persistent state ownership for every component: owner, filesystem location, desired state source, and runtime state form.

---

## 4. Phase 1: Mail Topology Realignment & Zero-Data-Loss Migration Runbook

### Architectural Context & Invariants
- **Stalwart**: Remains in Core as platform capability. Public endpoint moves to `smtp.roadtotech.me`. Persistent mail store (`Core/config/stalwart/data`) is never moved.
- **SnappyMail**: Moves from `Core/docker-compose.yml` to `~/Sites/snappymail` as an **Image-Only Class B Workload** (`mail.roadtotech.me`). Persistent state (`Core/config/snappymail/data`) is copied to `~/Sites/snappymail/data`.

### Step-by-Step Migration Execution

#### Step 1.1: Pre-Migration Health Audit
Verify existing Stalwart and SnappyMail containers and note running IDs:
```bash
docker ps --filter "name=stalwart" --filter "name=snappymail" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

#### Step 1.2: State Freeze
Halt SnappyMail to prevent database mutation during backup:
```bash
docker stop snappymail
```

#### Step 1.3: Verified Pre-Cutover Backup Archive
Create a compressed archive with permissions and timestamps preserved, generate a SHA-256 hash, and verify test extraction:
```bash
mkdir -p ~/backups/pre-mail-cutover-$(date +%F)
tar -czpf ~/backups/pre-mail-cutover-$(date +%F)/snappymail-data.tar.gz -C ~/Homelab/Core/config/snappymail data
sha256sum ~/backups/pre-mail-cutover-$(date +%F)/snappymail-data.tar.gz > ~/backups/pre-mail-cutover-$(date +%F)/snappymail-data.tar.gz.sha256
tar -tzf ~/backups/pre-mail-cutover-$(date +%F)/snappymail-data.tar.gz | head -n 10
```

#### Step 1.4: Workload Scaffolding & State Directory Provisioning
1. Provision isolated persistent state root outside the Git repository:
   ```bash
   mkdir -p ~/var/lib/homelab/snappymail
   ```
2. Create `~/Sites/snappymail/app.yaml`:
   ```yaml
   schemaVersion: "1.0"
   name: "snappymail"
   displayName: "SnappyMail"
   description: "Lightweight Webmail Client"
   category: "Communication"

   network:
     ingress: true
     domain: "mail.roadtotech.me"
     publishedPort: 8888
     internalOnly: false

   deployment:
     strategy: compose
     preflight:
       filesRequired:
         - docker-compose.yml
     healthcheck:
       type: http
       path: "/"
       expectedStatus: 200
       timeoutSeconds: 30
   ```
3. Create `~/Sites/snappymail/docker-compose.yml` configured to connect to Stalwart via `proxy-net`, mount `~/var/lib/homelab/snappymail:/var/lib/snappymail/_data_`, and expose Traefik labels for `mail.roadtotech.me`.

#### Step 1.5: Non-Destructive State Replication & Parity Proof
Copy state from Core to `~/var/lib/homelab/snappymail/` and verify file count and parity:
```bash
cp -a ~/Homelab/Core/config/snappymail/data/* ~/var/lib/homelab/snappymail/
diff -r ~/Homelab/Core/config/snappymail/data ~/var/lib/homelab/snappymail
```

#### Step 1.6: Stalwart Endpoint Cutover in Core
1. Update `Core/docker-compose.yml`:
   - Change Stalwart domain Traefik labels from `mail.roadtotech.me` to `smtp.roadtotech.me`.
   - Update `STALWART_PUBLIC_URL=https://smtp.roadtotech.me`.
   - Remove SnappyMail service block entirely.
2. Apply Core changes:
   ```bash
   cd ~/Homelab/Core && docker compose up -d stalwart
   ```

#### Step 1.7: Workload Launch & Live Verification
1. Launch SnappyMail:
   ```bash
   cd ~/Sites/snappymail && docker compose up -d
   ```
2. Verify:
   - Public webmail at `https://mail.roadtotech.me` is accessible.
   - User logins and address books intact.
   - IMAP/SMTP connectivity between SnappyMail and Stalwart functional.
   - Diun alert delivery over SMTPS (port 465) functional.
3. Retain Core backup archive for 14 days before storage cleanup.

---

## 5. Phase 2: GitOps Privilege & Authority Hardening

### Deliverable 2.1: Authoritative Core Repository Registry
1. Establish `Core/config/deployments.yaml` as the sole authority for admitted deployment repositories.
2. Manifests in `Sites` **cannot** declare aliases or alter admission paths.

### Deliverable 2.2: The CI-to-Deployment Reconciliation Pipeline
Formalize the authoritative event flow from software build to live runtime:
1. Pushes to Application Source repositories trigger Gitea Actions CI to test and build container images, embedding `org.opencontainers.image.revision`.
2. On successful image publishing, CI emits an authenticated deployment event to GitOps (`POST /webhook/deploy/<app>`).
3. GitOps verifies HMAC admission against Core's registry, acquires `.gitops.lock`, and invokes `appctl update <app>`.
4. `appctl update` reconciles the deployment:
   - Pulls Sites deployment descriptors.
   - Runs `docker compose pull` to retrieve the newly published image.
   - Recreates containers with `docker compose up -d`.
   - Runs healthchecks and records the 3-axis truth ledger.
   - **Prohibited**: Host never compiles code or clones application source.

### Deliverable 2.3: Second Brain Read-Only Data-Vault Policy
Designate `~/Brain` as a read-only vault with `strategy: pull-only`, isolated from Docker socket access.

### Deliverable 2.4: Workload Compose Security Policy
Implement pre-flight Compose AST validation in `Core/scripts/gitops_dispatcher.py` to reject:
- `privileged: true`
- Direct Docker socket bind mounts (`/var/run/docker.sock`)
- `network_mode: host` or `pid: host`
- Host root mounts outside `~/var/lib/homelab/<app>/`

### Deliverable 2.5: Systemd Service Sandboxing
Update `Core/nixos/modules/gitops.nix` with strict systemd execution constraints (`ProtectSystem=strict`, `NoNewPrivileges=true`, restricted `ReadWritePaths`).

---

## 6. Phase 3: Manifest Contract Convergence & appctl-v2 Integration

### Deliverable 3.1: Manifest Schema v1.0 & Parser Library (`core_manifest.py`)
Implement the single authoritative parser on `main`:
- Strongly-typed parsing using PyYAML and `@dataclass`.
- Implements `SourceConfig(type, url, ref)`:
  - Validates `source.type == "git"`.
  - Validates `source.url` format and enforces permitted transports (`https://`, `ssh://`, `git@`); rejects `file://` or relative paths.
  - Enforces 10-second timeout on remote Git inspections (`git ls-remote`).
  - Resolves `source.ref` tracking semantics (Branch vs Tag vs Commit SHA).
- Rejects unknown top-level keys.

### Deliverable 3.2: Workload Catalog Migration
Audit all `~/Sites/*/app.yaml` files:
- Source-backed apps (`doc2site`, `courses`): declare `source: { type: git, url: ..., ref: main }`.
- Image-only apps (`snappymail`, `jellyfin`, `stirling`): omit `source:` block.

### Deliverable 3.3: In-House Application Source Migration Runbook
For workloads where source code was previously co-located with deployment configs (e.g. `doc2site`):
1. Create standalone upstream Git repository on Gitea (e.g., `git.roadtotech.me/kiskaadee/doc2site`).
2. Move application source, `Dockerfile`, and tests to the new repo; remove all Homelab Traefik/network files.
3. Configure Gitea Actions CI workflow:
   ```yaml
   name: Build and Publish Image
   on:
     push:
       branches: [main]
   jobs:
     build:
       runs-on: nixos-act-runner
       steps:
         - uses: actions/checkout@v4
         - name: Build OCI Image
           run: |
             docker build \
               --label "org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}" \
               --label "org.opencontainers.image.revision=${{ github.sha }}" \
               -t registry.roadtotech.me/kiskaadee/doc2site:latest .
             docker push registry.roadtotech.me/kiskaadee/doc2site:latest
   ```
4. Update `Sites/doc2site/`:
   - `app.yaml`: declare `source: { type: git, url: "https://git.roadtotech.me/kiskaadee/doc2site.git", ref: "main" }`.
   - `docker-compose.yml`: reference `registry.roadtotech.me/kiskaadee/doc2site:latest`.

### Deliverable 3.4: appctl-v2 Convergence
1. Cherry-pick `core_manifest.py` from `main` into `refactor/appctl-rework`.
2. Connect `appctl_engine_v2.py` to `core_manifest.py`.
3. Verify test suite passes (`pytest`, `ruff`, `pyright`).
4. Promote `appctl_engine_v2.py` to `appctl_engine.py` on `refactor/appctl-rework` and merge into `main`.

---

## 7. Phase 4: Platform Lifecycle & Readiness Contracts

### Deliverable 4.1: Service Healthchecks & Dependency Gating
Add deterministic healthchecks in `Core/docker-compose.yml` and enforce `condition: service_healthy` across dependent chains:
- Traefik depends on socket-proxy healthy.
- Authelia depends on LLDAP healthy.
- Diun depends on Stalwart healthy.
- Dozzle/Homepage depend on Authelia healthy.

---

## 8. Phase 5: Deployment Truth & Historical Ledger

### Deliverable 5.1: Two Operational Inspection Axes & Three Revision Identities in GitOps Dispatcher
Record true deployment facts in `~/.local/state/homelab/gitops/ledger/<app>.json`:
```json
{
  "workload": "bitetrack",
  "deployment_config_revision": "c8f12a4",
  "source_revision": "e4a81b2",
  "artifact_digest": "sha256:7b9c45e812a...",
  "deployed_at": "2026-09-28T20:25:00Z",
  "duration_seconds": 12.4,
  "status": "success",
  "failure_stage": null
}
```
*Note: `artifact_digest` is extracted directly from the container inspect `RepoDigests` field, capturing the immutable OCI registry digest.*

### Deliverable 5.2: `appctl history` Command
Implement CLI inspection of the deployment ledger in `appctl_engine.py`.
