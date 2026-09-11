---
type: guide
project: nixos
tags:
  - nixos
  - flake
  - tarball
  - hydra
---

# Walkthrough: Transitioning to Official `channels.nixos.org` Channel Tarballs

## Overview
We created an isolated branch `feat/channel-tarball-nixpkgs` to transition `nixpkgs` flake inputs from GitHub (`github:nixos/nixpkgs/nixos-unstable`) to the official project-hosted, zstd-compressed channel tarballs (`https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst`).

This change provides:
- **~20–33% smaller download sizes** via Zstandard (`.tar.zst`) compression.
- **Forge independence** from GitHub for the core Nixpkgs repository.
- **Immunity from GitHub API rate-limiting**.
- **System flake registry pinning** (`nix.registry.nixpkgs.flake = inputs.nixpkgs;`) so ad-hoc CLI commands (`nix run nixpkgs#...`) reuse the evaluated channel snapshot without external GitHub lookups.

---

## Changes Made

1. **Dedicated Branch**:
   Created and checked out `feat/channel-tarball-nixpkgs` from `main` to ensure effortless rollback.

2. **System Flake Input**:
   - `flake.nix`: Changed `nixpkgs.url` to `"https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst"`.

3. **Flake Registry Integration**:
   - `modules/system/base.nix`: Added `inputs` to module arguments and configured `nix.registry.nixpkgs.flake = inputs.nixpkgs;`.

4. **Flake Lockfile**:
   - `flake.lock`: Updated the `nixpkgs` input node from type `github` to type `tarball` (`https://releases.nixos.org/nixos/unstable/nixos-26.11pre1070770.8ce4ef6cb6f8/nixexprs.tar.zst`). No other input nodes were disturbed.

5. **Documentation & Dev Flake Examples**:
   - `docs/development-environments.md`: Updated `devShell` example to recommend `https://channels.nixos.org/nixpkgs-unstable/nixexprs.tar.zst`.
   - `docs/antigravity.md`: Updated example snippet to use the channel tarball.

---

## Verification Results

### 1. Flake Checks
```bash
nix flake check
```
- Evaluated outputs for `nixosConfigurations.server`, `nixosConfigurations.desktop`, and `nixosConfigurations.laptop`.
- Result: **All checks passed cleanly**.

### 2. Dry-Build Validation (`--no-link`)
In accordance with repository invariants (**Build, Never Switch**), all three downstream host configurations were compiled dryly without mutating the running system:
- **`desktop`**:
  ```bash
  nix build .#nixosConfigurations.desktop.config.system.build.toplevel --no-link
  ```
  Result: **Success** (`/nix/store/ijg6vq9q7by98dfs1vs2vkzlcmrdjgg7-nixos-system-desktop-26.11.20260910.8ce4ef6.drv`).
- **`laptop`**:
  ```bash
  nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link
  ```
  Result: **Success** (`/nix/store/x0jgx8hghmjbi0pd3cfs7qdc1p0k015b-nixos-system-laptop-26.11.20260910.8ce4ef6.drv`).
- **`server`**:
  ```bash
  nix build .#nixosConfigurations.server.config.system.build.toplevel --no-link
  ```
  Result: **Success** (`/nix/store/kcbi75d4laqywwir3hvggwqngw33dvwm-nixos-system-server-26.11.20260910.8ce4ef6.drv`).
