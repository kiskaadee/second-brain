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
---

# Homelab Core — Architecture Consolidation & Hardening Implementation Guide v3

> **Companion Architecture Roadmap**: [`architecture-consolidation-roadmap-v3.md`](architecture-consolidation-roadmap-v3.md)
>
> **Target System**: `roadtotech.me` (NixOS appliance `Core/`, application workloads `Sites/`)
>
> **Execution Philosophy**: Local-first investigation, zero unverified state mutations, reversible staged migrations, atomic commit proposals.

---

## 1. Implementation Status & Execution Progress

| Phase / Workstream | Status | Target Scope / Key Deliverables | Verification Gates |
| :--- | :--- | :--- | :--- |
| **P0: Architecture Re-Baseline** | **📐 DRAFTED** | Taxonomy definitions, controller authority matrix, resource ownership matrix, dependency graphs, AGENTS alignment. | Documentation reviews, structural linting. |
| **P1: Mail Topology Realignment** | **🎯 UP NEXT** | Move Stalwart to `smtp.roadtotech.me`; move SnappyMail to `~/Sites/snappymail` (`mail.roadtotech.me`) with zero data loss. | Verified rollback archive, state parity proof, IMAP/SMTP auth, address book survival, Diun delivery test. |
| **P2: GitOps Privilege & Authority** | **⏳ PENDING** | Authoritative Core repository registry, inverted trust boundary, alias collision rejection, Brain pull-only policy, workload Compose security policy, systemd sandboxing. | Flake check, unit tests for admission and containment, path traversal tests, Compose policy validation tests. |
| **P3: Manifest Convergence** | **⏳ PENDING** | Schema v1.0, single typed parser library (`core_manifest.py`), declarative `strategy: compose`, migrate `~/Sites/*`. | Manifest validation in CI, schema lint tests. |
| **P4: Platform Lifecycle & Health** | **⏳ PENDING** | Service readiness probes in Core Compose, `condition: service_healthy` startup gating, image update policy. | Docker health inspects, dependency startup ordering tests. |
| **P5: Deployment Truth & Ledger** | **⏳ PENDING** | Track `requested_revision`, `deployed_revision`, `previous_revision`, atomic status record, `appctl history`. | Dispatcher status test fixtures, superseding accuracy tests. |

---

## 2. Mandatory Working Rules

### Rule 1 — One Architectural Workstream at a Time
Never combine mail infrastructure relocation, GitOps privilege modifications, and manifest schema refactors into single sweeping PRs. Keep each phase isolated on dedicated git branches (`feat/mail-topology-realignment`, `feat/gitops-authority-hardening`, etc.).

### Rule 2 — Absolute Preservation of Application State
State-bearing workloads must never be modified using destructive commands (`rm -rf`, `docker compose down -v`, or unverified moves). State directory migrations require an explicit pre-flight freeze, recursive archive with preserved timestamps/permissions, and parallel staging before live cutover.

### Rule 3 — Single Source of Truth
Never duplicate service definitions or trust boundaries across disparate files. Core owns the platform catalog; the authoritative registry owns admission paths; `core_manifest.py` owns workload manifest parsing.

### Rule 4 — The User Controls Production Transitions
Per Homelab Agent Guidelines: The agent investigates, crafts local code changes, and verifies tests locally. The user reviews atomic commit proposals, merges to `main`, and runs production deployments (`nixos-rebuild switch`, container recreation).

---

## 3. Phase 0: Architecture Re-Baseline & Structural Catalog

### Deliverable 0.1: Service Taxonomy & Platform Topology
Update `Core/docs/architecture.md` and repository guidelines to formalize the 5-tier taxonomy:
1. Host Foundation (NixOS, systemd, Docker, nftables, SOPS)
2. Edge & Security Primitives (Traefik, socket-proxy, Authelia, LLDAP)
3. Core Platform Capabilities (Stalwart)
4. Platform Operations (Homepage, Dozzle, Diun, Watchtower)
5. Workload Plane (`~/Sites/*`)

### Deliverable 0.2: Controller Authority Matrix
Document authoritative control loops across systemd, Docker Compose, GitOps, `appctl`, and CI runners in `Core/docs/architecture.md`.

