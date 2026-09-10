---
type: guide
project: homelab
tags:
  - gitea
  - brain
  - sync
  - gitops
  - cicd
  - homelab
status: active
---

# 🧠 Real-Time Brain Synchronization, CI/CD & Gitea Push Mirroring

## 🎯 Motivation & Objectives
The **Brain** repository (`~/Brain`) is an actively edited, durable personal knowledge graph. It is accessed locally (via CLI, agents, and Obsidian) and served live to `https://docs.roadtotech.me` via `homelab-doc2site`.

### Core Pipeline Invariants:
1. **The Curation Boundary**: Raw thoughts and scratch captures stay in `inbox/` (uncommitted, unvalidated, zero-friction). Once moved to their semantic home (`knowledge/`, `projects/`, `records/`, `practice/`), they join the committed graph.
2. **Local Schema Integrity Gate**: Every commit is verified locally by [`scripts/validate-brain.py`](../../../../scripts/validate-brain.py) via a `pre-commit` hook to ensure valid metadata and prevent broken relative links.
3. **Instant Zero-Delay Auto-Push**: A resilient `post-commit` hook automatically pushes commits to the primary self-hosted Gitea forge (`gitea.roadtotech.me`), falling back gracefully if offline.
4. **Automated Cloud Replication**: Gitea natively push-mirrors every commit to GitHub (`github.com/kiskaadee/second-brain`) immediately on receive.
5. **Server-Side CI & Observability**: Gitea Actions validates graph health on every push asynchronously without blocking editing or live rendering.

---

## 🏛️ End-to-End Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ LOCAL WORKSTATION (~/Brain)                                 │
│                                                             │
│  [inbox/] (Uncommitted staging, raw capture)                │
│      │                                                      │
│   (Curate: move to knowledge/, projects/, records/)         │
│      ▼                                                      │
│  git commit                                                 │
│      │                                                      │
│      ▼                                                      │
│  .githooks/pre-commit ────(Invalid)────► [Abort commit]     │
│      │ (Valid)                                              │
│      ▼                                                      │
│  Commit created                                             │
│      │                                                      │
│      ▼                                                      │
│  .githooks/post-commit ───► git push origin <branch>        │
└──────────────────────────────────────┬──────────────────────┘
                                       │ (HTTPS / SSH)
                                       ▼
┌─────────────────────────────────────────────────────────────┐
│ SELF-HOSTED GITEA (gitea.roadtotech.me)                     │
│                                                             │
│  Primary Forge receives new HEAD                            │
│  ├── 1. Push Mirror ──────────────► GitHub (Cloud Backup)   │
│  ├── 2. Gitea Actions (CI) ───────► act_runner validation   │
│  └── 3. doc2site Sync / Render ───► docs.roadtotech.me      │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Component Details

### 1. Local Git Hooks (`.githooks/`)

The repository maintains version-controlled hooks in `.githooks/`:

* **`pre-commit`**: Validates repository structure, required root files, YAML frontmatter, and relative markdown links.
* **`post-commit`**: Automatically runs `git push origin <current-branch>` with offline tolerance and detached-HEAD checks.

#### Installation:
Run the installer script anytime in a fresh clone:
```bash
bash scripts/install-hooks.sh
```

---

### 2. Gitea Actions CI Workflow (`.gitea/workflows/validate.yaml`)

Runs server-side verification using standard Actions syntax

### 3. Setting Up Gitea Actions Runner (`act_runner`)

To enable CI execution on `gitea.roadtotech.me`:

#### Step A: Enable Actions in Gitea `app.ini`
Ensure your Gitea configuration file (`app.ini`) includes:
```ini
[actions]
ENABLED = true
```
Restart Gitea if this was just enabled.

#### Step B: Obtain Registration Token
1. In Gitea, navigate to **Site Administration** $\rightarrow$ **Actions** $\rightarrow$ **Runners** (or Repository **Settings** $\rightarrow$ **Actions** $\rightarrow$ **Runners**).
2. Click **Create new Runner** and copy the registration token (`<REGISTRATION_TOKEN>`).

#### Step C: Deploy `act_runner`

**Option 1: Docker Compose (Homelab Host)**
```yaml
version: "3.8"
services:
  runner:
    image: gitea/act_runner:latest
    container_name: gitea-act-runner
    restart: always
    environment:
      - GITEA_INSTANCE_URL=https://gitea.roadtotech.me
      - GITEA_RUNNER_REGISTRATION_TOKEN=<REGISTRATION_TOKEN>
      - GITEA_RUNNER_NAME=homelab-docker-runner
      - GITEA_RUNNER_LABELS=ubuntu-latest:docker://node:18-bullseye,ubuntu-22.04:docker://node:18-bullseye
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/data
```

**Option 2: Declarative NixOS Module**
```nix
services.gitea-actions-runner.instances."homelab-runner" = {
  enable = true;
  name = "homelab-nixos-runner";
  url = "https://gitea.roadtotech.me";
  tokenFile = "/run/secrets/gitea-runner-token";
  labels = [
    "ubuntu-latest:docker://node:18-bullseye"
  ];
};
```

---

### 4. Gitea Push Mirroring (GitHub Hot Backup)

Configured under repository **Settings** $\rightarrow$ **Repository** $\rightarrow$ **Push Mirrors**:
* **Remote Address**: `https://github.com/kiskaadee/second-brain.git`
* **Authorization**: GitHub Username + Classic Personal Access Token with `repo` scope.
* **Sync Trigger**: *"Sync when commits are pushed"* enabled.

---

## 📄 Summary of Benefits
* ⚡ **Zero-Friction Staging**: Uncommitted raw captures in `inbox/` never trigger validation failures.
* 🛡️ **Guaranteed Knowledge Integrity**: Commits are validated before being finalized.
* 🚀 **Zero-Delay Auto-Sync**: Commits push instantly to Gitea and mirror to GitHub.
* 🔍 **Continuous Observability**: Server-side CI validates the entire knowledge graph on push.
