---
type: plan
status: completed
project: nixos
tags:
  - nixos
  - flake
  - cleanup
  - refactor
---

# Implementation Plan: Decommission Legacy Desktop Derivation

## Goal Description

Decommission and remove the legacy `desktop` host configuration (`nixosConfigurations.desktop` and `hosts/desktop/`) from the repository.

Now that homelab services (`homeserver.nix`, `traefik-deployments.nix`, `dynu.nix`, SOPS secrets) have been completely stabilized on the dedicated `server` host, and the active workstation environment is running on `laptop`, the legacy dual-mode `desktop` derivation is obsolete and can be cleanly decommissioned.

---

## User Review Required

> [!IMPORTANT]
> **Branch Isolation**:
> All modifications and deletions will take place on a dedicated branch `refactor/decommission-desktop` branched off `main`, allowing effortless rollback or recovery at any time.

> [!WARNING]
> **Host Scope**:
> Deleting `hosts/desktop/` removes:
> - `hosts/desktop/configuration.nix` & `specialisation.server`
> - `hosts/desktop/hardware-configuration.nix`
> - `hosts/desktop/home.nix` & `hosts/desktop/config/hypr/`
> - Legacy duplicated homelab files (`homeserver.nix`, `traefik-deployments.nix`, `dynu.nix`, `monitor.py`, `secrets.yaml`)
>
> All homelab functionality already exists independently in `hosts/server/`.

---

## Proposed Changes

### 1. Branch Creation
- Create and switch to `refactor/decommission-desktop`.

---

### 2. Flake Configuration

#### [MODIFY] flake.nix
- Remove `nixosConfigurations.desktop` block (lines 95–121).
- Active hosts remaining in `flake.nix`: `server` and `laptop`.

---

### 3. File Deletion

#### [DELETE] hosts/desktop/
- Delete the entire `hosts/desktop/` directory and all its contents:
  - `hosts/desktop/configuration.nix`
  - `hosts/desktop/hardware-configuration.nix`
  - `hosts/desktop/home.nix`
  - `hosts/desktop/config/hypr/`
  - `hosts/desktop/dynu.nix`
  - `hosts/desktop/homeserver.nix`
  - `hosts/desktop/traefik-deployments.nix`
  - `hosts/desktop/monitor.py`
  - `hosts/desktop/secrets.yaml`
  - `hosts/desktop/ddclient.conf`

---

### 4. Architecture & Documentation Sync

#### [MODIFY] architecture.md
- Update topology diagram and description to reflect active hosts: `server` (Homelab) and `laptop` (Workstation).
- Remove references to desktop specialization invariant.

#### [MODIFY] AGENTS.md
- Update validation commands from `desktop` to `server` and `laptop`.
- Update host validation matrix to reflect active hosts.

#### [MODIFY] README.md
- Remove legacy `hosts/desktop/` references from the directory map and documentation.

---

## Verification Plan

### Automated Tests
1. **Flake Check**:
   ```bash
   nix flake check
   ```
   Ensures flake metadata and all remaining host configurations (`server` and `laptop`) evaluate without errors.

2. **Dry-Build System Targets (Build, Never Switch)**:
   ```bash
   nix build .#nixosConfigurations.server.config.system.build.toplevel --no-link
   nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link
   ```
   Both remaining hosts must compile cleanly.

3. **Verify Desktop Derivation Is Removed**:
   ```bash
   nix eval .#nixosConfigurations --apply builtins.attrNames
   ```
   Expected output: `[ "laptop" "server" ]`

### Manual Verification
1. `git status` inspection to ensure no untracked or unwanted deletions occurred.
2. Confirm `git log` and commit history on the dedicated branch.