### Deliverable 0.3: Resource & State Ownership Matrix
Document persistent state ownership for every stateful resource. For each resource, define: owner, filesystem location, desired state source (Git, generated, runtime-only), and runtime state form. This matrix makes migration and recovery semantics explicit and prevents ambiguity about who owns what data.

---

## 4. Phase 1: Mail Topology Realignment & Zero-Data-Loss Migration Runbook

### Architectural Context & Invariants
- **Stalwart**: Remains in Homelab Core. Public endpoint moves from `mail.roadtotech.me` to `smtp.roadtotech.me`. Persistent mail store (`Core/config/stalwart/data`) is never moved.
- **SnappyMail**: Moves from `Core/docker-compose.yml` to `~/Sites/snappymail/docker-compose.yml`. Public endpoint moves from `webmail.roadtotech.me` to `mail.roadtotech.me`. Persistent state (`Core/config/snappymail/data`) is safely copied to `~/Sites/snappymail/data`.

### Step-by-Step Migration Execution

#### Step 1.1: Pre-Migration Health Audit
Verify existing Stalwart and SnappyMail containers and note running IDs:
```bash
ssh server-local "docker ps --filter 'name=stalwart' --filter 'name=snappymail'"
ssh server-local "ls -la ~/Core/config/stalwart/ ~/Core/config/snappymail/data"
```

#### Step 1.2: Freeze SnappyMail in Core
Prevent active user sessions or settings modifications while preserving Stalwart:
```bash
ssh server-local "docker stop snappymail"
```

#### Step 1.3: Create Verified Rollback Archive
Create a compressed archive of SnappyMail state with permissions and timestamps preserved:
```bash
ssh server-local "tar -czpf ~/snappymail-backup-\$(date +%Y%m%d%H%M%S).tar.gz -C ~/Core/config/snappymail data"
```
Generate a checksum for the archive:
```bash
ssh server-local "sha256sum ~/snappymail-backup-*.tar.gz"
```
Verify archive integrity by performing a test extraction into a temporary directory:
```bash
ssh server-local "mkdir -p /tmp/snappymail-verify && tar -xzf ~/snappymail-backup-*.tar.gz -C /tmp/snappymail-verify && diff -r ~/Core/config/snappymail/data /tmp/snappymail-verify/data && echo 'Archive verified OK' && rm -rf /tmp/snappymail-verify"
```
**Gate**: Do not proceed until archive extraction matches the live source directory.

#### Step 1.4: Scaffold Sites Workload (`~/Sites/snappymail`)
Create local directory structure:
```bash
mkdir -p ~/Sites/snappymail/data
```

Create `~/Sites/snappymail/app.yaml`:
```yaml
schemaVersion: "1.0"
name: "snappymail"
displayName: "SnappyMail"
description: "Modern Lightweight Webmail Client"
category: "Communication"

network:
  ingress: true
  domain: "mail.roadtotech.me"
  publishedPort: 8888
  internalOnly: false

deployment:
  strategy: compose
  branch: main
  preflight:
    filesRequired:
      - docker-compose.yml
      - data
```

Create `~/Sites/snappymail/docker-compose.yml`:
```yaml
services:
  snappymail:
    image: ghcr.io/the-djmaze/snappymail:latest
    container_name: snappymail
    restart: always
    volumes:
      - ./data:/var/lib/snappymail/_data_
    networks:
      - proxy-net
    labels:
      - "traefik.enable=true"
      # Public (HTTPS)
      - "traefik.http.routers.snappymail.rule=Host(`mail.${DOMAIN}`)"
      - "traefik.http.routers.snappymail.entrypoints=websecure"
      - "traefik.http.routers.snappymail.tls=true"
      - "traefik.http.routers.snappymail.tls.certresolver=myresolver"
      - "traefik.http.routers.snappymail.service=snappymail-svc"
      # Public (Redirect HTTP -> HTTPS)
      - "traefik.http.routers.snappymail-red.rule=Host(`mail.${DOMAIN}`)"
      - "traefik.http.routers.snappymail-red.entrypoints=web"
      - "traefik.http.routers.snappymail-red.middlewares=https-redirect@docker"
      # Backend Port
      - "traefik.http.services.snappymail-svc.loadbalancer.server.port=8888"

networks:
  proxy-net:
    external: true
```

