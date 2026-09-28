---
type: debug
date: 2026-09-27
project: nixos
tags:
  - incident
  - nixos
  - memory
  - zram
  - earlyoom
  - postmortem
---

# Laptop Memory Exhaustion Postmortem & Mitigation

## Incident Summary

On September 27, 2026, the `laptop` mobile workstation experienced a total UI freeze and lockup during high memory pressure, requiring a hard power-off.

### Root Cause
- **Zero Swap Space Configured**: With 38 GiB of RAM and 0B of swap, `systemd-oomd` logged `No swap; memory pressure usage will be degraded` at boot.
- **Synchronous Page Thrashing**: Without swap backing, the Linux kernel cannot swap out cold anonymous pages. Under heavy memory allocations, it was forced to aggressively drop file-backed pages (binaries, shared libraries, font caches).
- Once executable code pages were dropped, every user action, compositor frame, and audio buffer demanded synchronous NVMe disk reads. As I/O stalled, the compositor (`niri`), audio server (`pipewire`), and text editor (`zed`) locked up simultaneously before the kernel OOM killer could act.

## Implemented Mitigations (`system/core.nix`)

Two complementary layers of memory protection were declared in `~/Config/system/core.nix`:

### 1. Compressed In-RAM Swap (`zramSwap`)
```nix
zramSwap = {
  enable = true;
};
```
- Creates a virtual compressed block device (`/dev/zram0`) using up to 50% of RAM (~19 GiB) with fast `zstd` compression.
- Provides the kernel with headroom to page out inactive anonymous memory rather than discarding file cache.
- Satisfies `systemd-oomd` requirements for tracking memory pressure metrics.

### 2. Early OOM Killer Daemon (`services.earlyoom`)
```nix
services.earlyoom = {
  enable = true;
  enableNotifications = true;
  extraArgs = [
    "--avoid" "^(niri|dms|systemd|sshd)$"
  ];
};
```
- Monitors RAM and swap availability once per second.
- Proactively terminates the largest offending rogue process before memory exhaustion causes kernel and compositor lockups.
- Configured with `--avoid` to protect core session components: `niri` (Wayland compositor), `dms` (DankMaterialShell), `systemd`, and `sshd`.
- Configured with `enableNotifications = true` to alert the user via desktop notifications whenever a process is terminated.

## Validation & Verification

- `nix flake check`: Passed (5 checks: shellcheck, luacheck, ruff-lint, ruff-format, pyright, plus flake outputs).
- Dry build validation: `nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link` passed successfully.

## Activation Instructions

To activate these changes on the host system:
```bash
sudo nixos-rebuild switch --flake .#laptop
```
Verify zram is active after rebuild:
```bash
zramctl
free -h
systemctl status earlyoom
```
