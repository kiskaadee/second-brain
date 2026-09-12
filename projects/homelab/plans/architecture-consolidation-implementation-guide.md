---
type: plan
status: active
project: homelab
tags:
  - homelab
  - architecture
  - gitops
  - security
  - implementation
---

# Homelab Core — Architecture Consolidation & Hardening Implementation Guide

This guide turns the [Architecture Consolidation & Hardening Roadmap v2](architecture-consolidation-roadmap-v2.md) into an executable sequence of work.

The objective is not to introduce new infrastructure. It is to make the existing system's trust boundaries, contracts, deployment behavior, and recovery semantics explicit and machine-enforced.

---

# 0. Working Rules

Before starting the implementation, establish four rules for the entire refactor.

## Rule 1 — One architectural change at a time

Each deliverable should have a small, independently reviewable commit or commit series.

Avoid combining:

- GitOps security changes
- manifest redesign
- NixOS privilege changes
- documentation migration

into one large commit.

---

## Rule 2 — Preserve behavior unless the deliverable explicitly changes it

The refactor should distinguish:

- **security changes**
- **contract changes**
- **behavioral changes**
- **documentation changes**

For example, replacing:

```yaml
actions:
  - git_pull
  - compose_up
```

with:

```yaml
deployment:
  strategy: compose
```

is intentionally a contract change.

Moving a secret declaration between NixOS modules should not change runtime behavior.

---

## Rule 3 — The repository is the source of truth

Before implementing a deliverable, inspect the actual consumers.

Do not assume a field is unused because it is not documented.

For every migration:

```text
producer → parser → consumer → runtime behavior
```

must be identified.

---

## Rule 4 — Every deliverable finishes with a proof

Each implementation should end with at least one reproducible verification command.

Examples:

```bash
python -m pytest
```

```bash
nix flake check
```

```bash
docker compose config -q
```

or:

```bash
git grep ...
```

A completed change should be demonstrably correct, not merely plausible.

---

# 1. P0 — GitOps Trust Boundary

The first objective is to turn GitOps from a remotely triggerable command executor into a constrained deployment admission pipeline.

The current threat chain is:

```text
repository modification
        ↓
app.yaml
        ↓
webhook
        ↓
dispatcher
        ↓
shell execution
        ↓
kiskaadee
        ↓
Docker / sudo
        ↓
host
```

The roadmap explicitly identifies this as the highest-risk vulnerability.

## Deliverable 1.1 — Remove arbitrary `custom` execution

### Step 1 — Inventory current custom consumers

Search every application manifest:

```bash
find ~/Sites -name app.yaml -print0 |
  xargs -0 grep -n "custom:"
```

Also search the Core repository:

```bash
git grep -n "custom"
git grep -n "shell=True"
git grep -n "subprocess.run"
```

Record every existing consumer before changing the dispatcher.

The roadmap already identifies `homelab-magnetflix` as a known consumer.

### Step 2 — Decide the replacement for each consumer

For every `custom` command, classify it:

```text
normal deployment operation
    → built-in deployment behavior

database migration
    → explicit lifecycle mechanism

one-off administrative command
    → manual operator action

unsupported behavior
    → remove
```

Do not create a generic replacement such as:

```yaml
post_deploy:
  command: "..."
```

That simply recreates the vulnerability with a different name.

### Step 3 — Remove `custom` from the dispatcher

Delete the code path that eventually reaches:

```python
subprocess.run(cmd, shell=True, ...)
```

Then make unsupported action values fail closed:

```text
unknown action → deployment rejected
```

### Step 4 — Migrate MagnetFlix

Replace its current custom migration mechanism with the explicitly approved mechanism chosen above.

Deploy MagnetFlix manually once to prove the replacement works.

### Step 5 — Add a regression test

Create a test proving that a manifest containing:

```yaml
custom: "..."
```

cannot result in command execution.

### Exit condition

The following must be true:

