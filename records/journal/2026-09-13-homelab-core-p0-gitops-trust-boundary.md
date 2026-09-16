---
type: journal
date: 2026-09-13
project: homelab
tags:
  - homelab
  - gitops
  - security
  - architecture
---

# Homelab Core — Milestone P0: GitOps Trust Boundary Implementation

**Plan Reference:** [`projects/homelab/plans/architecture-consolidation-implementation-guide.md`](file:///home/kiskaadee/Brain/projects/homelab/plans/architecture-consolidation-implementation-guide.md)  
**Status:** Completed & Proven (All P0 Deliverables 1.1–1.5 achieved)

---

## 🏛️ Completed Deliverables & Commit Chain

1. **Deliverable 1.1 — Remove Arbitrary `custom` Execution**
   - **Commit:** [`29dd186`](file:///home/kiskaadee/Projects/active/homelab/Core) `refactor(gitops): remove arbitrary custom execution`
   - **Actions:** Removed `shell=True` and `custom:` execution handler from `scripts/gitops_dispatcher.py`. Unsupported actions fail closed.

2. **Deliverable 1.2 — Trusted Repository Resolution**
   - **Commit:** [`01acdb4`](file:///home/kiskaadee/Projects/active/homelab/Core) `feat(gitops): add trusted repository resolution`
   - **Actions:** Implemented `resolve_repository(repo_name)` enforcing canonical path resolution, strict regex naming (`^[a-zA-Z0-9][a-zA-Z0-9._-]*$`), directory traversal rejection (`../../etc`), symlink escape rejection, and allowed root containment (`~/Sites`, `~/Brain`).

3. **Deliverable 1.3 — Webhook Authentication**
   - **Commit:** [`fa8054a`](file:///home/kiskaadee/Projects/active/homelab/Core) `feat(gitops): add webhook authentication`
   - **Actions:** Configured HMAC-SHA256 signature verification (`X-Gitea-Signature`) using constant-time comparison (`hmac.compare_digest`). Generated shared secret encrypted via SOPS/Age in `nixos/secrets.yaml` and projected to `/run/secrets/gitops/webhook_secret` via `homeserver.nix`.

4. **Deliverable 1.4 — Repository, Event, and Branch Admission**
   - **Commit:** [`c265c3e`](file:///home/kiskaadee/Projects/active/homelab/Core) `feat(gitops): enforce repository/event/branch admission`
   - **Actions:** Implemented `admit_deployment()` verifying event type (`push` only), ref structure (`refs/heads/*` only; tags/PRs rejected), trusted repository identity, manifest validity, and target branch matching policy.

5. **Deliverable 1.5 — Serialized Asynchronous Deployment with Superseding**
   - **Commit:** [`5aae4ef`](file:///home/kiskaadee/Projects/active/homelab/Core) `feat(gitops): add serialized asynchronous deployment`
   - **Actions:** Separated HTTP admission from background execution. Incoming webhooks write atomic pending files and return HTTP 200 immediately. Workers acquire non-blocking per-repository `flock` locks, sequentially running deployments and automatically superseding intermediate pending commits (A running, B queued, C replaces B -> A deploys, then C deploys).

6. **Deliverables 3.1, 3.2, 3.6 — Automated Testing & CI Invariants**
   - **Commits:**
     - [`142697a`](file:///home/kiskaadee/Projects/active/homelab/Core) `test(architecture): add structural invariants and test runner`
     - [`f4b676b`](file:///home/kiskaadee/Projects/active/homelab/Core) `test(architecture): add compose and socket proxy security invariants`
     - [`3351466`](file:///home/kiskaadee/Projects/active/homelab/Core) `ci: run architecture and security validation in flake check and gitea actions`
   - **Actions:** Added automated test runner [`scripts/test`](file:///home/kiskaadee/Projects/active/homelab/Core/scripts/test), structural invariant checks (`tests/structural/`), Compose security invariant checks (`tests/security/test_security_invariants.py`), Nix flake check integration (`checks.x86_64-linux.test-suite` in `flake.nix`), and Gitea Actions CI workflow (`.gitea/workflows/ci.yaml`).

7. **Documentation Synchronization**
   - **Commit:** [`534ea9e`](file:///home/kiskaadee/Projects/active/homelab/Core) `docs: sync repository documentation with GitOps hardening and automated test invariants`
   - **Actions:** Synchronized [`README.md`](file:///home/kiskaadee/Projects/active/homelab/Core/README.md) and [`SECURITY.md`](file:///home/kiskaadee/Projects/active/homelab/Core/SECURITY.md) with the hardened GitOps architecture, automated test runner instructions, Docker socket isolation guarantees, and declarative NixOS SOPS checklist.

---

## 🧪 Verification & Invariant Proofs

- **Pytest Suite**: 31 passing tests in 0.09s (`tests/security/`, `tests/structural/`).
- **One-Command Test Runner**: `./scripts/test` (linting + unit tests + Nix flake check).
- **Ruff Code Health**: Zero lint or formatting warnings across the entire repository.
- **NixOS Evaluation & Pure Sandbox Check**: `nix flake check` passing with zero errors.
- **Continuous Integration**: Machine-enforced via Gitea Actions on every push and PR.
