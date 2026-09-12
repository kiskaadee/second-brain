---
type: discussion
project: homelab
date: 2026-09-11
tags: [nixos, homelab, architecture, inventory]
---

# Migration Blueprint: Splitting `nixos-config` and `homelab-core`

## Executive Summary

Transferring the server's NixOS configuration directly into `homelab-core` leaves `nixos-config` as a pure, focused workstation and dotfiles repository, while `homelab-core` becomes a completely self-contained NixOS appliance running both the operating system and containerized homelab services.

---

## 1. What Migrates to `homelab-core` (The Server Repository)

Everything that defines, secures, or automates the homelab server moves to `homelab-core`:

| Component | Files to Migrate | Purpose in `homelab-core` |
| :--- | :--- | :--- |
| **Flake Entrypoint** | *New dedicated `flake.nix`* | A clean flake with only `nixpkgs` and `sops-nix`. (No Home Manager, no Wayland/desktop inputs). |
| **System & Hardware** | `hosts/server/configuration.nix`<br>`hosts/server/hardware-configuration.nix` | Base OS, EFI bootloader, Docker daemon, user accounts, SSH keys. |
| **Homelab Services** | `hosts/server/homeserver.nix`<br>`hosts/server/traefik-deployments.nix` | Authelia, Docker service lifecycles, Traefik edge proxy secrets. |
| **Smart DDNS** | `hosts/server/dynu.nix`<br>`hosts/server/monitor.py`<br>`hosts/server/ddclient.conf` | Dedicated Dynamic DNS monitor daemon and timers. |
| **Secrets & Keys** | `hosts/server/secrets.yaml`<br>*.sops.yaml (server-scoped)* | Authelia hashes, Dynu passwords, and GitOps tokens encrypted with server's age key. |

### Major Benefit on the Server Side:
- **No Home Manager overhead**: The server can drop Home Manager entirely. Pure NixOS options like `programs.tmux.enable = true;` and `programs.neovim.enable = true;` provide instant, reliable editor and terminal multiplexing.
- **No more `lib.mkForce false`**: The server no longer imports `modules/system/base.nix` (which had printing, bluetooth, and audio), eliminating the need to force-disable them.

---

## 2. What Remains in `nixos-config` (The Workstation Repository)

This repository becomes 100% focused on being the personal workstation environment:

| Component | Files Remaining | Purpose in `nixos-config` |
| :--- | :--- | :--- |
| **Flake Entrypoint** | `flake.nix` (with `laptop` only) | Flake inputs for desktop UI: `nixpkgs`, `home-manager`, `dms`, `dank-greeter`, `zen-browser`, `antigravity`. |
| **Workstation Host** | `hosts/laptop/*` | Niri window manager, laptop hardware settings, display configs. |
| **Workstation System Modules** | `modules/system/base.nix`<br>`modules/system/graphical.nix` | Bluetooth, PipeWire audio, Epson printing & scanning, greetd, desktop session variables. |
| **Rich User Environment** | `home.nix`<br>`modules/user/*` | Full Lua Neovim (treesitter, LSP), styled Tmux, Starship prompt, Alacritty, desktop Wayland tools. |
| **Developer Toolchains** | `modules/user/apps.nix` | Rust, Go, Python/uv, Zen Browser, Antigravity, Tea, GitHub CLI. |
| **Workstation Scripts** | `modules/user/shell/*`<br>`modules/user/scripts/*` | Interactive scripts: `git.sh`, `todo.sh`, `jump.sh`, `record.sh`, `bundle_project.py`. |
| **Workstation Secrets** | `hosts/laptop/secrets.yaml` | Workstation-specific secrets only. |

---

## 3. What Gets Purged / Cleaned Up

1. **Purged from `nixos-config`**:
   - `hosts/server/` directory (all 9 files).
   - `server` age key from `.sops.yaml`.
   - `nixosConfigurations.server` block from `flake.nix`.
2. **Simplified on the Server (`homelab-core`)**:
   - Flake evaluation time drops from ~3 seconds to under 0.5 seconds.
   - Server flake lockfile has only 2 inputs instead of 10.
   - Zero risk of desktop package breakages blocking server builds.
