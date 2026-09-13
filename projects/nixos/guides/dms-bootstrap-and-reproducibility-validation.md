---
type: guide
project: nixos
tags:
  - nixos
  - dms
  - niri
  - docker
  - validation
  - bootstrap
---

# Validation Guide: DMS Desktop Bootstrap & Container Reproducibility Test

## Executive Summary

To verify the standalone workstation's disaster recovery and first-boot convergence without risking the host system, we conducted an end-to-end containerized bootstrap test using an isolated NixOS Docker container (`nixos/nix:latest`). 

The test verified:
1. Pure flake evaluation and check (`nix flake check`) in a freshly cloned environment.
2. The exact behavior of `dms setup binds` in an empty user home directory.
3. The preservation of the application's runtime mutation model without store-symlink conflicts.

---

## 1. Container Isolation & Flake Evaluation Test

We spawned an ephemeral container running official `nixos/nix` to simulate a clean machine without pre-existing user configurations or local caches:

```bash
docker run --rm \
  -v /home/kiskaadee/Config:/repo:ro \
  nixos/nix:latest \
  sh -c '
    git config --global --add safe.directory "*"
    git clone /repo /root/Config
    cd /root/Config
    nix --extra-experimental-features "nix-command flakes" flake check
  '
```

### Results
* **Git Clone**: Successfully cloned the declarative repository into `/root/Config`.
* **Inputs Evaluated**:
  - `nixpkgs` (unstable official zstd tarball)
  - `home-manager`
  - `dms`, `dgop`, `dank-greeter`, `dankcalendar`, `danksearch`
  - `zen-browser-flake`, `antigravity-nix`
* **Outcome**: **`all checks passed!`** (Clean evaluation of `nixosConfigurations.laptop`).

---

## 2. Desktop Bootstrap Test: `dms setup binds`

On a fresh NixOS installation, the DMS daemon touches an empty `0-byte` file for `binds.kdl` if missing, resulting in absent keybindings on initial launch. 

To validate the non-privileged bootstrap protocol, we executed `dms setup binds` in a completely empty, simulated user environment (`HOME=/tmp/fresh-user`):

```bash
echo "1" | DMS_PRIVESC=sudo HOME=/tmp/fresh-user dms setup binds
```

### Observed Behavior & Verification
1. **Compositor Detection**: DMS correctly auto-detected `niri` as the active Wayland compositor.
2. **Terminal Detection**: DMS detected `alacritty` and populated all application launcher strings accordingly.
3. **Privilege Escalation**: Setting `DMS_PRIVESC=sudo` cleanly bypassed interactive prompts.
4. **File Generation**:
   - Location: `~/.config/niri/dms/binds.kdl`
   - File Size: `9,153 bytes`
   - Permissions: `-rw-r--r--` (`0644`, owned by the user)
5. **Keybindings Populated**:
   - Core launchers: `Mod+T` (Alacritty), `Mod+Space` (Spotlight), `Alt+Space` (Spotlight Bar), `Mod+V` (Clipboard), `Mod+M` (Task Manager).
   - Session controls: `Super+X` (Power Menu), `Mod+Comma` (Settings), `Mod+Tab` (Overview), `Mod+Shift+E` (Quit).
   - Audio & Brightness: `XF86AudioRaiseVolume`, `XF86MonBrightnessUp`, MPRIS controls.
   - Window & Workspace navigation: `Mod+Q` (Close), `Mod+F` (Maximize), `Mod+Shift+T` (Floating), column and monitor navigation.

---

## 3. The Declarative vs. Runtime Mutation Proof

| Configuration | Behavior Under Store Symlink (`home.file`) | Behavior Under Seeded Bootstrap (`dms setup binds`) |
| :--- | :--- | :--- |
| **Monitor Re-arrangement** | Fails or gets overwritten on `nixos-rebuild switch`. | Persisted by DMS to `outputs.kdl` cleanly. |
| **Wallpaper Theming** | Matugen cannot write dynamic palettes to read-only store. | Matugen updates `colors.kdl` dynamically at runtime. |
| **GUI Keybinding Tweaks** | Fails with `EACCES` when editing in DMS Settings. | Modifies `binds.kdl` directly with user permissions. |
| **First-Boot State** | Zero shortcuts if empty file touched. | **Complete functional desktop instantly seeded.** |

---

## 4. Disaster Recovery Procedure Summary

On any new workstation machine:
1. Perform bare-metal install per `docs/getting-started.md`.
2. Execute initial switch: `sudo nixos-rebuild switch --flake ~/Config#laptop`.
3. Log into Niri via `dank-greeter`.
4. Run the one-time desktop bootstrap:
   ```bash
   dms setup binds
   ```
5. All Niri shortcuts, DMS panels, and custom user keybindings (`custom.kdl`) become immediately functional.
