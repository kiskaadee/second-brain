---
type: guide
project: nixos
tags:
  - nixos
  - workstation
  - refactor
  - architecture
  - walkthrough
---

# Walkthrough: Standalone Workstation Architecture & Secrets Decoupling

## Overview

Following the migration of homelab server infrastructure to the dedicated `Core` repository, the primary system configuration repository (`~/Config`) was transformed from a multi-host fleet hierarchy into a standalone, domain-driven configuration for the mobile workstation (`laptop`).

Subsequently, all remaining workstation boundaries, compositor residue, and secrets architecture were refined, verified, and successfully activated on the host.

---

## 1. Secrets Architecture & Clean Decoupling

* **Clarified Roles**: The workstation acts strictly as the **administrative authoring station** for homelab credentials, while the server is a headless **consumer**.
* **Removed Host Secrets Stubs**:
  * Deleted stale root `.sops.yaml`.
  * Removed `sops-nix` flake input from `flake.nix`.
* **Preserved Operator Toolchain**: Retained `sops`, `age`, and `rbw` CLI packages in `home/dev.nix` so secrets in `Core/nixos/secrets.yaml` can continue to be edited and rotated locally.
* **Rewrote Runbook**: Updated `docs/secrets-management.md` with a clear GitOps diagram explaining the author-consumer split and step-by-step instructions for managing `Core` secrets from the laptop.

---

## 2. Compositor Cleanliness (Niri-Native)

* **Removed Hyprland Session Target**: Deleted `systemd.user.targets.hyprland-session` from `home/desktop.nix`.
* **Streamlined Screen Recorder**: Refactored `home/scripts/record.sh` to query Niri directly (`niri msg -j focused-output`) and removed all legacy `hyprctl` checks.

---

## 3. Decoupled Filesystem Paths

* **Eliminated Hard Runtime Path Dependency**:
  * Removed `$HOME/Core/scripts` from `sessionPath` in `home/default.nix`.
  * Removed `$HOME/Core/scripts` from the `PATH` export in `home/shell.nix`.
  * Preserved only standard user binary paths (`$HOME/.local/bin` and `$HOME/.cargo/bin`).

---

## 4. Semantic & Documentation Precision

* **Machine Services & Peripherals**: Updated `system/hardware.nix` header to accurately reflect machine-level daemons (PipeWire, Docker, Bluetooth, power management, printing).
* **Updated Upstream DMS Options**: Removed deprecated `enableSystemMonitoring` and `enableClipboardPaste` from `system/desktop.nix` (now natively built into DMS).
* **Refined Architectural Principles in `architecture.md`**:
  * Clarified that workstation OpenSSH remote access $\neq$ homelab server infrastructure.
  * Refined "Git is the source of truth" to target reproducible configuration decisions, acknowledging runtime state (SSH keys, machine-id, caches).
  * Formally documented the dual-composition model (`flake.nix` composing `system/` and `home/`).
  * Rephrased package placement invariant around execution context.
* **Documentation Path Fixes**:
  * Fixed stale `modules/user/terminal.nix` in `docs/tmux.md`.
  * Fixed stale `modules/user/apps.nix` in `docs/development-environments.md` and `docs/package-and-secrets.md`.

---

## 5. Verification Results

| Validation Command | Status | Details |
| :--- | :--- | :--- |
| `nix flake check` | **PASSED** | Flake inputs, schema, and `laptop` configuration evaluated cleanly. |
| `nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link` | **PASSED** | Complete dry build succeeded, compiling all derivations. |
| `sudo nixos-rebuild switch --flake .#laptop` | **PASSED** | System successfully activated into new generation without regressions. |