```bash
git grep -n "shell=True" scripts/gitops_dispatcher.py
```

returns nothing relevant, and no manifest can provide arbitrary shell input.

---

# 2. Deliverable 1.2 — Trusted Repository Resolution

The webhook payload must identify a repository by **logical identity**, not by filesystem path. Core resolves that identity locally.

## Step 1 — Define the trusted mapping

Decide what constitutes the canonical repository identity.

For example:

```text
homelab-docs
homelab-gitea
homelab-magnetflix
```

Map those identities to known directories under:

```text
/home/kiskaadee/Sites/
```

The important property is:

```text
payload → name → trusted mapping → local path
```

never:

```text
payload → path
```

## Step 2 — Implement one resolver

Create one function responsible for:

```python
resolve_repository(name) -> trusted repository
```

Every deployment must use it.

Do not allow callers to construct paths independently.

## Step 3 — Canonicalize the resolved path

After resolution:

```python
realpath(target)
```

must still be checked against the allowed root.

This remains defense in depth rather than the primary trust mechanism.

## Step 4 — Test traversal and ambiguity

Reject:

```text
../../foo
/home/foo
/etc
symlink escapes
unknown repositories
```

Test both malicious and valid names.

### Exit condition

A webhook can select only repositories explicitly recognized by Core.

---

# 3. Deliverable 1.3 — Webhook Authentication

The roadmap specifies HMAC-SHA256 using `X-Gitea-Signature`, with the secret stored via SOPS and projected through `/run/secrets/`.

## Step 1 — Obtain the exact incoming request representation

Before implementing verification, establish exactly what bytes the signature covers:

```text
HTTP body
```

Do not verify a reconstructed or parsed JSON object.

Signature verification must operate on the original request body.

## Step 2 — Store the webhook secret

Add a dedicated secret to SOPS.

Do not place it in:

```text
app.yaml
docker-compose.yml
gitops_dispatcher.py
```

Project it to the service at runtime.

## Step 3 — Implement verification

Verification should:

1. read the raw body
2. read the signature header
3. calculate HMAC-SHA256
4. compare using a constant-time comparison
5. reject invalid requests before deployment

Conceptually:

```text
request
   ↓
read raw body
   ↓
calculate HMAC
   ↓
constant-time compare
   ↓
valid → continue
invalid → reject
```

## Step 4 — Reject missing signatures

These are failures:

```text
no signature
malformed signature
wrong signature
empty secret
```

There should be no anonymous fallback.

## Step 5 — Test

Create tests for:

```text
valid signature
invalid signature
missing signature
modified body
modified signature
```

### Exit condition

No unauthenticated request can reach deployment admission.

---

# 4. Deliverable 1.4 — Repository, Event, and Branch Admission

Authentication answers:

> Who sent this?

It does not answer:

> Should this request be deployed?

The admission layer must validate the repository, event/ref, and branch policy before execution.

## Step 1 — Define accepted event semantics

Document which webhook events are deployable.

For example:

```text
push → eligible
pull_request → rejected
tag → rejected unless explicitly supported
```

Use the actual webhook payload structure rather than assuming every event is equivalent.

## Step 2 — Validate repository identity

Verify:

```text
payload repository
        ↓
trusted repository mapping
```

Reject unknown repositories.

## Step 3 — Validate the branch

Determine the branch from the manifest:

```yaml
deployment:
  branch: main
```

with:

```text
default = main
```

Then require the incoming ref to match the declared policy.

## Step 4 — Validate manifest before execution

The manifest must be parsed and validated before Git or Docker actions occur.

The roadmap explicitly places manifest validation inside the admission pipeline.

### Exit condition

An authenticated request still gets rejected if:

```text
wrong repository
wrong event
wrong branch
invalid manifest
unsupported strategy
```

---

# 5. Deliverable 1.5 — Serialized Deployment

The desired behavior is:

```text
A arrives → deploy A
B arrives → queue B
C arrives → replace B
A finishes → deploy C
```

