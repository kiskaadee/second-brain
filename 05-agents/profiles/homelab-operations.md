---
type: agent
status: active
name: homelab-operations
target_workspace: /home/kiskaadee/Homelab
project: homelab
tags:
  - homelab
  - operations
  - nixos
  - guardrails
  - execution-harness
  - interactive-troubleshooting
  - gitops
  - troubleshooting
---

# Homelab Operations & Troubleshooting Agent

## 1. Overview & Operational Scope

* **Target Workspace**: `/home/kiskaadee/Homelab` (Local multi-repo operations workstation)
* **Primary Role**: Autonomous diagnostic triage, read-only inspection, local declarative development, interactive troubleshooting execution harness, and structured incident recording.
* **Problem Space & Safety Constraints**:
  * **The "Local First" Rule & Workspace Isolation**: Edits are strictly authored in the local workspace on dedicated branches (`investigate/<topic>` or `fix/<topic>`); never directly on the remote server host via interactive SSH sessions. Read-only diagnostics require no branch.
  * **Remote Diagnostic Boundary**: Agents use SSH strictly for read-only inspections (`journalctl`, `docker logs`, `appctl info`, container `exec`). Production service restarts or deployments over SSH are strictly forbidden as autonomous agent operations.
  * **Mandatory Execution Boundaries**: The agent must **never autonomously** create Git commits on `main`, push to any remote, merge branches, deploy to production, execute `nixos-rebuild`, or perform service restarts to roll out changes.
  * **Global Skill Delegation**:
    * Diagnostic triage and 6-part checkpoints defer to the global skill **`engineering-investigation`**.
    * Atomic commit slicing, Conventional Commit derivation, and branch readiness defer to the global skill **`git-commit`**.
    * Incident RCA capture and architectural decisions defer to the global skill **`documentation-router`** (`03-records/debug/`, `03-records/decisions/`).

---

## 2. Architectural Modeling & Design Rationale

### A. Dual-File Architecture: Authoritative Contract (`AGENTS.md`) vs. Client Adapter (`CLAUDE.md`)
The operational contract is partitioned into two files to solve the problem of multi-agent tooling drift:
* **`AGENTS.md` as the Single Source of Truth**: Houses the universal, client-agnostic operational rules for the homelab appliance. It captures system topology, network endpoints, server integrity guardrails, deployment handoffs, and CI/CD invariants.
* **`CLAUDE.md` as a Lean Client Adapter**: Instructs Claude Code to read and defer strictly to `AGENTS.md` without duplicating or redefining policy. It clarifies toolchain mechanisms (`.claude/rules/`, `.claude/skills/`, and hooks) and establishes a clear directive: *do not duplicate or override the operational rules in `AGENTS.md`*.

### B. Global Skill Synergy
Rather than defining custom, redundant execution loops in every repository, Homelab operations leverage the global workstation skills:
1. **`engineering-investigation`**: Enforces the scientific method (Observe $\to$ Hypothesize $\to$ Test $\to$ Narrow $\to$ RCA $\to$ Fix $\to$ Validate $\to$ Verify) and halts at structured 6-part checkpoints before crossing state boundaries.
2. **`git-commit`**: Discovers repository-local branch isolation rules, evaluates commit slice readiness, and derives evidence-based Conventional Commit messages while preventing direct commits to `main`.
3. **`documentation-router`**: Acts as a second-order gatekeeper to evaluate whether incident findings warrant a durable Debug Record (`03-records/debug/`) or an ADR, eliminating unnecessary documentation boilerplate for routine fixes.

---

## 3. Canonical Agent Specifications

### A. Authoritative Specification: `/home/kiskaadee/Homelab/AGENTS.md`

````markdown
# 🤖 Homelab Operations & Troubleshooting — Agent Guidelines

This repository (`/home/kiskaadee/Homelab`) is the local operational workstation for administering, developing, and troubleshooting the `roadtotech.me` homelab appliance.

---

## 1. System Topology & Environment Awareness

* **Local Workstation**: `laptop` (`/home/kiskaadee/Homelab`)
  * `Core/`: NixOS host definition, SOPS secrets, shared platform services, and orchestration tooling (`appctl`).
  * `Sites/`: Independent application workloads (`Sites/<app>/docker-compose.yml`, `Sites/<app>/app.yaml`).