#### Step 1.5: Non-Destructive State Copy & Verification
Replicate existing configuration data to `~/Sites/snappymail/data/` preserving ownership, timestamps, and hidden files:
```bash
ssh server-local "cp -a ~/Core/config/snappymail/data/. ~/Sites/snappymail/data/"
```
*(Notice: The original `~/Core/config/snappymail/data` is left untouched as an emergency rollback anchor).*

Verify source/destination parity before proceeding:
```bash
# File count comparison
ssh server-local "echo 'Source:' && find ~/Core/config/snappymail/data -type f | wc -l && echo 'Destination:' && find ~/Sites/snappymail/data -type f | wc -l"

# Byte count comparison
ssh server-local "echo 'Source:' && du -sb ~/Core/config/snappymail/data && echo 'Destination:' && du -sb ~/Sites/snappymail/data"

# Recursive diff (should produce no output)
ssh server-local "diff -r ~/Core/config/snappymail/data ~/Sites/snappymail/data"

# Ownership/permissions spot-check
ssh server-local "ls -laR ~/Sites/snappymail/data | head -n 30"
```
**Gate**: Do not proceed to Step 1.6 until file count, byte count, and recursive diff confirm exact parity.

#### Step 1.6: Update Stalwart in `Core/docker-compose.yml`
1. Reconfigure Stalwart's public identity and Traefik labels from `mail.${DOMAIN}` to `smtp.${DOMAIN}`:
```yaml
    environment:
      - DOMAIN=${DOMAIN}
      - STALWART_PUBLIC_URL=https://smtp.${DOMAIN}
      - STALWART_RECOVERY_ADMIN=admin:${LLDAP_LDAP_USER_PASS}
    labels:
      - "traefik.enable=true"
      # HTTPS WebAdmin & JMAP Router
      - "traefik.http.routers.stalwart.rule=Host(`smtp.${DOMAIN}`)"
      - "traefik.http.routers.stalwart.entrypoints=websecure"
      - "traefik.http.routers.stalwart.tls=true"
      - "traefik.http.routers.stalwart.tls.certresolver=myresolver"
      - "traefik.http.routers.stalwart.service=stalwart-svc"
      # HTTP -> HTTPS Redirect
      - "traefik.http.routers.stalwart-red.rule=Host(`smtp.${DOMAIN}`)"
      - "traefik.http.routers.stalwart-red.entrypoints=web"
      - "traefik.http.routers.stalwart-red.middlewares=https-redirect@docker"
      - "traefik.http.services.stalwart-svc.loadbalancer.server.port=8080"
```
2. Remove the `snappymail:` service definition from `Core/docker-compose.yml`.

#### Step 1.7: Update Core Platform Tooling (`appctl_engine.py`)
1. Remove `snappymail` from Core services list (`get_core_services()`) in `Core/scripts/appctl_engine.py`.
2. Update `stalwart` entry in `get_core_services()`:
```python
{"name": "stalwart", "domain": "smtp.roadtotech.me", "container": "stalwart", "desc": "All-in-one Mail Server & JMAP/IMAP/SMTP"}
```
3. Update Homepage metadata mapping so `stalwart` points to `smtp.roadtotech.me`.

**Note**: The [appctl refactor](appctl/appctl-engine-v2-refactoring.md) is not completed (commit 5fc5ad86562e44246c2b0bb940f8626ce3311a0f (HEAD -> refactor/appctl-rework, origin/refactor/appctl-rework)). This change can be implemented in the running appctl version, and should be pinned as a task for appctl-v2.
#### Step 1.8: Production Cutover & Verification
Deploy the Core update:
```bash
ssh server-local "cd ~/Core && docker compose up -d stalwart && docker rm -f snappymail"
```
Start the new SnappyMail workload:
```bash
ssh server-local "cd ~/Sites/snappymail && docker compose up -d"
```

#### Step 1.9: Verification Checklist
- [ ] `https://smtp.roadtotech.me`: Stalwart WebAdmin loads, TLS certificate valid.
- [ ] `https://mail.roadtotech.me`: SnappyMail webmail interface loads, TLS certificate valid.
- [ ] SnappyMail authenticates via LLDAP credentials against Stalwart (`stalwart:993` / IMAPS).
- [ ] User address books, signatures, and custom folder configurations are intact.
- [ ] Inbound/outbound email test succeeds.
- [ ] Diun notification delivery test succeeds (`stalwart:465` with TLS).
- [ ] `appctl list` shows `stalwart` under Core and `snappymail` under Workloads.

