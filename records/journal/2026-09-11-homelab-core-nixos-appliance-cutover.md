---
type: journal
project: homelab
date: 2026-09-11
tags: [homelab, nixos, migration, cutover]
---

# homelab-core NixOS Appliance Merged & Documentation Audit Complete

## Overview
The transformation of `homelab-core` into a turnkey, standalone declarative NixOS appliance is fully complete, validated, merged into `main`, and deployed. All documentation drift across both `homelab-core` and `Config` repositories has been resolved.

## Summary of Completed Actions

### 1. `homelab-core` Repository
- **Merged `feat/nixos-appliance` into `main`** (Fast-forward, pushed to `origin/main`).
- **NixOS Appliance Layer**:
  - `flake.nix`: 2-input flake (`nixpkgs` channel tarball + `sops-nix`).
  - `flake.lock`: Pinned to `nixos-26.11pre1070770.8ce4ef6`.
  - `.sops.yaml`: Scoped to `nixos/secrets.yaml` with server and laptop age keys.
  - `nixos/configuration.nix`: Clean, headless NixOS profile without Home Manager or desktop inheritance.
  - `nixos/modules/homeserver.nix`: Systemd services (`homeserver-core`, `homelab-gitops`), Authelia declarative user config, and secret templates.
  - `nixos/modules/traefik-deployments.nix`: Traefik deployment environment templates (`traefik-deployments.env`).
  - `nixos/modules/dynu.nix`: Smart dynamic IP monitor timer and ddclient credentials.
  - `nixos/modules/shell.nix`: Tailored declarative bash environment via `/etc/bashrc` with `zoxide`, `starship`, `direnv`, `fastfetch`, `fzf`, `bat`, `qpdf`, and server aliases.
- **Documentation Overhaul**:
  - `README.md`: Updated secrets architecture to `nixos/secrets.yaml` and `/run/secrets/rendered/`. Added comprehensive `Declarative NixOS Appliance` section detailing directory layout, rebuild commands, and disaster recovery.
  - `docs/setup_guide.md`: Updated paths from `~/Config/hosts/desktop/` to `nixos/`, updated `sops nixos/secrets.yaml` workflow, and documented module roles.
  - `SECURITY.md`: Removed legacy Arch Linux / `pacman -Syu` references; documented NixOS SSH and declarative immutability guidelines.
  - `AGENTS.md`: Updated secrets location invariant to `nixos/secrets.yaml`.

### 2. `Config` Repository
- **Documentation Streamlining**:
  - `README.md`: Replaced verbose Dynu flowchart and implementation details with a concise feature highlight linking to `docs/dynu-ip-monitor.md`. Updated `record.sh` description to reflect Niri sessions (removed legacy Hyprland reference).
  - `docs/system-maintenance.md`: Fixed remaining `.desktop` build and rebuild commands, replacing them with `.laptop`.
- **Validation**:
  - `nix flake check` passed cleanly.
  - Both `server` and `laptop` configurations evaluate without errors.

## Next Phase (Phase 5)
Once the server running generation has been verified over an extended period, the legacy `hosts/server/` folder and server configurations can be formally deprecated and purged from the `Config` repository.
