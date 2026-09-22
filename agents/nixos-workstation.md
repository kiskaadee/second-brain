---
type: agent
status: active
name: nixos-workstation
target_workspace: ssh://git@gitea.roadtotech.me:2223/kiskaadee/nixos-config
project: nixos
tags:
  - nixos
  - home-manager
  - workstation
  - guardrails
  - sops
---

# NixOS Mobile Workstation Configuration Agent

## 1. Overview & Operational Scope

* **Target Workspace**: `ssh://git@gitea.roadtotech.me:2223/kiskaadee/nixos-config` (`/home/kiskaadee/Config`)
* **Primary Role**: Maintains the declarative NixOS and Home Manager configuration for the `laptop` mobile workstation.
* **The Golden Rule & Security Barrier**:
  * **Build, Never Switch**: Agents are strictly forbidden from running `sudo nixos-rebuild switch`, `boot`, or `test`. The agent may modify declarations and verify via dry builds (`nix build ... --no-link`), but live-system mutations remain strictly in human hands.
  * **Preserve Pre-Existing Work**: Always check `git status` first and never discard, overwrite, or stash uncommitted human changes.
  * **Risk Classification Framework**: Changes are categorized into Low, Medium, High, and Prohibited tiers with clear escalation triggers.

---

## 2. Canonical Agent Specification

The following specification represents the active behavioral contract configured for `/home/kiskaadee/Config/AGENTS.md`:

````markdown
# AGENTS.md

## Mission & Purpose

This repository manages the declarative NixOS and Home Manager configuration for the `laptop` mobile workstation host.

AI agents working in this repository must maintain architectural integrity, avoid configuration sprawl, respect pre-existing work, and adhere strictly to the invariants defined in `architecture.md`.

---

## The Golden Rule: Build, Never Switch

> [!CAUTION]
> **Agents are strictly forbidden from executing `sudo nixos-rebuild switch`, `boot`, `test`, or mutating the running host system.**
> An agent may modify the *declaration* of the system and verify compilation. It must *never* autonomously alter the running state of the host machine.

### Security Boundary Model

```text
Repository
    │
    ├── Agent may READ
    ├── Agent may MODIFY
    └── Agent may VALIDATE
             │
             ▼
        Nix Derivation (Dry Build)
             │
      ═══════╪══════════════════════════════════════ [STRICT BARRIER]
             ▼
        Running Host System
        (Mutations strictly prohibited without explicit user instruction)
```

### Permitted Verification Commands
```bash
# Validate flake metadata, inputs, and derivations
nix flake check

# Build laptop host dryly (evaluates configuration without switching)
nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link
```

### Prohibited Live-System Commands (Unless Explicitly Requested)
- `nixos-rebuild switch` / `boot` / `test`
- `systemctl [start|stop|restart|reload]`
- `udevadm *`
- `mount` / `umount`
- `reboot` / `shutdown`
- `nix-store --delete` or manual modifications to `/nix/var/nix/profiles/`

---

## Operating Rules & Constraints

### 1. Request Interpretation
- **Narrow Interpretation**: Interpret the user's request as narrowly as reasonably possible.
- **No Inferred Authorization**: Do not infer permission for unrelated cleanup, dependency upgrades, directory reorganization, or live-system mutations.

### 2. Preserve Pre-Existing Uncommitted Work
- **Inspect First**: Before making any edits, check `git status` to identify pre-existing uncommitted changes.
- **Never Overwrite**: Never overwrite, discard, reset, stash (`git checkout .`, `git reset`, `git stash`), or manipulate user changes that existed prior to your task.
- **Distinguish Attribution**: Clearly separate pre-existing modifications from agent modifications in the completion report.

### 3. Do Not Expand Scope & Minimal Change Principle
- **No Spontaneous Refactoring**: An agent must not turn a feature request into a refactoring project.
- **Report Architectural Issues Separately**: If a requested change exposes an architectural smell or problem, report it to the user rather than silently attempting to refactor surrounding code (unless strictly required for correctness).
- **Smallest Viable Change**: Make the minimal change that satisfies the request. Do not introduce single-use abstractions, single-option wrapper modules, or arbitrary file reorganizations.
- **Capture Out-of-Scope Ideas in Second Brain**: When the user mentions a new idea, feature request, or architectural concept unrelated to the immediate active task, record a note in `/home/kiskaadee/Brain/` (or suggest logging it) so valuable insights are preserved without disrupting current execution scope.

### 4. Package Placement Rules
- **Developer Tools, Compilers, LSPs**: Place in `home/dev.nix`.
- **Graphical Applications & Desktop Tools**: Place in `home/desktop.nix`.
- **Terminal Utilities & Shell Integration**: Place in `home/shell.nix`.
- **System-Wide Daemons & Hardware Support**: Place in `system/core.nix` or `system/hardware.nix` *only* if required for root maintenance, core networking, or systemd daemons.

### 5. Homelab Infrastructure Decoupling
- Production homelab services, Traefik edge proxying, Docker container deployments, and DDNS automation live exclusively in the `Core` repository (`~/Projects/active/homelab/Core`).
- Never import or re-introduce server daemon definitions into this workstation repository.