#### Step 1.10: Rollback Procedure (If issues occur)
If webmail fails or state corruption is suspected:
```bash
# 1. Stop Sites workload
ssh server-local "cd ~/Sites/snappymail && docker compose down"

# 2. Revert Core/docker-compose.yml changes via Git
ssh server-local "cd ~/Core && git checkout HEAD -- docker-compose.yml"

# 3. Bring Core stack back up (restoring original mail.roadtotech.me & webmail.roadtotech.me)
ssh server-local "cd ~/Core && docker compose up -d"
```

---

## 5. Phase 2: GitOps Privilege & Authority Hardening

### Deliverable 2.1: Core Authoritative Repository Registry
Create `Core/config/deployments.yaml` as the sole authority for repository identity and filesystem location. The registry answers **WHO** and **WHERE**; the workload's `app.yaml` answers **WHAT** deployment intent to execute.

```yaml
# Core/config/deployments.yaml — Authoritative Repository Identity Registry
# Owns: repository identity, canonical filesystem path, coarse admission mode.
# Does NOT own: deployment strategy, branch, healthchecks (those belong to app.yaml).

schemaVersion: "1.0"
repositories:
  snappymail:
    path: "/home/kiskaadee/Sites/snappymail"
    mode: workload
  gitea:
    path: "/home/kiskaadee/Sites/gitea"
    mode: workload
  jellyfin:
    path: "/home/kiskaadee/Sites/jellyfin"
    mode: workload
  second-brain:
    path: "/home/kiskaadee/Brain"
    mode: data-vault
```

**Ownership Split**:

```text
Core registry (deployments.yaml)
    = WHO is admitted / WHERE it lives / WHAT mode (workload vs data-vault)

Workload manifest (app.yaml)
    = WHAT deployment intent (strategy, branch, healthcheck, metadata)

GitOps dispatcher
    = HOW that intent is executed safely
```

> [!IMPORTANT]
> Registry paths must be absolute. Python's `Path()` does not perform shell-style tilde expansion; `~/Sites/snappymail` resolves incorrectly. The implementation must use `Path(raw_path).expanduser().resolve()` or store fully expanded paths.

### Deliverable 2.2: Refactor `gitops_dispatcher.py` Admission Pipeline
1. Invert trust boundary: Replace dynamic scanning of `app.yaml` aliases with strict lookup in `Core/config/deployments.yaml`.
2. Explicitly reject duplicate aliases and path traversal.
3. Enforce directory containment strictly within `~/Sites` or designated data vaults.
4. Execute Brain sync with `strategy: pull-only` (isolated from Docker socket).

### Deliverable 2.3: Systemd Confinement for `homelab-gitops`
Update `Core/nixos/modules/homeserver.nix`:
```nix
systemd.services.homelab-gitops = {
  description = "Homelab GitOps Webhook Dispatcher";
  wantedBy = [ "multi-user.target" ];
  after = [ "network.target" "docker.service" ];

  serviceConfig = {
    Type = "simple";
    User = "kiskaadee"; # Transitioning to sandboxed profile
    WorkingDirectory = "/home/kiskaadee/Core";
    ExecStart = "${pkgs.python3}/bin/python3 /home/kiskaadee/Core/scripts/gitops_dispatcher.py --listen 127.0.0.1 --port 9000";
    Restart = "always";
    RestartSec = "5s";

    # Sandboxing & Confinement
    ProtectSystem = "strict";
    ProtectHome = "read-only";
    ReadWritePaths = [
      "/home/kiskaadee/Sites"
      "/home/kiskaadee/Brain"
      "/home/kiskaadee/.local/state/homelab/gitops"
      "/run/homelab-gitops"
    ];
    NoNewPrivileges = true;
    PrivateTmp = true;
    CapabilityBoundingSet = "";
    AmbientCapabilities = "";
  };
};
```

### Deliverable 2.4: Workload Compose Security Policy
The GitOps executor processes workload-authored `docker-compose.yml` files. A workload Compose file is itself a capability declaration and must be validated against Core security invariants before deployment.

