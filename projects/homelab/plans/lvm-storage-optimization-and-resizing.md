# 💾 LVM Storage Optimization & Partition Resizing Strategy

## 🎯 Motivation & Objectives
The homelab node operates on a **1 TB NVMe SSD (`nvme0n1`)** partitioned into an LVM2 Volume Group (`nixos_vg`) and formatted with `ext4` filesystems.
As the machine transitions into a dedicated 24/7 headless server (with GUI/compositor duties moving to the laptop), the storage topology needs to be optimized to prioritize media library growth (`/media` for Jellyfin) while reclaiming bloated desktop cache directories.

---

## 🔍 Current Storage Topology vs. Target Allocation

### Current Layout (931.5 GB Total NVMe SSD):
```text
nvme0n1 (931.5 GB NVMe SSD)
├── nvme0n1p1 (1 GB)    ── /boot (vfat EFI)
└── LVM Volume Group: nixos_vg (930.5 GB)
    ├── nixos_vg-root   (150 GB)   ── /      (ext4) [~110 GB used / 40 GB free]
    ├── nixos_vg-media  (380.5 GB) ── /media (ext4) [~289 GB used / 66 GB free - 77%]
    └── nixos_vg-home   (400 GB)   ── /home  (ext4) [~332 GB used / 39 GB free - 85%]
```

### 🚨 Critical Diagnostic: 323 GB Desktop Indexer Cache
During disk diagnostics, `/home` was found to be 85% full due almost entirely to:
* **`/home/kiskaadee/.cache/danksearch` (323 GB)**: Local search indexing daemon (`dsearch`) generated massive cache dumps and CPU overhead.
* Actual application repositories (`~/Sites`), Brain vault (`~/Brain`), and NixOS configurations (`~/Config`) consume **under 10 GB total**.

### Target Production Server Layout:
| Logical Volume | Mount Point | Current Size | Proposed Size | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `nixos_vg-root` | `/` | 150 GB | **120 GB** | More than ample for NixOS store generations, kernel images, and Docker container layers. |
| `nixos_vg-home` | `/home` | 400 GB | **180 GB** | Huge headroom for micro-repo codebases, Docker bind mounts, and persistent application data. |
| `nixos_vg-media` | `/media` | 380.5 GB | **~630 GB** | Allocates maximum SSD capacity to expanding Jellyfin media libraries (Movies, Shows, Music, Books). |

---

## 🛡️ LVM Resizing Mechanics (Zero Data Loss Rules)

### 1. Online Extension (Zero Downtime)
* **LVM + ext4 supports online expansion while the filesystem is actively mounted**:
  ```bash
  sudo lvextend -r -L +100G /dev/nixos_vg/media
  ```
  *(The `-r` / `--resizefs` flag automatically expands the underlying ext4 filesystem online in milliseconds).*

### 2. Offline Shrinking (Requires Unmounted Filesystem)
* **ext4 filesystems cannot be shrunk while mounted**.
* When shrinking `/home` to reallocate space to `/media`, execution must happen offline (e.g. from a NixOS Live USB):
  1. Boot into NixOS Live USB.
  2. Scan volume groups: `vgchange -ay nixos_vg`.
  3. Force filesystem check on `/home`:
     ```bash
     e2fsck -f /dev/nixos_vg/home
     ```
  4. Shrink filesystem and logical volume together (safe atomic reduce):
     ```bash
     lvreduce -r -L 180G /dev/nixos_vg/home
     ```
  5. Extend `/media` into the newly unallocated free space:
     ```bash
     lvextend -r -L 630G /dev/nixos_vg/media
     ```
  6. Reboot back into the production server.

---

## 🧹 Maintenance & Laptop Cache Safeguards

1. **Server Cleanup**:
   - Reclaim 323 GB on the server immediately:
     ```bash
     rm -rf ~/.cache/danksearch
     ```
2. **Laptop Monitoring (`dsearch` / DankSearch)**:
   - On the laptop (which uses Niri and DankMaterialShell), monitor `~/.cache/danksearch` periodically or limit its index scope to prevent index bloat and high CPU utilization.
