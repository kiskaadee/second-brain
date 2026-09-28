---
type: guide
project: nixos
tags:
  - nixos
  - flake
  - ci
  - linters
  - quality
---

# Integrated Linters and Quality Checks in Nix Flake Check

## Overview

Static analysis and linting checks are integrated directly into the Nix flake output (`checks.x86_64-linux` in `flake.nix`). This ensures that `nix flake check` verifies code hygiene and style alongside derivation evaluation.

## Integrated Checks

1. **Python Linting (`ruff-lint`)**:
   - Tool: `pkgs.ruff`
   - Command: `ruff check --no-cache ${self}`
   - Enforces flake8, bugbear, and Python linting rules.

2. **Python Formatting Check (`ruff-format`)**:
   - Tool: `pkgs.ruff`
   - Command: `ruff format --check ${self}`
   - Verifies formatting consistency without mutating the source tree.

3. **Python Static Type Checking (`pyright`)**:
   - Tool: `pkgs.pyright`
   - Command: `pyright ${self}`
   - Analyzes type hints across Python scripts (e.g. `bundle_project.py`).

4. **Shell Script Linting (`shellcheck`)**:
   - Tool: `pkgs.shellcheck`
   - Command: `find ${self} -type f -name "*.sh" -exec shellcheck -s bash {} +`
   - Analyzes all `.sh` scripts in `home/scripts/` and `home/shell/`.
   - Also added `# shellcheck shell=bash` directives to modular sourced scripts.

## Developer Tooling Additions

- Added `shellcheck` to `home/dev.nix` in `home.packages` so it is available interactively for editor diagnostics and CLI use.

## Validation Commands

```bash
# Run all flake checks (linters + NixOS system evaluation)
nix flake check

# Run individual checks
nix build .#checks.x86_64-linux.ruff-lint --no-link
nix build .#checks.x86_64-linux.ruff-format --no-link
nix build .#checks.x86_64-linux.pyright --no-link
nix build .#checks.x86_64-linux.shellcheck --no-link
```
