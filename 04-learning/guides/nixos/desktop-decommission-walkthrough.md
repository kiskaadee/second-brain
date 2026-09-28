---
type: guide
project: nixos
tags:
  - nixos
  - flake
  - refactor
---

# Walkthrough: Decommissioning the Legacy Desktop Derivation

## Overview
We cleanly decommissioned the legacy `desktop` host configuration (`nixosConfigurations.desktop` and `hosts/desktop/`) on the dedicated branch `refactor/decommission-desktop`. 

With the dedicated `server` host handling all homelab services and `laptop` serving as the daily-driver workstation, the legacy dual-mode `desktop` host is no longer needed.

---

## Changes Made

1. **Branch Isolation**:
   Created and checked out branch `refactor/decommission-desktop` from `main`.

2. **Flake Output Pruning**:
   - `flake.nix`: Removed `nixosConfigurations.desktop`. The only active targets are now `server` and `laptop`.

3. **Directory Deletion**:
   - Removed `hosts/desktop/` and all its legacy contents (Hyprland configuration, duplicated server configs, hardware configuration, and legacy secrets). All active homelab services remain fully preserved under `hosts/server/`.

4. **Architecture & Constitution Alignment**:
   - `architecture.md`: Pruned `desktop` from the topology directory tree, Mermaid diagrams, placement guides, and invariants.
   - `AGENTS.md`: Updated agent constitution, verification commands, and validation matrix to target `server` and `laptop`.
   - `README.md`: Updated high-level overview, topology diagrams, and deployment guides to reflect the 2-host architecture (`server` and `laptop`).
   - `docs/`: Updated references in `dynu-ip-monitor.md`, `package-and-secrets.md`, `secrets-management.md`, and `antigravity.md`.

---

## Verification Results

### 1. Attribute Check
```bash
nix eval .#nixosConfigurations --apply builtins.attrNames
```
- Result: `[ "laptop" "server" ]` (confirming `desktop` is cleanly removed).

### 2. Flake Validation
```bash
nix flake check
```
- Result: **All checks passed cleanly** for `nixosConfigurations.server` and `nixosConfigurations.laptop`.

### 3. Dry-Build Validation (`--no-link`)
- **`server`**:
  ```bash
  nix build .#nixosConfigurations.server.config.system.build.toplevel --no-link
  ```
  Result: **Success (code 0)**.
- **`laptop`**:
  ```bash
  nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link
  ```
  Result: **Success (code 0)**.
