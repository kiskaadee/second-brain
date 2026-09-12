---
type: plan
status: active
project: nixos
tags:
  - nixos
  - workstation
  - architecture
  - refactor
  - cleanup
---

# Architecture & Execution Plan: Decoupling Server & Standalone NixOS Workstation

## Executive Summary & Context

Following the migration of the homelab infrastructure, Docker stacks, and Traefik edge ingress to the dedicated [`homelab-core`](file:///home/kiskaadee/Projects/active/homelab/Core) repository, the primary system configuration repository ([`/home/kiskaadee/Config`](file:///home/kiskaadee/Config)) transitions from a multi-host fleet manager into a single-purpose, declarative configuration for the mobile workstation host (`laptop`) running Wayland (Niri) and Home Manager.

This document combines the **first-principles architectural analysis** of the standalone workstation with the **concrete phased implementation plan** to decommission legacy server files, dissolve the "multi-host tax", and re-align documentation.

Per the **Risk Classification Framework** in `Config/AGENTS.md` (Tier **HIGH**: server deployments, Traefik, SOPS keys/secrets setup), this plan establishes explicit invariants and validation criteria before execution.

---

## Part 1: Architectural Analysis — The Standalone Workstation

### 1. The Context & The "Multi-Host Tax"

The legacy structure of `Config` was heavily shaped by a classic systems challenge: **reconciling a headless homelab server with a Wayland graphical workstation in a single declarative repository**.

To prevent the server from compiling GUI libraries or running display managers, the configuration was forced to adopt several complex layers of indirection:
1. **The 3-Tier Home Manager Division**:
   - *Tier 1 (`base.nix`, `terminal.nix`, `neovim.nix`)*: Strictly CLI, safe for the headless server.
   - *Tier 2 (`apps.nix`)*: CLI developer tools and cloud SDKs.
   - *Tier 3 (`graphical.nix`)*: GUI applications, Wayland utilities, and display servers.
2. **The System Split**:
   - `modules/system/base.nix` vs. `modules/system/graphical.nix` (preventing the server from importing `greetd` or Wayland compositors).
3. **The `hosts/` Folder Hierarchy**:
   - `hosts/laptop/` vs. `hosts/server/`, each defining its own `configuration.nix` and `home.nix` that selectively imported combinations of the shared modules.

With the server decoupled and managed independently in `homelab-core`, the rationale for this defensive stratification disappears. Left behind is a **"multi-host tax"**: 8 hops of indirection, fragmented package lists across 7 files, and artificial module boundaries.

---

### 2. The Role of Home Manager: Machine vs. User Scope

Home Manager is often perceived as an unnecessary layer when it is used primarily as an **isolation barrier** between machines. In a multi-host setup, engineers frequently use Home Manager tiers to conditionally inject dotfiles into `$HOME` while struggling to keep system-level declarations uniform.

However, in a **standalone workstation**, Home Manager has a precise, clean architectural role:

| Concern | Native NixOS (`configuration.nix`) | Home Manager (`home.nix`) |
| :--- | :--- | :--- |
| **Scope** | Root / Machine level (`/etc`, systemd system units, kernel, hardware, display manager daemon, udev rules). | User session (`~/.config`, user systemd units, shell environment, desktop keybindings, app configs). |
| **Purity** | Modifies root filesystem state. Requires `sudo`. | Modifies only `$HOME`. Declarative symlink farm for dotfiles. |
| **Desktop Integration** | Runs the compositor (`programs.niri.enable`), greetd, PAM. | Configures the compositor (`config.kdl`), Alacritty, Fastfetch, Neovim plugins, Wayland clipboards. |

**Key Architectural Takeaway**: Home Manager itself is not the problem; **the multi-tiered, fragmented consumption of Home Manager was**. In a single-host setup, 5 separate Home Manager user modules are no longer needed to guard against a headless server.

---

### 3. First-Principles Standalone Architecture

Designed from scratch as a dedicated workstation, the architecture prioritizes **cohesion and domain grouping** over host isolation:

```mermaid
graph TD
    subgraph "Legacy (Multi-Host Guardrails)"
        FLAKE1[flake.nix] --> HOST_L[hosts/laptop/]
        FLAKE1 -.-> HOST_S[hosts/server/]
        HOST_L --> M_SYS_B[modules/system/base]
        HOST_L --> M_SYS_G[modules/system/graphical]
        HOST_L --> HM_ROOT[home.nix]
        HOST_L --> HM_L[laptop/home.nix]
        HM_ROOT --> TIER1[Tier 1: base + neovim + term]
        HM_L --> TIER2[Tier 2: apps]
        HM_L --> TIER3[Tier 3: graphical]
    end

    subgraph "First-Principles Standalone Workstation"
        FLAKE2[flake.nix] --> SYS[system/ (or configuration.nix)]
        FLAKE2 --> USR[home/ (or home.nix)]
        SYS --> D_SYS[desktop: Niri, greetd, audio]
        SYS --> H_SYS[hardware: battery, wifi, boot]
        USR --> D_USR[desktop: shortcuts, DMS, wayland]
        USR --> DEV_USR[dev: nvim, compilers, zed]
        USR --> SH_USR[shell: bash, tmux, aliases]
    end
```

#### Target Layout:

```text
Config/
├── flake.nix                   # Minimal entrypoint: defines nixosConfigurations.laptop
├── flake.lock
├── hardware-configuration.nix  # Generated hardware scan (disks, CPU, kernel)
│
├── system/                     # NixOS system-level concerns (root, daemons, hardware)
│   ├── default.nix             # Replaces hosts/laptop/configuration.nix + modules/system/*
│   ├── boot.nix                # systemd-boot, EFI, kernel modules
│   ├── hardware.nix            # Power profiles, brightnessctl, upower, audio (pipewire)
│   └── desktop.nix             # greetd, dank-greeter, Niri display enablement
│
├── home/                       # Home Manager user-level concerns (kiskaadee)
│   ├── default.nix             # Replaces home.nix + hosts/laptop/home.nix + tiers
│   ├── desktop/                # Niri keybindings (kdl), Alacritty, DMS, wallpapers
│   ├── dev/                    # Neovim, Zed, compilers, language servers, Git forge tools
│   └── shell/                  # Bash aliases, Tmux, Starship, custom scripts
│
└── docs/                       # Human maintenance and operational guides
```

---

### 4. Architectural Comparison: Standalone vs. Multi-Host

| Design Aspect | Current Multi-Host Legacy | Standalone Workstation Ideal |
| :--- | :--- | :--- |
| **Host Directory** | `hosts/laptop/` (defensive nesting anticipating sibling hosts) | Direct `system/` or root `configuration.nix` (no dummy nesting) |
| **User Modules** | 3 artificial tiers (`base`, `apps`, `graphical`) across 6 files | Domain modules (`desktop`, `dev`, `shell`) |
| **Package Attribution** | Dispersed across 7 separate `packages = with pkgs; [...]` lists | Consolidated by domain (e.g., dev packages live in `dev.nix`, GUI tools in `desktop.nix`) |
| **Mental Model** | *"Is this package safe for a headless server?"* | *"What domain does this tool belong to on my laptop?"* |
| **Aliases & Scripts** | Conditioned or sprinkled with leftover specialisations (`server-on/off`) | Tailored strictly to local workflow + remote client connections |

---

## Part 2: Phased Implementation Roadmap

To avoid unnecessary risk, the refactor follows a structured two-phase trajectory:

```
Phase 1: Immediate Decoupling & Server Pruning
(Decommission server host, delete server files, clean aliases, update docs)
                     ↓
Phase 2: Workstation Architectural Consolidation
(Consolidate system modules, dissolve Home Manager tiers into domain modules)
```

---

### Phase 1: Server Decommission & Decoupling (Immediate Scope)

#### 1. Host Declarations (`flake.nix`)
- Remove the `nixosConfigurations.server` definition block.
- Retain `nixosConfigurations.laptop` as the sole workstation target.
- Preserve existing flake inputs and `flake.lock` integrity.

#### 2. File Removal (`hosts/server/`)
- Remove the `hosts/server/` directory and all its contents:
  - `configuration.nix` (Headless server NixOS configuration)
  - `hardware-configuration.nix` (Server hardware parameters)
  - `home.nix` (Server diagnostic tools profile)
  - `secrets.yaml` (Encrypted server secrets)
  - `ddclient.conf` & `dynu.nix` (Dynu DDNS update configuration)
  - `homeserver.nix` (Core homelab runtime services)
  - `monitor.py` (WAN IP rotation detector)
  - `traefik-deployments.nix` (Edge proxy configuration)
- *Verification Invariant*: Confirm all homelab services have corresponding canonical representations in [`homelab-core`](file:///home/kiskaadee/Projects/active/homelab/Core/nixos).

#### 3. User Modules & Workstation Cleanup
- **`modules/user/base.nix`**:
  - Remove obsolete `server-on` and `server-off` aliases referencing legacy hardware specialisations.
  - Preserve SSH client host configurations (`server-local`, `server-remote`, `gitea.roadtotech.me`) to ensure uninterrupted remote management from the workstation.
- **`modules/user/neovim.nix`** & **`hosts/laptop/configuration.nix`**:
  - Update comments and headers referencing desktop/server profiles.

#### 4. Documentation Rework
- **`architecture.md`**:
  - Update repository role to single-workstation architecture (`laptop`).
  - Update topology tree and Mermaid diagrams to remove `server`.
  - Update Layer Responsibilities and Placement Guide to omit homelab/DDNS rows, noting the homelab boundary in `Core`.
  - Update Architectural Invariants (Invariant 3 and 6) to reflect workstation-focused boundaries and validation.
- **`AGENTS.md`**:
  - Update scope and validation matrix to `laptop` only.
  - Remove server dry-build verification instructions (`nixosConfigurations.server`).
  - Update Section 5 (Host Isolation & Homelab Infrastructure) to document that homelab services are managed in `Core`.
- **`README.md`**:
  - Update title, description, and Mermaid diagram to focus on the Niri-based workstation environment.
  - Remove `hosts/server/` directory overview.
  - Remove Section 1 (Smart Dynamic DNS Monitor) from specialized automation.
  - Remove server rebuild instructions (`#server`).
  - Update Secrets Management and Reference Documentation sections.
- **`docs/dynu-ip-monitor.md`**:
  - Remove this file as the service is now homelab-internal under `Core`.
- **`docs/package-and-secrets.md`**, **`docs/secrets-management.md`**, **`docs/system-maintenance.md`**:
  - Update server-specific examples (e.g., `systemctl status dynu-monitor.service`, `hosts/server/secrets.yaml`, dynu registration snippets) to workstation equivalents.

---

### Phase 2: Workstation Architectural Consolidation (Future Scope)

Once the server removal has stabilized:
1. Flatten `hosts/laptop/` into a unified system profile (`system/`).
2. Dissolve the 3 Home Manager tiers (`Tier 1 / Tier 2 / Tier 3`) into clean functional domains (`desktop`, `dev`, `shell`).
3. Consolidate package lists by domain, eliminating duplicated definitions.

---

## Part 3: Verification & Invariant Proofs

Before committing Phase 1 changes in the `Config` repository, verify all invariants:

1. **Flake Integrity**:
   ```bash
   nix flake check
   ```
2. **Workstation Build Verification**:
   ```bash
   nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link
   ```
3. **Clean Git Working Tree**:
   ```bash
   git status
   git diff
   ```
   Confirm clean removal of server files without touching unrelated laptop workstation configurations.