### 6. Hardware Configurations
- `system/hardware-configuration.nix` is generated by `nixos-generate-config`. Do not manually restructure, clean up, or refactor it. Hardware additions (e.g., kernel parameters, disk mounts) require explicit justification.

### 7. Secrets & Key Safety (SOPS)
- **Never write or commit plaintext secrets** into `.nix`, `.yaml`, or temporary files.
- **Never decrypt secrets into tracked or persistent working-tree files**.
- **Never add, modify, or rotate SOPS/age keys** unless explicitly commanded by the user.
- **Never expose decrypted secret material** through `git diff`, logs, or terminal outputs.
- Reference secrets only via `/run/secrets/<name>` or `config.sops.secrets.<name>.path`.

### 8. Flake Dependencies
- Do not introduce a new flake input if standard `nixpkgs` provides the required package or module.
- Do not update unrelated flake inputs or regenerate `flake.lock` for feature changes.
- Pin `inputs.nixpkgs.follows = "nixpkgs"` on new flake inputs whenever applicable.

---

## Risk Classification Framework

| Tier | Category | Examples | Required Action & Workflow |
| :--- | :--- | :--- | :--- |
| **LOW** | User Configuration | User packages in `home/dev.nix`, shell aliases in `home/shell.nix`, Neovim lua config, docs. | **Autonomous**: Agent plans, edits, and validates via `nix flake check` + laptop build. |
| **MEDIUM** | System & Desktop Stack | `system/core.nix`, `system/desktop.nix`, greetd/DMS, firewall rules, user groups, new flake inputs. | **Autonomous**: Agent plans, edits, and validates via `nix flake check` + laptop build. |
| **HIGH** | Core Hardware & Boot | Bootloader, filesystem mounts, SOPS keys setup, kernel module changes. | **Stop & Wait**: Agent must present the plan and **wait for user approval before editing**. |
| **PROHIBITED** | Live System Mutators | `nixos-rebuild switch`, destructive disk ops, editing `/etc` outside Nix, rotating age keys, plaintext secrets. | **Blocked**: Cannot execute unless explicitly commanded by the user in the current prompt. |

---

## Change Protocol

Every modification by an agent must follow this lifecycle:

```text
REQUEST
   │
   ▼
1. UNDERSTAND
   ├── Identify affected components in system/ or home/
   ├── Check `git status` to identify pre-existing uncommitted work
   └── Read architectural boundaries in architecture.md
   │
   ▼
2. PLAN
   ├── Formulate minimal viable change
   ├── Verify no architectural invariants are violated
   └── IF HIGH RISK: Stop and present plan for user approval before proceeding
   │
   ▼
3. EDIT
   ├── Make targeted modifications only
   └── Respect package and secret placement boundaries
   │
   ▼
4. VALIDATE
   ├── Run `nix flake check`
   └── Build laptop host (`--no-link`): `nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link`
   │
   ▼
5. REVIEW
   ├── Inspect `git diff` for unintended changes or exposed secrets
   └── Ensure no pre-existing user work was disturbed
   │
   ▼
6. REPORT
   └── Provide completion report with pre-existing work status and build outputs
```

---

## Validation Matrix

| Modified Path | Affected Consumer | Required Build Validation |
| :--- | :--- | :--- |
| `system/*` | `laptop` | `nix flake check`<br>`nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link` |
| `home/*` | `laptop` | `nix flake check`<br>`nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link` |
| `flake.nix` / `flake.lock` | `laptop` | `nix flake check`<br>`nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link` |

---

## Documentation Hygiene

Maintain clear ownership of documentation:
- **`README.md`**: High-level repository overview and quick start.
- **`architecture.md`**: Structural topology, layer boundaries, and architectural invariants.
- **`AGENTS.md`**: Agent constitution, change policies, risk matrix, and validation rules.
- **`docs/*.md`**: Step-by-step procedural guides for humans (maintenance, secrets, Antigravity).

*Rule: Do not duplicate architectural descriptions into procedural docs or README.*

---

## Completion Report Format

When reporting back after a task, summarize:
1. **Pre-Existing Changes Detected**: [Yes / No (with details if preserved)]
2. **Files Modified by Agent**: List of exact files changed.
3. **Architectural Assessment**: Verification that invariants were respected and boundaries maintained.
4. **Validation Executed**: Output of `nix flake check` and `nix build ... --no-link`.
5. **Pending Manual Actions**: Any user-required steps (e.g. running `sudo nixos-rebuild switch` or committing changes).
````

---

## 3. Related Resources & Context

* [NixOS Fleet & Workstation Project Overview](../projects/nixos/README.md)
* [NixOS Standalone Workstation Walkthrough](../projects/nixos/guides/standalone-workstation-walkthrough.md)
* [Server Decoupling & Standalone Workstation Plan](../projects/nixos/plans/server-decoupling-and-standalone-workstation.md)
* [Homelab Operations Agent](homelab-operations.md)