* **Remote Appliance**: `server` (`roadtotech.me`)
  * **Local LAN SSH**: `ssh server-local` (`192.168.1.36:22`)
  * **Remote WAN SSH**: `ssh server-remote` (`roadtotech.me:2222`)
  * **Gitea Git Remote**: `ssh://git@gitea.roadtotech.me:2223/kiskaadee/<repo>`

---

## 2. Remote Interaction & Server Integrity Guardrails

To protect the server appliance's integrity, agents **must strictly follow** these operational rules:

### A. The "Local First" Rule & Workspace Isolation
* **Never edit code or configuration files directly on the server over SSH** (e.g. `sed`, `cat <<EOF`, `nano`, `vim`).
* **Branching & State Isolation**:
  * Diagnostic investigation that is read-only (logs, metrics, status queries) does not modify repository state and does not require a branch.
  * **If repository state must change during investigation or remediation, work must be isolated from `main` on a dedicated local branch.**
  * Use `investigate/<topic>` when troubleshooting requires repository modifications before the root cause or remediation is established (e.g., temporary instrumentation, reproduction configurations, exploratory patches).
  * Use `fix/<topic>` or `feat/<topic>` for straightforward remediation or feature work.
  * **Do not create branches for individual hypotheses**; hypotheses belong in the diagnostic journal, while Git branches represent isolated repository states.
  * Once remediation is confirmed, ensure exploratory instrumentation is removed so only production-intended changes are proposed.
* Verify invariants and test locally before proposing commits or handoffs.

### B. What Agents CAN Do Over Remote SSH
Agents are encouraged to use SSH for **read-only diagnostics and non-destructive inspection**:
* **Logs & Metrics**:
  * `ssh server-local "journalctl -u <service> -n 50 --no-pager"`
  * `ssh server-local "docker logs --tail 50 <container>"`
  * `ssh server-local "appctl logs <app>"`
* **Status & Inspections**:
  * `ssh server-local "systemctl status <service> --no-pager"`
  * `ssh server-local "appctl list --core"` / `appctl info <app>`
  * `ssh server-local "docker ps -a"` / `docker inspect <container>`
* **Runtime Diagnostic Execution**:
  * `ssh server-local "docker exec <container> <cmd>"` (e.g., `nslookup`, `curl`, `getent`)

### C. Mandatory Execution Boundaries (What Agents MUST NOT Do Autonomously)
To protect operational safety and preserve user ownership:
* **Do not create commits, push to any remote, or merge branches.** Propose atomic commits with descriptions and validation proof; do not execute `git commit`, `git push`, or `git merge`.
* **Do not deploy changes to production.** The user owns all production transitions. The agent provides deployment runbooks and rollback procedures, but never executes deployment commands.
* **Do not execute `nixos-rebuild` autonomously.** System-level NixOS rebuilds can disrupt network, DNS, or boot configs. When Core/NixOS changes are validated, provide the deployment runbook for the user to execute:
  ```bash
  sudo nixos-rebuild switch --flake ~/Core#server
  ```
* **Do not perform production service restarts** (e.g. `appctl restart <app>`, `docker restart <container>`) as part of deploying changes.
* **Do not run destructive Docker commands** (e.g. `docker system prune -a --volumes` or manual database file removals) without explicit confirmation.
* **Do not modify `/etc/` or host system files** over SSH outside of NixOS declarative modules.

---

## 3. Operational Lifecycles & Global Skill Integration

Operational troubleshooting, commit packaging, and knowledge preservation defer strictly to the workstation's global skills:

### A. Investigation & Checkpoints (`engineering-investigation`)
* When diagnosing or troubleshooting issues on the host or application stacks, follow the scientific progression governed by **`engineering-investigation`** (Observe $\to$ Hypothesize $\to$ Test $\to$ Narrow $\to$ RCA $\to$ Fix $\to$ Validate $\to$ Verify).
* Pause at meaningful transitions (state changes, hypothesis confirmation/elimination, atomic commit boundaries, deployment handoffs) using the 6-part checkpoint protocol (Current State, Reasoning, Changes, Validation, Next Action, Recovery).

### B. Git Commits & Branch Integration (`git-commit`)
* Commit packaging, atomic slicing, and branch safety are governed by **`git-commit`**.
* Edits must be isolated on dedicated branches (`investigate/<topic>` or `fix/<topic>`); direct commits to `main` are strictly prohibited.
* The agent proposes atomic commit slices with evidence-based Conventional Commit messages; autonomous commits on `main` are blocked.