rather than attempting every intermediate revision.

## Step 1 — Identify deployment targets

Serialization should be per application/repository.

Two unrelated applications should be able to deploy independently.

## Step 2 — Choose filesystem-level synchronization

Use a simple mechanism such as:

```text
flock
```

or a systemd-managed worker.

Do not add Redis, RabbitMQ, or another message broker.

## Step 3 — Separate admission from execution

The HTTP request should not perform:

```text
git pull
docker compose pull
docker compose up
```

Instead:

```text
HTTP request
    ↓
validate
    ↓
enqueue latest desired revision
    ↓
return
```

Then:

```text
worker
    ↓
take target
    ↓
deploy
```

This directly addresses the roadmap's asynchronous-dispatch requirement.

## Step 4 — Implement superseding

Maintain at most:

```text
one active deployment
one pending deployment
```

When a newer valid request arrives:

```text
pending old revision → replaced
pending new revision → retained
```

## Step 5 — Test race behavior

Simulate:

```text
A starts
B arrives
C arrives
A finishes
```

and verify that:

```text
B is skipped
C is deployed
```

### P0 exit condition

The complete flow is now:

```text
webhook
   ↓
cryptographic verification
   ↓
repository admission
   ↓
event/ref admission
   ↓
manifest validation
   ↓
deployment scheduling
   ↓
serialized executor
   ↓
closed deployment strategy
```

This is the first major milestone.

---

# 6. P1 — Manifest Contract v1

The manifest currently functions as an informal configuration format. The goal is to turn it into a strict API contract.

Do this only after the P0 trust boundary is established.

---

## Deliverable 2.1 — Write the Manifest Specification First

Do not begin by writing JSON Schema.

Begin with a human specification.

Create:

```text
docs/architecture/manifest-specification.md
```

Define:

### Required fields

For example:

```yaml
schemaVersion
name
domain
```

### Optional fields

For example:

```yaml
title
description
aliases
visible
auth
networks
env
deployment
homepage
```

### Types

Explicitly define:

```text
name → string
aliases → array[string]
visible → boolean
networks → array[string]
env → mapping[string,string]
```

### Defaults

Document defaults explicitly.

### Allowed values

For example:

```yaml
deployment.strategy:
  compose
```

### Cross-field constraints

Examples:

```text
auth=true may require the proxy network
deployment.strategy must be supported
domain must be unique
name must be unique
```

### Security constraints

Explicitly prohibit:

```text
arbitrary commands
filesystem paths
Docker socket access
privileged deployment directives
```

The manifest must describe application intent, not host capabilities.

---

# 7. Deliverable 2.2 — Create JSON Schema v1

Create:

```text
schemas/app-v1.schema.json
```

Start from the written specification.

Include:

```text
$schema
$id
title
type
required
properties
additionalProperties
```

Prefer rejecting unknown fields rather than silently accepting them.

The roadmap deliberately makes JSON Schema the normative external contract and Pydantic the runtime enforcement mechanism.

## Step-by-step

1. encode primitive types
2. encode required fields
3. encode defaults
4. encode enumerations
5. encode nested objects
6. add security restrictions
7. add cross-field constraints where supported
8. write valid examples
9. write invalid examples

Create fixtures such as:

```text
tests/fixtures/manifests/valid/
tests/fixtures/manifests/invalid/
```

---

# 8. Deliverable 2.3 — Introduce `schemaVersion`

Every application manifest becomes:

```yaml
schemaVersion: 1
```

Core must reject:

```yaml
schemaVersion: 2
```

and missing `schemaVersion` unless a future compatibility policy explicitly says otherwise.

This prevents silent interpretation changes.

---

# 9. Deliverable 2.4 — Replace Imperative Deployment Actions

Current:

```yaml
deployment:
  branch: main
  actions:
    - git_pull
    - compose_up
```

Target:

