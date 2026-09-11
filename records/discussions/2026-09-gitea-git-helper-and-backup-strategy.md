---
type: discussion
project: homelab
tags:
  - gitea
  - git
  - backup
  - homelab
date: 2026-09-10
---

# Discussion: Gitea Git Credential Helper, Protocol Trade-Offs, and Hybrid Backup Architecture

## 1. Context & Motivation

While evaluating tooling configurations, an analysis arose regarding whether to configure Gitea (via the `tea` CLI) as a Git credential helper, and how local Git workflows should adapt to a hybrid topology:
- **Primary Forge**: Self-hosted Gitea instance (`gitea.roadtotech.me`) running Gitea Actions for automated CI/CD pipelines.
- **Secondary / Backup Forge**: GitHub (`github.com`) as a public cloud warm backup.
- **Questions addressed**:
  1. What is the role of a Git helper, and does configuring Gitea as one provide tangible value?
  2. How does `tea` compare to GitHub's `gh` credential helper, and what are its limitations?
  3. What is the optimal architecture for keeping repositories synchronized between self-hosted Gitea and GitHub?

---

## 2. Demystifying the Git Helper

### The Role of a Credential Helper
Git core does not include native persistent storage for network credentials. When performing operations over **HTTPS** (e.g., `git clone https://...`, `git push origin main`), Git invokes a helper program (`git credential-<helper>`) implementing standard subcommands (`get`, `store`, `erase`) to retrieve HTTP Basic Auth credentials or access tokens without prompting the user on every transaction.

### The Critical Protocol Divide: HTTPS vs. SSH
A credential helper is strictly scoped to the **HTTPS** transport protocol:
- **HTTPS (`https://...`)**: Passes tokens/passwords through the Git credential helper subsystem.
- **SSH (`git@...`)**: Authentication is handled entirely by OpenSSH (`ssh-agent`, public/private key pairs such as `~/.ssh/id_ed25519`). Git delegates the network transport directly to the SSH binary. Credential helpers are never queried or invoked.

Because local developer configurations (such as `gh.settings.git_protocol = "ssh"` in `Config/modules/user/base.nix`) already standardize on SSH for day-to-day work, a Git credential helper remains completely inactive during standard SSH pushes and pulls.

---

## 3. Comparative Analysis: `tea` vs. `gh`

| Dimension | GitHub CLI (`gh auth git-credential`) | Gitea CLI (`tea login helper`) |
| :--- | :--- | :--- |
| **Authentication Flow** | Interactive OAuth web flows, 2FA prompts, or ephemeral personal tokens. | Static Personal Access Token (PAT) configured during `tea login add`. |
| **Lifecycle & Expiry** | Dynamically refreshes expiring OAuth tokens in the background. | Completely static; if the PAT expires or is revoked, Git fails until updated in `~/.config/tea/config.yml`. |
| **Target Scope** | Defaults to `credential.https://github.com`. | Defaults to `credential.https://<self-hosted-domain>`. |
| **Namespace Isolation** | Domain-scoped in Git config. | Domain-scoped in Git config. **Both helpers can coexist without conflicts.** |
| **NixOS Compatibility** | Declaratively handled via `programs.gh`. | Attempts imperative runtime `git config --global`, which fails (`exit status 255`) on NixOS due to read-only symlinks to `/nix/store`. |

---

## 4. Trade-Off Evaluation: Should Gitea be Configured as a Git Helper?

### Benefits
1. **Frictionless HTTPS Fallback**: Facilitates cloning private repositories via HTTPS without manual token prompts.
2. **Firewall Resilience**: If outbound SSH (port 22) is blocked (e.g., corporate networks, restrictive Wi-Fi), operations can fall back to HTTPS (port 443) seamlessly.
3. **No Cross-Forge Pollution**: Because Git matches helpers by explicit URL prefixes (e.g., `[credential "https://gitea.roadtotech.me"]`), configuring `tea` does not interfere with GitHub configurations.

### Costs & Limitations
1. **NixOS Friction**: Cannot be registered imperatively via `tea login add` without triggering `exit status 255`. It must be declared explicitly in Home Manager (`programs.git.settings`).
2. **Maintenance Overhead**: Static tokens require manual renewal and re-configuration upon expiration.
3. **Redundancy**: With SSH keys deployed to both Gitea and GitHub, credential helpers provide no utility for standard development flows.

### Conclusion
**Rely on SSH as the primary transport for daily development.** Configure `tea login helper` only if HTTPS fallback is specifically required, and do so declaratively in Home Manager rather than imperatively through the CLI.

---

## 5. Architectural Blueprint: Self-Hosted Primary with Cloud Backup

To fulfill the goal of self-hosting all repositories with Gitea Actions CI/CD while maintaining GitHub as a backup, two structural models exist:

### Model A: Server-Side Push Mirroring (Recommended)

```text
Local Workstation
       │
       ▼ git push (SSH)
Gitea Instance (Primary)
  ├── 1. Triggers local Gitea Actions (CI/CD)
  └── 2. Push Mirror Daemon ──(Background Sync)──> GitHub (Backup)
```

1. **Workflow**:
   - The developer pushes exclusively to Gitea: `git push origin main`.
   - Gitea Actions picks up the push and runs automated tests/builds.
   - Gitea's native **Push Mirror** automatically synchronizes all branches, tags, and commits to the corresponding GitHub repository.
2. **Advantages**:
   - **Zero Local Overhead**: Single push command; no duplicate network egress from the local workstation.
   - **Resilience**: If GitHub experiences downtime or rate limits, local work is unaffected; Gitea queues and retries the mirror sync automatically.
   - **Guaranteed Parity**: The backup mirror is updated server-to-server immediately upon receipt.

### Model B: Dual Push Remotes (Client-Side)

1. **Configuration**:
   ```gitconfig
   [remote "origin"]
       url = git@gitea.roadtotech.me:kiskaadee/repo.git
       pushurl = git@gitea.roadtotech.me:kiskaadee/repo.git
       pushurl = git@github.com:kiskaadee/repo.git
   ```
2. **Trade-offs**:
   - Requires double upload bandwidth on the workstation.
   - If one forge hangs or fails, the entire push command can fail or partially complete, requiring manual reconciliation.

---

## 6. Actionable Implementation Path

1. **Gitea SSH Authentication**: Add `~/.ssh/id_ed25519.pub` to the Gitea profile (`Settings -> SSH / GPG Keys`).
2. **Repository Mirroring Setup**:
   - In Gitea, open **Repo Settings -> Repository -> Push Mirrors**.
   - Set remote address to `https://github.com/kiskaadee/<repo>.git` (or SSH deploy key).
   - Enter GitHub Personal Access Token with repository write permissions.
   - Enable sync on push.
3. **Declarative HTTPS Fallback (Optional)**:
   If HTTPS support is desired, add the following to `modules/user/base.nix`:
   ```nix
   programs.git.settings = {
     "credential \"https://gitea.roadtotech.me\"" = {
       helper = "tea login helper";
     };
   };
   ```
