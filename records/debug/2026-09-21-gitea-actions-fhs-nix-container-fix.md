---
type: debug
project: homelab
date: 2026-09-21
tags:
  - operations
  - homelab
  - troubleshooting
  - gitea
  - nix
  - ci-cd
  - docker
---

# Remediation: Gitea Actions Nix Container FHS and Entrypoint Failure

## Problem Statement
After switching the `validate` CI job in `homelab-core` to run inside a container (`nixos/nix:latest`), Gitea Actions workflows consistently failed during the container setup step:
```text
failed to start container: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "/bin/sleep": stat /bin/sleep: no such file or directory
```

## Research & Hypotheses
1. **Act Runner Entrypoint Invariant**: Gitea's `act_runner` (based on `nektos/act`) initiates job containers with `entrypoint: ["/bin/sleep", "10800"]` to keep the background container process alive while executing subsequent step commands via `docker exec`.
2. **Non-FHS NixOS Container Layout**: The official `nixos/nix` container image provides a minimal Nix store environment where standard utilities reside in `/root/.nix-profile/bin/` rather than `/bin/` or `/usr/bin/` (only `/bin/sh` and `/usr/bin/env` are symlinked), resulting in `stat /bin/sleep: no such file or directory`.
3. **Step Runtime Requirements**: Actions steps like `actions/checkout@v4` are JavaScript actions executed via `node` within the container context, requiring a Node.js runtime and standard POSIX tools. In addition, single-user Nix inside unprivileged containers requires `build-users-group =` to evaluate derivations without missing `nixbld` group errors.

## Diagnostics & Findings
1. **Container Path Inspection**:
   - `docker run --rm --entrypoint /bin/sh nixos/nix:latest -c "ls -la /bin /usr/bin"` confirmed that `/bin/sleep` is absent in `nixos/nix:latest`.
2. **Runner Log Analysis**:
   - Task `#87` and `#88` aborted immediately at container spawn due to missing `/bin/sleep`.
   - Task `#89` tested with `nixery.dev/shell/coreutils/git/nix:latest` resolved the container start issue, but failed in `actions/checkout` with `exec: "node": executable file not found in $PATH`.
   - Flake checks inside the container threw `error: the group 'nixbld' specified in 'build-users-group' does not exist` when `build-users-group` was unset.

## Remediation / Fix
1. **FHS-Compliant Pre-Baked Toolchain Container**:
   Updated `.gitea/workflows/ci.yaml` to use `nixery.dev/shell/coreutils/git/nix/nodejs:latest`. This provides standard `/bin/sleep`, `git`, `bash`, `nix`, and `node` binaries in standard FHS paths.
2. **Nix Flake & Single-User Runner Configuration**:
   Configured `nix.conf` with both flake flags and single-user build group bypass:
   ```yaml
   - name: Configure Git Safe Directory & Nix Flakes
     run: |
       git config --global --add safe.directory "$GITHUB_WORKSPACE"
       mkdir -p ~/.config/nix
       echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
       echo "build-users-group =" >> ~/.config/nix/nix.conf
   ```
3. **Documentation & Agent Guidelines**:
   Updated [`Core/docs/gitops.md`](file:///home/kiskaadee/Homelab/Core/docs/gitops.md) and [`Homelab/AGENTS.md`](file:///home/kiskaadee/Homelab/AGENTS.md) to document the `act_runner` FHS and entrypoint requirements.
4. **Local and Server Verification**:
   Pre-pulled the image to `server-local`, ran local `./scripts/test`, and pushed commit `dc02893` to `origin/main`.

## Results & Verification
- Gitea Actions spawned task `#90` on `homelab-runner`.
- Container `GITEA-ACTIONS-TASK-90-...` initialized cleanly with `/bin/sleep`.
- `actions/checkout@v4` executed with Node.js and checked out the repository.
- `nix flake check` evaluated all 35 tests, NixOS server flake definitions, and architecture invariants cleanly.
- Job succeeded with exit code 0 (`🏁 Job succeeded`).

## Takeaways & Prevention
- **Act Runner Expects FHS Binaries**: Any container specified under `container: { image: ... }` in Gitea Actions / `act_runner` must include `/bin/sleep`, `sh`, and `node` (if running JS-based GitHub/Gitea actions).
- **Use Nixery for Composable CI Toolchains**: `nixery.dev/shell/coreutils/git/nix/nodejs` provides an ad-hoc, declarative container image that satisfies both FHS runner requirements and hermetic Nix flake toolchains without maintaining separate custom Dockerfiles.
- **Set `build-users-group =` in Single-User Containers**: Without the nix-daemon and `nixbld` system group, containerized Nix builds require an empty `build-users-group` in `nix.conf`.
