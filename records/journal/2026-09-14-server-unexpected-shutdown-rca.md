---
type: journal
project: homelab
date: 2026-09-14
tags:
  - operations
  - homelab
  - incident
  - rca
  - hardware
  - jellyfin
  - nixos
  - vaapi
---

# Incident RCA: Unexpected Server Shutdown & Thermal Cut-Off Resolution

## 1. Incident Overview

* **Host**: `server` (Beelink SER Mini PC, AMD Ryzen 7 255 with Radeon 780M Graphics, 64GB DDR5, NixOS 26.11)
* **Incident Window**: Sunday, 2026-09-13 22:30:12 CST to Monday, 2026-09-14 07:49:53 CST (~9h 20m downtime)
* **Symptoms**: The server abruptly went offline late Sunday night. Physical inspection Monday morning revealed the computer was completely turned off with no LED activity. Pressing the physical power button restored normal boot.

---

## 2. Initial Hypotheses

1. **Software Crash / Kernel Panic**: Kernel halted on an unhandled exception and either hung or rebooted.
2. **Out of Memory (OOM) Lockup**: Memory leak from containers caused system lockup or aggressive OOM kills.
3. **OS-Initiated Thermal Shutdown**: ACPI thermal governor detected high temperatures and cleanly powered off the host (`poweroff.target`).
4. **Hardware Thermal / Power Trip**: Silicon-level PROCHOT protection or external power brick Over-Current Protection (OCP) cut power instantly without OS participation.

---

## 3. Step-by-Step Diagnostics

### A. Boot & Shutdown History Analysis
Inspected system boot states via `last` and `journalctl`:
```bash
last -x -n 10 shutdown reboot
journalctl --list-boots
```
* **Findings**: Boot `-1` (`Fri Sep 11 17:56:41`) had **no** preceding `shutdown system down` entry in `wtmp` before boot `0` (`Mon Sep 14 07:49:56`). The system was never cleanly commanded to power off.

### B. Journal Tail Inspection
Inspected the final moments of the previous boot via `journalctl -b -1 -n 40`:
* **Findings**: The log abruptly ceased at `22:30:12` in the middle of serving an HTTP GET request for `.obsidian/app.json` via Gitea.
* No `systemd-shutdownd`, no `systemd-logind` power action, and no disk sync messages were recorded. The disk buffer was halted mid-stream, confirming an instant drop-dead power cut.

### C. Kernel & Memory Verification
Checked kernel logs and memory utilization:
```bash
journalctl -b -1 -k --since '2026-09-13 21:00:00'
free -h
```
* **Findings**: The Linux kernel recorded zero errors or warnings in the 90 minutes preceding the shutdown. The system had over 51GiB of available RAM out of 58GiB with zero OOM events.

### D. Workload & Service Discovery
Filtered container activity during the 30 minutes leading up to the cut:
* Over 174 `ffmpeg` / `trickplay` / `jellyfin` log entries occurred between 22:00 and 22:30.
* Jellyfin was looping continuously through library media (*Solo Leveling*, *House of the Dragon*, *Dr. Stone*, *Teen Titans*), logging hundreds of errors:
  ```text
  System.IO.IOException: Read-only file system : '/media/Shows/Solo Leveling (2024) [imdbid-tt21209876]/S01E03.trickplay'
     at System.IO.FileSystem.CreateDirectory(String fullPath, UnixFileMode unixCreateMode)
     at Jellyfin.Server.Implementations.Trickplay.TrickplayManager.RefreshTrickplayDataInternal(...)
  ```

### E. The "Read-Only File System" Mystery
* **Host vs Container Permissions**:
  * On the host, `/media/Shows` was owned by `kiskaadee:users` with permissions `drwxr-xr-x` (755).
  * In `docker-compose.yml`, the volume mount was explicitly defined as read-only:
    `- ${MEDIA_PATH:-/media}:/media:ro`
  * In Jellyfin's Library configuration (`Shows/options.xml`), the option `<SaveTrickplayWithMedia>true</SaveTrickplayWithMedia>` was enabled.
* **Failure Loop Mechanics**: Jellyfin attempted to create `.trickplay` folders directly beside `.mkv` files in `/media`. Because the bind mount was `:ro`, Linux returned `EROFS`. Jellyfin caught the error and immediately advanced to the next episode, spawning `ffmpeg` repeatedly in a rapid, continuous CPU loop.

### F. Transcoding & Hardware Acceleration Audit
Inspected Jellyfin's encoding profile (`config/config/encoding.xml`):
* `<HardwareAccelerationType>none</HardwareAccelerationType>`
* `<EncodingThreadCount>-1</EncodingThreadCount>` (Auto — grabs all 16 threads)
* `<EnableThrottling>false</EnableThrottling>`
* `docker-compose.yml` did not expose `/dev/dri` to the container.
* **Root Cause Conclusion**: Without GPU passthrough, Jellyfin performed 100% CPU software video decoding and thumbnail scaling across all 16 threads. In a compact Beelink SER mini PC chassis, prolonged multi-core AV1/H.264 CPU software processing heat-soaked the cooling chamber, triggering AMD hardware PROCHOT thermal cut-off (~105°C) to prevent silicon destruction.

---

## 4. Remediation & Measures Taken

### 1. Hardware GPU Passthrough (AMD Radeon 780M VA-API)
* Evaluated host GPU capabilities with `vainfo` inside a test container:
  * Host device `/dev/dri/renderD128` confirmed operational with Mesa Gallium 25.0.7 (radeonsi, phoenix, RDNA3).
  * Confirmed full hardware encode/decode support for H.264, HEVC (10-bit), and AV1.
* Updated `docker-compose.yml` in `Homelab/Sites/jellyfin`:
  ```yaml
      devices:
        - /dev/dri:/dev/dri
      group_add:
        - "303" # render group on host
  ```
* Committed (`916d598: feat: enable AMD Radeon GPU passthrough for VA-API`), pushed to Gitea origin, and deployed on `server-remote` via `git pull && appctl restart jellyfin`.

### 2. Elimination of the Trickplay Loop
* In Jellyfin Web UI (`Dashboard -> Libraries -> Shows & Movies -> Manage Library`):
  * **Unchecked**: `Save trickplay files within media folders`.
  * Thumbnails now save to the read-write `/cache` and `/config` volumes, eliminating the `EROFS` crash loop.

### 3. Transcoding Safeguards & Throttling
* In Jellyfin Web UI (`Dashboard -> Playback -> Transcoding`):
  * **Hardware acceleration**: Switched to `Video Acceleration API (VAAPI)` with device `/dev/dri/renderD128`.
  * **Codecs enabled**: Hardware decoding for H264, HEVC, AV1, and VP9.
  * **Thread limit**: Set transcoding thread count to `4` (fallback limit instead of unconstrained `Auto`).
  * **Throttling**: Enabled `[x] Throttle Transcodes` (buffer delay 180s) to allow CPU/GPU cool-down intervals during active streaming.

### 4. Operational & Physical Maintenance Recommendations
* **Physical Cleaning**: Inspect fan intake and copper exhaust fins on the Beelink SER chassis to ensure unobstructed airflow.
* **BIOS Power Recovery**: Enable `State After G3` / `Restore on AC Power Loss -> Power On` in BIOS so the server automatically recovers from power interruptions.
* **BIOS TDP**: Ensure CPU power limit is set to Balanced (54W) rather than Performance (65W).
