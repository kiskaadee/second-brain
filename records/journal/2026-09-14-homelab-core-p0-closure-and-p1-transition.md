---
type: journal
date: 2026-09-14
project: homelab
tags:
  - homelab
  - gitops
  - security
  - architecture
---

# Homelab Core — Milestone P0: Final Closure and P1 Transition

**Plan Reference:** [`projects/homelab/plans/architecture-consolidation-implementation-guide.md`](file:///home/kiskaadee/Brain/projects/homelab/plans/architecture-consolidation-implementation-guide.md)  
**Status:** 🔒 100% SEALED & FROZEN (All P0 Deliverables 1.1–1.5 fully hardened and closed)  
**Latest Commits:** [`f8cbe08`](file:///home/kiskaadee/Projects/homelab/Core) & [`4c9e7a4`](file:///home/kiskaadee/Projects/homelab/Core)

---

## 🛡️ Resolution of Reviewer Feedback & Final P0 Hardening

Following architectural review of Milestone P0 (GitOps Trust Boundary), two execution-path considerations were addressed:

1. **Temporal Boundary: Revision-Consistent Manifest Validation**
   - **Problem:** Manifest validation performed strictly during the admission phase examined the working tree at admission time (`HEAD-A`), while background deployment executes after a `git pull` updates the working tree to the target revision (`HEAD-B`). If an untrusted commit updated `app.yaml` with unsupported strategies or changed branch policies, the pre-pull check would have missed it.
   - **Fix:** In [`scripts/gitops_dispatcher.py`](file:///home/kiskaadee/Projects/homelab/Core/scripts/gitops_dispatcher.py), the worker re-reads and re-validates `app.yaml` immediately after `git pull` updates the working directory. If the pulled manifest contains unsupported actions or invalid branch constraints, deployment fails closed before any commands execute. Validated actions from the pulled revision are adopted for execution.
   - **Coverage:** Added automated tests verifying rejection of unsupported actions and policy mismatches introduced post-pull, and adoption of valid updated actions.

2. **Observable Worker Execution State**
   - **Implementation:** Added atomic status persistence writing to `~/.local/state/homelab/gitops/<target>.status.json` containing target, branch, commit SHA, success status, and UTC timestamp.

3. **HMAC Signature Specification**
   - **Documentation:** Explicitly documented signature headers and formats: `X-Gitea-Signature` uses a bare 64-character hex digest, while `X-Hub-Signature-256` uses the `sha256=<hex>` format.

---

## 🧪 Test Suite & Invariant Status

- **Automated Tests:** 35 passing tests (expanded from 31 to 35).
- **Tooling Verification:**
  - `./scripts/test` passes cleanly (Ruff linting + Pytest suite + Pure Nix sandbox check).
  - `nix flake check` passes without warnings or failures.
  - Gitea Actions CI workflow configured for automated PR/push enforcement.

---

## 📋 P0 Commit Summary

- [`29dd186`](file:///home/kiskaadee/Projects/homelab/Core) `refactor(gitops): remove arbitrary custom execution`
- [`01acdb4`](file:///home/kiskaadee/Projects/homelab/Core) `feat(gitops): add trusted repository resolution`
- [`fa8054a`](file:///home/kiskaadee/Projects/homelab/Core) `feat(gitops): add webhook authentication`
- [`c265c3e`](file:///home/kiskaadee/Projects/homelab/Core) `feat(gitops): enforce repository/event/branch admission`
- [`5aae4ef`](file:///home/kiskaadee/Projects/homelab/Core) `feat(gitops): add serialized asynchronous deployment`
- [`142697a`](file:///home/kiskaadee/Projects/homelab/Core) `test(architecture): add structural invariants and test runner`
- [`f4b676b`](file:///home/kiskaadee/Projects/homelab/Core) `test(architecture): add compose and socket proxy security invariants`
- [`3351466`](file:///home/kiskaadee/Projects/homelab/Core) `ci: run architecture and security validation in flake check and gitea actions`
- [`534ea9e`](file:///home/kiskaadee/Projects/homelab/Core) `docs: sync repository documentation with GitOps hardening and automated test invariants`
- [`f8cbe08`](file:///home/kiskaadee/Projects/homelab/Core) `fix(gitops): enforce revision-consistent manifest validation and worker status observation`
- [`4c9e7a4`](file:///home/kiskaadee/Projects/homelab/Core) `docs: document revision-consistent manifest validation and worker status observation`

---

## 🎯 Next Milestone: P1 Manifest Contract v1

With Milestone P0 sealed, work transitions to Milestone P1:
- **Deliverable 2.1:** Repository identity authority & strict alias collision rejection (centralized registry vs self-derived names).
- **Deliverable 2.2–2.5:** Author `docs/architecture/manifest-specification.md` and JSON schema v1 for `app.yaml`.
- **Phase 4:** Dedicated `gitops` system user and systemd confinement.
