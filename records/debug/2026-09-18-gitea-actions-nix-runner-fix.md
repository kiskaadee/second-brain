---
type: debug
project: homelab
date: 2026-09-18
tags:
  - operations
  - homelab
  - troubleshooting
  - gitea
  - nix
  - ci-cd
---

# Remediation: Gitea Actions CI Build Hang on Nix Installation

## Problem Statement
The CI pipeline for `homelab-core` (`validate` job in `.gitea/workflows/ci.yaml`) hung indefinitely (>5 minutes) at the `Install Nix` step (`DeterminateSystems/nix-installer-action@main`), stalling builds on push and pull requests.

## Research & Hypotheses
1. **Runner connectivity/authorization**: Evaluated whether the `act_runner` had lost communication with Gitea or lacked repository access.
2. **Container network/DNS misconfiguration**: Checked if the runner container was unable to resolve external domains like `install.determinate.systems`.
3. **Init system & environment incompatibility**: Investigated whether the action expected a multi-user `systemd` daemon environment or GitHub-specific metadata that is absent in Gitea's containerized `act_runner`.

## Diagnostics & Findings
1. **Runner Daemon & Registration**: Checked `ssh server-local "docker logs --tail 50 gitea-runner"`. Verified that the runner was operational, healthy, and successfully claiming jobs (`task 74/75`).
2. **Step-Level Execution**: Steps `Set up job` and `Check out repository` completed within seconds. The workflow consistently halted inside `DeterminateSystems/nix-installer-action` during binary download and initialization.
3. **Root Cause Confirmed**:
   - Gitea's `act_runner` runs tasks inside non-systemd Docker containers (`ghcr.io/catthehacker/ubuntu:act-latest`).
   - `DeterminateSystems/nix-installer-action` attempts a multi-user installation requiring systemd to manage the Nix daemon socket (`/nix/var/nix/daemon-socket/socket`) and sends telemetry/requests against `${{ github.server_url }}` which in Gitea resolves to `https://gitea.roadtotech.me`.
   - Without systemd and with mismatched API URLs, the installer hung waiting on sockets and timeouts.

## Remediation / Fix
1. **Direct Container Execution**: Replaced the dynamic Ubuntu install step with the native container image `nixos/nix:latest` in [`homelab-core/.gitea/workflows/ci.yaml`](https://gitea.roadtotech.me/kiskaadee/homelab-core/src/branch/main/.gitea/workflows/ci.yaml).
2. **Git & Flake Configuration**: Configured `git config --global --add safe.directory "$GITHUB_WORKSPACE"` and enabled `nix-command flakes` in `~/.config/nix/nix.conf`.
3. **Local Invariant Verification**: Validated the entire pipeline locally via `./scripts/test` and inside a Docker simulation of `nixos/nix:latest`.
4. **GitOps Rollout**: Committed to `fix/ci-nix-runner`, merged to `main`, and pushed to `origin/main` (`ssh://git@gitea.roadtotech.me:2223/kiskaadee/homelab-core`).

## Results & Verification
- Gitea Actions triggered Task `#76` for commit `d43848c`.
- The `validate` job completed successfully in **~16 seconds** (down from timing out at 5+ minutes).
- Flake checks and security invariants executed without socket or permission errors.

## Takeaways & Prevention
- **Avoid Dynamic Toolchain Installation in Containerized CI**: For tools with rich container ecosystems (like Nix), using a pre-baked base image (`container: nixos/nix:latest`) is significantly faster, more deterministic, and avoids init system/PID 1 discrepancies.
- **Always Configure Git Safe Directory in CI Containers**: Containerized runners mounting repository volumes across UID boundaries require `git config --global --add safe.directory "$GITHUB_WORKSPACE"` for Nix flake git operations.