**Pre-deployment validation must reject workload Compose files containing:**
- `privileged: true`
- `devices:` host device mappings
- `network_mode: host` or `pid: host` or `ipc: host`
- Direct Docker socket bind mounts (`/var/run/docker.sock`)
- `cap_add:` beyond a defined allowlist
- `security_opt:` overrides
- Arbitrary host path bind mounts outside the workload's own directory

**Implementation**:
1. Extend the existing `tests/security/` test suite to validate workload Compose files, not just `Core/docker-compose.yml`.
2. Add a pre-deployment Compose policy check in `gitops_dispatcher.py` that runs the same validations before executing `docker compose up`.
3. Define an explicit denied-capability list in `Core/config/compose-policy.yaml` or equivalent.

---

## 6. Phase 3: Manifest Contract Convergence

This requires further verification to integrate with the appctl refactor plan.
### Deliverable 3.1: Unified Manifest Parser (`core_manifest.py`)
Create a shared, strictly typed Python module (`Core/scripts/core_manifest.py`) implementing:
- Dataclass models (`WorkloadManifest`, `NetworkConfig`, `DeploymentConfig`, `HealthcheckConfig`).
- Strict schema enforcement: Rejection of unknown fields.
- Schema version gating (`schemaVersion: "1.0"`).
- Replaces duplicate `parse_yaml_simple()` across `appctl_engine.py` and `gitops_dispatcher.py`.

### Deliverable 3.2: Declarative Intent Transition
Deprecate procedural action vectors:
```text
OLD: actions: ["git_pull", "compose_up", "compose_build"]
NEW: deployment:
       strategy: compose
```

### Deliverable 3.3: Sites Manifest Migration
Update all manifests in `~/Sites/*/app.yaml` to schema v1.0.

---

## 7. Phase 4: Platform Lifecycle & Readiness Contracts

### Deliverable 4.1: Readiness Probes for Core Services
Every Core service that is a dependency of another service must expose a deterministic readiness signal via a Compose `healthcheck` block. The specific probe mechanism is chosen during implementation based on each image's available tools and version:

**Investigation targets** (verify against actual image capabilities before committing):
- **Traefik**: Built-in ping endpoint or CLI healthcheck
- **socket-proxy**: HTTP version endpoint on internal port
- **LLDAP**: Built-in healthcheck subcommand or TCP port probe
- **Authelia**: Built-in healthcheck subcommand
- **Stalwart**: TCP port probes on critical protocol ports (465, 993) or HTTP readiness endpoint

> [!NOTE]
> These are starting points for implementation research, not architectural commitments. The correct probe for each service depends on the container image version, available utilities, and startup characteristics discovered during P4 implementation.

### Deliverable 4.2: Dependency Readiness Gating
Update service `depends_on` declarations to enforce health conditioning:
```yaml
    depends_on:
      lldap:
        condition: service_healthy
      socket-proxy:
        condition: service_healthy
```

---

## 8. Phase 5: Deployment Truth & Historical Ledger

### Deliverable 5.1: Structured Deployment State Model
Update `~/.local/state/homelab/gitops/<repo>.status` to record complete revision facts:
```json
{
  "target": "snappymail",
  "requested_revision": "9a8b7c6d5e4f3a2b1c0d",
  "deployed_revision": "9a8b7c6d5e4f3a2b1c0d",
  "previous_revision": "1f2e3d4c5b6a7b8c9d0e",
  "status": "success",
  "failure_stage": null,
  "start_time": "2026-09-26T14:30:00Z",
  "end_time": "2026-09-26T14:30:22Z",
  "duration_seconds": 22.4,
  "superseded": false
}
```

### Deliverable 5.2: `appctl` Status & History Subcommand

**Note**: Requires completion of the [appctl refactor](appctl/appctl-engine-v2-refactoring.md).

Expose deployment state directly through CLI:

```bash
appctl history snappymail
appctl status --all
```

---

## 9. Epistemic Verification & Second Brain Documentation

Following Homelab Agent Guidelines:
- Any operational anomalies encountered during the migration must be captured in the Second Brain inbox (`inbox/YYYY-MM-DD-<slug>-debug.md`).
- Upon successful validation of Phase 1 (Mail topology realignment), record an operational snapshot documenting verified certificates, DNS routing, and state migration proof.
