---
type: decision
status: accepted
project: nixos
tags: [terminal, tmux, niri, alacritty, sessionizer, architecture]
date: 2026-09-14
---

# Architectural Decision Record: Terminal Workspace Subsystem

## 1. Context & Problem Statement

On the `laptop` NixOS mobile workstation, terminal usage encompasses two fundamentally different intents:
1. **Ephemeral work**: Short-lived shells, quick inspections, one-off scripts, and debugging snippets that should start instantly, remain isolated, and terminate upon exit.
2. **Persistent project workspaces**: Long-running development contexts (`Config`, `Brain`, `Core`, `bitetrack-api`) with active background daemons, compilers, Neovim sessions, and multi-pane layouts that must survive graphical window closures.

Previously, tmux had to be started and attached manually, or terminals risked being hardwired to tmux globally. We needed a clean, deterministic architecture that decouples terminal emulation, graphical window tiling, workspace discovery, and session persistence without creating friction across tools, subshells, or desktop layers.

---

## 2. Considered Models

### Model A: Alacritty Globally Spawns Tmux (`shell.program = "tmux"` or `.bashrc` exec)
- **Concept**: Every Alacritty terminal instance attaches or creates a tmux session automatically.
- **Why Rejected**: Converts a workflow preference into a rigid application-level policy. Breaks tools executing `$SHELL` (Neovim `:terminal`, Git diff tools, IDE terminals), causes SSH nested-session collisions, couples unrelated windows to shared session geometries, and eliminates ephemeral scratch terminals.

### Model B: Niri Manages Tmux Sessions Directly
- **Concept**: Niri keybindings hardcode specific project sessions (e.g. `Mod+B -> tmux bitetrack`, `Mod+C -> tmux config`).
- **Why Rejected**: Pollutes compositor configuration with project-specific routing. Violates separation of concerns; Niri should manage graphical windows, not workspace identity.

### Model C: Decoupled Project-Driven Sessionizer (Chosen)
- **Concept**: Niri exposes two distinct entry points: `Mod+Return` for an ephemeral shell and `Mod+T` for a persistent workspace. The workspace entry point launches Alacritty running a dedicated control plane (`tmux-sessionizer` / `ts`) that discovers projects, validates uniqueness, and manages tmux sessions.

---

## 3. Chosen Architecture & Layer Separation

```text
                 "Where does the window live?"
                               │
                               ▼
                    Niri (Window Manager)
                               │
                "How is the terminal rendered?"
                               │
                               ▼
                 Alacritty (Terminal Emulator)
                               │
                     "Where am I working?"
                               │
                               ▼
                  Sessionizer (`ts` Control Plane)
                               │
               "Which persistent context is that?"
                               │
                               ▼
                   Tmux (Multiplexer Engine)
```

### Responsibility Boundaries

| Layer | Primary Responsibility | Explicit Boundaries |
| :--- | :--- | :--- |
| **Niri** | GUI window layout, focus, scrolling columns, application lifecycle. | Does NOT know project names or tmux session semantics. |
| **Alacritty** | GPU rendering, PTY allocation, font metrics, raw keyboard/mouse input. | Does NOT auto-start tmux globally; remains a clean terminal emulator. |
| **Sessionizer** | Workspace discovery, name normalization, collision safety, CLI resolution, attach/switch. | Does NOT orchestrate applications (no auto-starting Neovim, compilers, or servers). |
| **Tmux** | Headless process persistence, split panes, windows, layouts, client connections. | Does NOT manage GUI window placement or compositor layout. |

---

## 4. Design Principles

1. **Explicit persistence**: Persistent terminal state is opt-in through the workspace entry point (`Mod+T`); ordinary terminals (`Mod+Return`) remain ephemeral.
2. **Deterministic identity**: A workspace directory maps to a deterministic tmux session name derived from its basename.
3. **Refuse ambiguity**: The system fails rather than guessing when workspace identity cannot be determined uniquely.
4. **Separation of concerns**: GUI management, terminal emulation, workspace resolution, and terminal persistence remain independent responsibilities.
5. **Context without orchestration**: The sessionizer establishes workspace context (working directory and session) but does not dictate which project processes should run.
6. **Preserve existing state**: Reconnecting to an existing workspace restores the existing tmux environment rather than reconstructing or resetting it.
7. **Declarative integration**: The subsystem is packaged and integrated through NixOS/Home Manager (`pkgs.writeShellApplication`) with explicit runtime dependencies, avoiding mutable host state.

---

## 5. Architectural Invariants

The following invariants are normative for the subsystem:

