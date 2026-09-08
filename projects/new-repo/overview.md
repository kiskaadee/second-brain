---
type: project
status: active
tags:
  - gitea
  - github
  - rust
  - automation
  - cli
  - homelab
---
# 🚀 new-repo — Automated Repository Provisioning CLI

## 🎯 Overview

`new-repo` is a lightweight native Rust command-line utility designed to automate the creation of new repositories across a hybrid Git topology:
- **Primary Forge**: Self-hosted Gitea instance (`gitea.roadtotech.me`).
- **Offsite Backup Forge**: GitHub (`github.com`) via automated push mirroring.

It eliminates repetitive manual setup by providing sensible defaults (Gitea as primary, automated GitHub push mirroring, `UNLICENSE` default, private visibility) while supporting Gitea repository templates and optional standalone configurations.

---

## 🏛️ System Architecture & Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Developer (Laptop)
    participant CLI as new-repo (Rust)
    participant SOPS as sops (RAM Decrypt)
    participant Gitea as Gitea API (Primary)
    participant GitHub as GitHub API (Backup)
    participant Git as Local Git

    User->>CLI: new-repo <repo-name> [flags]
    
    alt Using Template (-t <template>)
        CLI->>Gitea: POST /repos/{owner}/{template}/generate
        Gitea-->>CLI: Repo created from template
    else Standard Repo
        CLI->>Gitea: POST /user/repos (with license & init)
        Gitea-->>CLI: Repo created
    end

    opt Mirroring Enabled (Default)
        CLI->>SOPS: sops -d --extract ["github_mirror_token"]
        SOPS-->>CLI: In-Memory Token (SecretStr)
        CLI->>GitHub: POST /user/repos (create target repo)
        GitHub-->>CLI: 201 Created
        CLI->>Gitea: POST /repos/{owner}/{repo}/push_mirrors
        Gitea-->>CLI: Push Mirror Registered
    end

    opt Auto-clone Enabled (-c / --clone)
        CLI->>Git: git clone git@gitea.roadtotech.me:user/repo.git
        Git-->>CLI: Working tree ready
    end
```

---

## 🔒 Security Model

1. **In-Memory Token Handling**: The GitHub Personal Access Token (`github_mirror_token`) is decrypted strictly in-memory from `secrets.yaml` using `sops`.
2. **Zero Command-Line Leaks**: Secrets are transmitted exclusively via native HTTPS request headers (`Authorization: token ...`), preventing token visibility in `/proc/$PID/cmdline` or system process listings (`ps`).
3. **Memory Hygiene**: Secret buffers are scrubbed from memory after use.

---

## 📑 Project Documents & Plans

- [**Repository Provisioning CLI Plan**](plans/provisioning-cli-plan.md) — Comprehensive functional specification, trait architecture, API contracts, and implementation milestones.
- **Local Implementation Tree**: [`/home/kiskaadee/Projects/active/new-repo`](file:///home/kiskaadee/Projects/active/new-repo)
