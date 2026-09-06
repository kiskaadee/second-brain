# 🧠 Real-Time Brain Synchronization & Gitea Push Mirroring

## 🎯 Motivation & Objectives
The **Brain** repository (`~/Brain`) represents an actively edited knowledge vault (notes, architectural plans, daily learnings) accessed via Obsidian on client workstations (laptop) and served live to `https://docs.roadtotech.me` via `homelab-doc2site`.

### Key Challenges & Invariants:
1. **Zero CI/CD & Rate-Limit Overhead**: Standard GitHub Actions pipelines consume build minutes, hit quota limits, and take minutes to deploy. Note edits must appear in seconds without triggering remote CI runners.
2. **Instant Local Reflection**: `homelab-doc2site` dynamically reads from disk on every HTTP request. As soon as changes land on the server host in `/home/kiskaadee/Brain`, they are visible on `docs.roadtotech.me` with zero container rebuilds.
3. **Automated Cloud Backup**: Edits must be backed up offsite to GitHub automatically without manual multi-remote pushes.

---

## 🏛️ End-to-End GitOps Architecture

```
                    ┌────────────────────────┐
                    │     Laptop (Author)    │
                    │  (Obsidian / Markdown) │
                    └───────────┬────────────┘
                                │ (Auto Git Push over HTTPS)
                                ▼
                    ┌────────────────────────┐
                    │    Self-Hosted Gitea   │
                    │ (gitea.roadtotech.me)  │
                    └───────────┬────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │ [Push Mirror (Auto Cloud Backup)]             │ [Server Host Sync Pull]
        ▼                                               ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│     GitHub Remote (Offsite)   │               │ Server Systemd Service/Timer  │
│  (github.com/kiskaadee/Brain) │               │   (brain-sync.timer / pull)   │
└───────────────────────────────┘               └───────────────┬───────────────┘
                                                                ▼
                                                ┌───────────────────────────────┐
                                                │   Server Host: ~/Brain        │
                                                │   (Mounted to doc2site)       │
                                                └───────────────┬───────────────┘
                                                                ▼
                                                ┌───────────────────────────────┐
                                                │ Live docs.roadtotech.me (0s)  │
                                                └───────────────────────────────┘
```

---

## 🚀 Validated Test Results

A full end-to-end integration test was executed using a test repository (`testing-repo`):
1. **Local Push**: Laptop pushed commits over HTTPS to `https://gitea.roadtotech.me/kiskaadee/testing-repo.git`.
2. **Gitea Push Mirror**: Configured with GitHub Classic Personal Access Token (`ghp_...`) and `repo` scope.
3. **SHA Parity**: Verified identical commit hashes (`38285c4`) mirrored to `https://github.com/kiskaadee/testing-repo` instantaneously.

---

## ⚙️ Implementation Guide

### 1. Configure Gitea Push Mirror (Web UI)
1. Open Gitea repository $\rightarrow$ **Settings** $\rightarrow$ **Repository** $\rightarrow$ **Mirror Settings**.
2. Add Push Mirror:
   - **Target Address**: `https://github.com/kiskaadee/<repo-name>.git`
   - **Authorization**: GitHub Username + Classic PAT (`ghp_...` with `repo` scope).
   - **Sync Trigger**: Enable *"Sync when commits are pushed"*.

### 2. Client-Side (Laptop) Automation
On your laptop, configure automatic commit and push:
* **Option A (Obsidian Git Plugin)**: Set auto-save / auto-commit interval to 5–10 minutes.
* **Option B (Git Remote Configuration)**:
  ```bash
  cd ~/Brain
  git remote set-url origin https://gitea.roadtotech.me/kiskaadee/Brain.git
  ```

### 3. Server-Side Automated Git Reconciliation (`brain-sync.timer`)
A lightweight NixOS systemd timer runs periodically on the homelab host to pull upstream edits:

```nix
# Declarative Systemd Timer in NixOS
systemd.services.brain-sync = {
  description = "Synchronize Brain markdown vault from Gitea";
  serviceConfig = {
    Type = "oneshot";
    User = "kiskaadee";
    WorkingDirectory = "/home/kiskaadee/Brain";
    ExecStart = "${pkgs.git}/bin/git pull --ff-only origin main";
  };
};

systemd.timers.brain-sync = {
  description = "Trigger Brain sync every 2 minutes";
  timerConfig = {
    OnBootSec = "1min";
    OnUnitActiveSec = "2min";
  };
  wantedBy = [ "timers.target" ];
};
```

---

## 📄 Summary of Benefits
* ⚡ **Instant**: Note changes render live upon page load on `docs.roadtotech.me`.
* 🛡️ **Zero API / CI/CD Quotas**: Never consumes billable GitHub Actions minutes.
* 📦 **Offsite Redundancy**: Gitea autonomously keeps GitHub in sync as a hot backup.