```yaml
deployment:
  strategy: compose
  branch: main
  verify: healthcheck
```

The important principle is:

```text
application declares intent
            ↓
Core owns execution
```

not:

```text
application tells Core which commands to run
```

The roadmap explicitly adopts this intent-over-imperative model.

## Migration procedure

For each application:

1. inspect current actions
2. determine the intended strategy
3. convert to `deployment.strategy`
4. remove `actions`
5. validate
6. deploy manually
7. confirm equivalent behavior
8. commit migration

---

# 10. Deliverable 2.5 — Replace the Custom YAML Parser

The existing parser should stop being the source of truth.

Choose a real YAML parser compatible with the project constraints.

Then construct a typed model representing the v1 manifest.

The runtime flow becomes:

```text
app.yaml
   ↓
YAML parser
   ↓
Pydantic model
   ↓
validated manifest object
   ↓
appctl / GitOps
```

Do not let every consumer parse YAML independently.

---

# 11. Deliverable 2.6 — Desired State vs Observed State

Make the distinction explicit.

```text
app.yaml
    ↓
desired state
```

while:

```text
Git / Docker / TLS / container health
    ↓
observed state
```

`appctl` reconciles and presents the two rather than storing observed runtime facts in `app.yaml`.

## Practical test

Ask of every field:

> Could this value be determined from runtime inspection instead?

If yes, it probably does not belong in the manifest.

---

# 12. Deliverable 2.7 — Preflight Validation

Both consumers must use the same validation layer:

```text
appctl
GitOps dispatcher
```

Create one reusable validation interface.

For example:

```text
load_manifest(path)
validate_manifest(manifest)
```

The CLI and dispatcher should not implement different validation rules.

### Exit condition

Every application manifest in `~/Sites` is:

```text
schemaVersion: 1
valid
intent-based
strictly parsed
```

---

# 13. P1 — Architecture Invariant Tests

The objective here is to convert `AGENTS.md` architectural rules into executable constraints. The roadmap defines five categories.

Create:

```text
tests/
├── structural/
├── security/
├── manifests/
├── operational/
└── documentation/
```

---

# 14. Deliverable 3.1 — Structural Tests

Verify `nixos/`, `scripts/`, `docs/`, `docker-compose.yml`, `flake.nix`, `AGENTS.md`, `UNLICENSE` exist.

Also reject deprecated structures such as `infra/core/`, `./up.sh`, `./down.sh`.

The test should inspect the filesystem rather than relying on documentation claims.

---

# 15. Deliverable 3.2 — Security Tests

Create assertions for:

```text
no direct docker.sock mounts
socket-proxy POST=0
socket-proxy DELETE=0
no privileged containers
no forbidden host paths
no shell=True in GitOps
```

Where possible, parse Compose/YAML rather than using fragile grep-only checks.

---

# 16. Deliverable 3.3 — Manifest Tests

Scan every `~/Sites/*/app.yaml` and validate:

```text
schemaVersion
schema validity
unique names
unique domains
allowed networks
allowed deployment strategies
```

This creates a repository-wide contract test rather than validating only the application currently being deployed.

---

# 17. Deliverable 3.4 — Operational Tests

Run:

```bash
docker compose config -q   # for Core
nix flake check             # for NixOS configuration
```

Then run equivalent Compose validation for each application stack.

---

# 18. Deliverable 3.5 — Documentation Tests

Build simple checks that identify commands, paths, and deprecated paths referenced in docs.

Focus on known failure modes rather than building a natural-language parser.

The immediate reason for this is existing documentation drift.

---

# 19. Deliverable 3.6 — CI Integration

Add a Gitea Actions workflow.

On every Core change, run at minimum:

```text
structural
security
manifest
```

The desired property is:

```text
architectural regression → CI failure
```

---

# 20. P1 — Privilege Boundary

After arbitrary command execution is removed, reduce the remaining GitOps authority.