- **INV-001 (Layer Separation)**: Niri owns GUI lifecycle; Alacritty owns emulation; Sessionizer owns workspace resolution; Tmux owns persistent terminal state.
- **INV-002 (Deterministic Naming)**: A workspace directory's basename MUST always normalize to the exact same tmux session identifier.
- **INV-003 (Unique Workspace Identity)**: Within the validated workspace registry, each normalized session name MUST correspond to exactly one workspace directory.
- **INV-004 (Strict Ambiguity Refusal)**: The sessionizer MUST refuse ambiguous workspace resolutions and session-name collisions before taking action.
- **INV-005 (No Nested Tmux)**: Invoking `ts` inside an existing tmux session MUST switch clients (`switch-client`) rather than creating a nested client.
- **INV-006 (Existing-Session Preservation)**: Resolving an existing session MUST NOT change its current working directory or reset its state.
- **INV-007 (Creation Establishes CWD)**: The target workspace directory establishes the working directory only when a new tmux session is created.
- **INV-008 (Independent Workspaces)**: Explicit workspace registration does not depend on Git repository metadata.
- **INV-009 (Supplemental Discovery)**: Git discovery supplements explicit workspace roots rather than replacing them.
- **INV-010 (No Project Orchestration)**: The sessionizer establishes context; it does not orchestrate project applications.
- **INV-011 (Side-Effect-Free Cancellation)**: Cancelling interactive selection (`Escape` in `fzf`) terminates cleanly with code `0` without creating or modifying sessions.
- **INV-012 (Hermetic Dependencies)**: The packaged executable (`tmux-sessionizer`) provides its required runtime dependencies explicitly via Nix `runtimeInputs`.
- **INV-013 (Resolution Snapshot)**: Workspace discovery and normalization MUST produce a single registry snapshot that is validated before resolution. Resolution MUST operate against that snapshot rather than rediscovering workspaces during the same invocation.

---

## 6. Workspace Discovery, Normalization & Collisions

### 6.1 Discovery Hierarchy
1. **Explicit Workspaces**: Registered roots (`$HOME/Config`, `$HOME/Brain`, `$HOME/Homelab/Core`).
2. **Git Repositories**: Discovered by searching for `.git` directories (depth 4) beneath `$HOME/Projects` and `$HOME/Homelab`.
3. **Deduplication**: Directory paths are deduplicated into an associative map before normalization.

### 6.2 Normalization Contract
```bash
normalize_name() {
    local raw="$1"
    local name
    name=$(basename "$raw" | tr '[:upper:]' '[:lower:]' | sed -E 's/[ .]+/-/g; s/[^a-z0-9_-]//g; s/[-_]+$//')
    [[ -z "$name" ]] && return 1
    echo "$name"
}
```

### 6.3 Global Collision Policy (Strict Refusal)
If multiple paths yield identical normalized session names (e.g. `/home/kiskaadee/Homelab/Core` and `/home/kiskaadee/Projects/archive/core`), validation fails globally:
```text
ERROR: workspace name collision: 'core'
  /home/kiskaadee/Homelab/Core
  /home/kiskaadee/Projects/archive/core
```
The sessionizer aborts before resolution occurs. Interactive mode does not guess between collided names.

### 6.4 Direct Path Bypass Property
Direct filesystem paths (e.g. `ts ~/some/path`) bypass repository discovery but still undergo canonicalization (`realpath`) and deterministic session-name normalization, allowing persistent sessions in arbitrary locations.

---

## 7. Resolution Algorithm Precedence

When invoked with `ts <argument>`:
1. **Existing Directory**: Direct path match via `realpath`.
2. **Exact Session Name**: Case-insensitive exact match against the normalized session name column.
3. **Exact Basename**: Case-insensitive match against directory basename.
4. **Unique Substring Match**: Substring match across session names and paths. Ambiguous matches list all candidates and fail.
5. **No Match**: Aborts with exit code `1`.

---

## 8. Client Context Awareness & Persistence

```text
Outside Tmux:
Alacritty → ts → fzf → exec tmux attach-session -t <session>

Inside Tmux:
Shell → ts → fzf → tmux switch-client -t <session>
```

Persistence resides strictly in the tmux server:
```text
Alacritty closes → PTY client disconnects → tmux server retains session & jobs
ts <workspace>   → reconnects to existing session without resetting state
```

---

## 9. Verification Summary

The implementation is verified via:
1. `shellcheck`: 0 warnings, 0 errors.
2. `nix flake check`: All linters and checks pass.
3. `nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link`: Closure evaluates and builds cleanly with `tmux-sessionizer.drv`.
