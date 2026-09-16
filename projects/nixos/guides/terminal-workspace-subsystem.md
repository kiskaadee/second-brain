---
type: guide
project: nixos
tags:
  - nixos
  - terminal
  - tmux
  - niri
  - alacritty
---

# Terminal Workspace Subsystem Walkthrough

## Summary of Completed Work

We evaluated, designed, and implemented the **Terminal Workspace Subsystem** for the `laptop` NixOS workstation. The subsystem enforces a clean, deterministic separation across four layers:

```text
┌─────────────────────────────────────────────────────────────┐
│ Niri (Compositor / Window Manager)                          │
│                                                             │
│ Mod+Return: Ephemeral Alacritty Shell ($SHELL)              │
│ Mod+T:      Persistent Workspace Terminal (Alacritty -> ts) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Alacritty (Terminal Emulator)                               │
│                                                             │
│ GPU rendering, PTY management, font metrics, input routing  │
│ (Does NOT auto-launch tmux globally)                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Sessionizer (`tmux-sessionizer` / `ts`)                     │
│                                                             │
│ Discovery → Normalization → Registry Validation             │
│ → Deterministic Resolution → Tmux Lifecycle                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Tmux (Terminal Multiplexer)                                 │
│                                                             │
│ Persistent headless process state across window closures;   │
│ Vi-mode copy, smart Neovim navigation, OSC-52 clipboard     │
└─────────────────────────────────────────────────────────────┘
```

---

## Files Modified & Created

1. **`home/scripts/tmux-sessionizer.sh`** [NEW]:
   - Discovers explicit workspaces (`~/Config`, `~/Brain`, `~/Homelab/Core`) and git repositories under `~/Projects` and `~/Homelab`.
   - Normalizes folder basenames to lowercase, regex-sanitized tmux session names without trailing hyphens/underscores (`tr '[:upper:]' '[:lower:]' | sed -E 's/[ .]+/-/g; s/[^a-z0-9_-]//g; s/[-_]+$//'`).
   - Validates the complete registry up-front for session name collisions before resolving requests (Option A: global fatal refusal).
   - Resolves CLI queries via strict precedence: (1) existing directory path, (2) exact session name, (3) exact basename, (4) unique substring match. Never guesses ambiguous matches.
   - Parses final record via native Bash `IFS=$'\t' read -r session_name target_dir`.
   - Dual-context switching: outside tmux calls `exec tmux attach-session -t ...`; inside tmux calls `tmux switch-client -t ...` (prevents nested sessions).
   - Establishes working directory with `-c "$target_dir"` only when creating a new session; never resets an existing session's directory.
2. **`home/shell.nix`** [MODIFIED]:
   - Declared `tmuxSessionizer` as a hermetic derivation using `pkgs.writeShellApplication` with runtime dependencies: `bash`, `coreutils`, `gnused`, `gawk`, `gnugrep`, `fd`, `fzf`, `tmux`.
   - Added `tmuxSessionizer` to `home.packages`.
   - Added shell alias `ts = "tmux-sessionizer";` to `programs.bash.shellAliases`.
3. **`home/config/niri/custom.kdl`** [MODIFIED]:
   - Added `Mod+T` hotkey binding to spawn Alacritty directly running `tmux-sessionizer`.
   - Updated `Mod+Return` label to denote ephemeral shell terminal.
4. **`docs/reference/tmux.md`** [MODIFIED]:
   - Restructured into the comprehensive **Terminal Workspace Architecture & Tmux Reference**.
   - Codified the 12 architectural invariants (INV-001 through INV-012).
   - Documented naming, discovery hierarchy, collision policies, CLI usage, and tmux configuration.

---

## Validation & Test Results

### 1. Script Quality & Shellcheck
- Ran `shellcheck` across `home/scripts/tmux-sessionizer.sh`.
- Passed with **0 errors, 0 warnings**.

### 2. Flake Validation (`nix flake check`)
- Ran `nix flake check` on `/home/kiskaadee/Config`.
- All checks (`check-ruff-lint`, `check-ruff-format`, `check-pyright`, `check-shellcheck`) passed cleanly.

### 3. Laptop Host Dry Build
- Executed dry build:
  ```bash
  nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link
  ```
- Build succeeded completely, building `tmux-sessionizer.drv`, Home Manager activation units, and the complete system top-level derivation.

---

## Operational Guide

### Interactive Workspace Selection
Press **`Mod+T`** from anywhere in Niri, or run `ts` in an existing terminal:
- `fzf` displays `session_name` and `absolute_path`.
- Pressing `Escape` exits cleanly with code `0` and closes the Alacritty window.
- Selecting a workspace creates or attaches to the persistent tmux session.

### Direct CLI Selection
```bash
ts config          # Attaches/switches to ~/Config session
ts brain           # Attaches/switches to ~/Brain session
ts bitetrack-api   # Attaches/switches to bitetrack-api session
ts magnet          # Unique substring match -> attaches to MagNetFlix
ts ~/Projects/...  # Explicit path
```

### Context Switching Inside Tmux
- While inside any active tmux session, running `ts <target>` or interactive `ts` switches the client directly via `tmux switch-client` without creating nested tmux instances.