The roadmap proposes a dedicated Unix user and systemd hardening.

---

# 21. Deliverable 4.1 — Create the `gitops` User

Add a dedicated NixOS user `gitops` with only the permissions necessary for deployment. No `wheel`. Docker access only.

---

# 22. Deliverable 4.2 — Move GitOps Runtime to `gitops`

Change `User=kiskaadee` to the dedicated identity.

Then inspect every dependency: Sites permissions, Docker permissions, secret access, configuration files, working directory, logs, temporary files.

Do not assume the service will continue working simply because the user belongs to `docker`.

---

# 23. Deliverable 4.3 — Apply systemd Hardening

Apply the planned directives:

```text
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=...
PrivateTmp=yes
NoNewPrivileges=yes
CapabilityBoundingSet=
```

After each restriction:

```bash
sudo systemctl daemon-reload
sudo systemctl restart homelab-gitops
journalctl -u homelab-gitops
```

This incremental process is important because systemd hardening often exposes previously implicit filesystem assumptions.

---

# 24. Deliverable 4.4 — Prove the New Boundary

Perform an explicit capability review:

```text
Can GitOps write outside Sites?
Can GitOps access unrelated secrets?
Can GitOps invoke sudo?
Can GitOps modify NixOS?
Can GitOps execute arbitrary shell?
Can GitOps access the Docker daemon?
```

The goal is not merely "It runs." The goal is "Its authority is intentionally bounded."

---

# 25. P2 — Architecture Documentation

Do this after P0/P1 behavior has stabilized.

The documentation tree proposed by the roadmap is:

```text
docs/
├── architecture/
│   ├── system-topology.md
│   ├── ownership-matrix.md
│   ├── gitops-protocol-v1.md
│   └── manifest-specification.md
├── security/
│   ├── trust-model.md
│   ├── secret-management.md
│   └── socket-proxy-policy.md
├── operations/
│   ├── nixos-management.md
│   └── disaster-recovery.md
├── adr/
└── archive/
```

Principle: `docs/` = current truth; `docs/archive/` = historical truth.

---

# 26–34. Documentation Deliverables (5.1–5.9)

Create each document after the implementation it describes is stable:

- **5.1** `docs/architecture/system-topology.md` — three-layer diagram (use the approved Mermaid flowchart from the roadmap), orchestration as cross-cutting
- **5.2** `docs/architecture/ownership-matrix.md` — owns / must not own per layer
- **5.3** `docs/architecture/gitops-protocol-v1.md` — webhook format, auth, resolution, branch policy, serialization, failure semantics
- **5.4** `docs/architecture/manifest-specification.md` — human-readable companion to JSON Schema
- **5.5** `docs/security/trust-model.md` — full trust chain and component authority
- **5.6** `docs/security/secret-management.md` — SOPS lifecycle, projection, ownership vs. consumption
- **5.7** `docs/operations/disaster-recovery.md` — split declarative recovery vs. state recovery
- **5.8** Historical migration — ADRs to `docs/adr/`, obsolete docs to `docs/archive/`
- **5.9** Audit active docs — correct ports, paths, commands, TLS/Watchtower/DDNS claims

---

# 35. P3 — Deployment Verification

## Deliverable 6.1 — Preflight Validation

Before changing runtime state, run schema validation, branch validation, and `docker compose config -q`.

## Deliverable 6.2 — Implement Deployment Lifecycle

Standardize the sequence:

```text
capture current revision → fetch target → validate manifest
    → validate Compose → pull images → compose up → verify → record result
```

Keep execution deterministic. Do not allow manifests to change the sequence arbitrarily.

## Deliverable 6.3 — Health Verification

Implement container state + health status checks. Optionally HTTP probe when a domain is declared.

A health verification failure should not automatically imply rollback in v1.

## Deliverable 6.4 — Explicit Failure Semantics

```text
Preflight failure  → reject + log reason
Git failure        → FAILED, stop
Compose failure    → FAILED, stop
Health failure     → DEGRADED, log warning
```