### C. Architectural & Incident Knowledge Preservation (`documentation-router`)
* Knowledge preservation is governed by **`documentation-router`**.
* Only non-obvious root causes, false system assumptions, or architectural discoveries warrant durable capture (`03-records/debug/`, `03-records/decisions/`, or `02-discussions/` in the Brain).
* Routine maintenance, configuration adjustments, and self-explanatory fixes require no external documentation.

---

## 4. Production Deployment & Handoff Policy

The user owns the production transition. When local validation is complete:
1. Explicitly identify that the change is ready for deployment.
2. Provide a structured **Deployment Handoff**:
   * **Exact User Action Required**: Provide the exact deployment command(s) appropriate to the affected workload:
     * *Core / NixOS host*: `sudo nixos-rebuild switch --flake ~/Core#server`
     * *Sites workloads*: target-specific service commands (e.g. `ssh server-local 'cd ~/Sites/<app> && git fetch && git pull origin <branch> && appctl restart <app>'` or stack-specific compose invocations).
   * **Expected Production Changes**: State changes, service reloads, or container recreations that should occur.
   * **Expected Post-Deployment Evidence**: Log lines, socket status, or HTTP response codes indicating success.
   * **Verification Commands**: Non-destructive diagnostic commands the agent or user will run post-deployment to verify recovery.
   * **Rollback Procedure**: Step-by-step instructions to restore previous state if verification fails.
3. Do not execute the deployment. Wait for user execution before proceeding to post-deployment verification.

This policy applies equally to Core/NixOS system changes and Sites application changes.

---

## 5. CI/CD & Gitea Actions (`act_runner`) Invariants

* **Pre-Baked Images over In-Job Installers**: Always declare `container: { image: <image> }` (e.g., `nixery.dev/shell/coreutils/git/nix/nodejs:latest`, `python:3.12-slim`, `node:20-alpine`) rather than running dynamic installers in generic Ubuntu runners. Note that `act_runner` expects standard FHS utilities (like `/bin/sleep`) at container initialization; minimal images like raw `nixos/nix` lack `/bin/sleep` and fail container init.
* **Git Safe Directory Invariant**: When job containers mount the workspace with root or differing UIDs, always configure Git safe directory before invoking Git or Flake tools:
  ```yaml
  - name: Configure Git Safe Directory
    run: git config --global --add safe.directory "$GITHUB_WORKSPACE"
  ```
* **Avoid GitHub API Assumptions**: Avoid third-party marketplace actions that rely on `${{ github.server_url }}` (which resolves to `https://gitea.roadtotech.me` instead of `github.com`). Use direct container runtimes and standard shell scripts.

````

### B. Client Adapter Specification: `/home/kiskaadee/Homelab/CLAUDE.md`

````markdown
# Homelab Agent Instructions

This repository is operated under the project rules defined in `AGENTS.md`.

## Operating Contract

Before investigating, modifying, or troubleshooting the Homelab:

1. Read and follow `AGENTS.md`.
2. Treat `AGENTS.md` as the authoritative operational contract.
3. Preserve the Local First rule and workspace isolation requirements.
4. Follow the interactive troubleshooting and execution harness defined there.
5. Keep the user in control of commits, branch integration, and production deployment.
6. Do not create commits, push, merge, deploy, or execute `nixos-rebuild` autonomously.
7. Use meaningful checkpoints rather than stopping after every individual command.
8. Preserve the distinction between diagnostic reasoning, repository state, and the durable incident journal.

## Scope

Do not duplicate or override the operational rules in `AGENTS.md`.

For Claude-specific behavior, prefer Claude Code mechanisms such as:
- `.claude/rules/` for scoped repository instructions;
- `.claude/skills/` for reusable workflows;
- hooks for deterministic enforcement where appropriate.

When instructions appear to conflict, stop and surface the conflict rather than silently choosing the more permissive interpretation.
````

---

## 4. Related Resources & Context

* [Homelab Architecture & Topology Overview](../../06-projects/homelab/README.md)
* [Homelab Core Platform Agent](homelab-core.md)
* [Brain GitOps & Auto-Sync Deployment Pipeline Guide](../../04-learning/guides/homelab/brain-gitops-deployment-pipeline.md)
* [Scientific Incident Investigation & Epistemic Journaling Protocol](../../04-learning/knowledge/methods/incident-investigation-and-journaling.md)
* [Webhook HMAC Signature Mismatch RCA](../../03-records/debug/2026-09-21-gitops-webhook-payload-signature-mismatch.md)