No automatic rollback in v1.

## Deliverable 6.5 — Structured Deployment Logging

Produce JSON logs with: `repository`, `revision`, `stage`, `timestamp`, `result`, `error`.

---

# 36. P4 — Deployment State & Observability

## Deliverable 7.1 — Define Deployment Record Schema

```json
{
  "id": "deploy-docs-20260912-001422",
  "repository": "homelab-docs",
  "commit": "9ac3f7b2",
  "previous_commit": "87b2e1a4",
  "branch": "main",
  "timestamp": "2026-09-12T00:14:22-05:00",
  "duration_seconds": 22,
  "result": "SUCCESS",
  "failure_reason": null,
  "triggered_by": "webhook"
}
```

## Deliverable 7.2 — Implement Append-Only Storage

Use JSON Lines. One record per line. Decide per-repo file vs. global log based on querying needs.

## Deliverable 7.3 — Track Previous Revision

Capture previous commit at deployment time for rollback context.

## Deliverable 7.4 — Add `appctl deployment`

```bash
appctl deployment <app>
```

Shows last and previous deployment: commit, time, duration, result.

---

# 46. Final Integration Pass

After all deliverables are implemented, confirm the five acceptance questions from the roadmap can be answered from the repository alone:

1. What does **NixOS** own?
2. What does **Core** own?
3. What does an **application repository** own?
4. What can **GitOps** execute?
5. What happens **when deployment fails**?

---

# Suggested Commit Sequence

```text
1. refactor(gitops): remove arbitrary custom execution
2. feat(gitops): add trusted repository resolution
3. feat(gitops): add webhook authentication
4. feat(gitops): enforce repository/event/branch admission
5. feat(gitops): add serialized asynchronous deployment
6. migrate(apps): convert custom deployment consumers

7. docs(manifest): define app.yaml v1 specification
8. feat(manifest): add JSON Schema v1
9. feat(manifest): add typed runtime validation
10. migrate(apps): add schemaVersion and intent-based deployment

11. test(architecture): add structural invariants
12. test(architecture): add security invariants
13. test(manifests): add manifest invariants
14. test(architecture): add operational invariants
15. test(docs): add documentation invariants
16. ci: run architecture validation in Gitea Actions

17. feat(security): create dedicated gitops user
18. harden(systemd): restrict GitOps service

19. docs(architecture): add system topology
20. docs(architecture): add ownership matrix
21. docs(gitops): document protocol v1
22. docs(manifest): add specification reference
23. docs(security): document trust and secrets
24. docs(operations): document recovery
25. docs: archive historical material

26. feat(gitops): add deployment preflight
27. feat(gitops): add deployment verification
28. feat(gitops): define failure semantics

29. feat(gitops): add deployment records
30. feat(appctl): add deployment history
```

---

# Definition of Done

The consolidation is complete when:

```text
[ ] GitOps cannot execute arbitrary repository-supplied shell
[ ] webhook requests are authenticated
[ ] repositories are resolved through trusted identity
[ ] branch/event policy is enforced
[ ] deployment execution is asynchronous and serialized
[ ] app.yaml v1 is formally specified
[ ] JSON Schema is normative
[ ] runtime validation is typed
[ ] all manifests use schemaVersion
[ ] deployment configuration expresses intent
[ ] architectural invariants are tested automatically
[ ] CI enforces those invariants
[ ] GitOps runs under a restricted identity
[ ] systemd limits GitOps filesystem authority
[ ] current architecture is documented
[ ] historical documentation is separated
[ ] deployment preflight exists
[ ] deployment health is verified
[ ] failure semantics are explicit
[ ] deployment history is persisted
[ ] appctl can report deployment history
```

The resulting system should be **more constrained than the current one, not merely more documented**. Its architecture should be understandable from the repository, while its most important boundaries are enforced even when a future contributor does not remember them.
