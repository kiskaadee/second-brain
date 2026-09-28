---
type: decision
status: accepted
project: nixos
date: 2026-09-27
tags:
  - nixos
  - antigravity
  - flake
  - packaging
  - developer-tools
---

# Architectural Decision Record: Unified Antigravity Flake Packaging

## 1. Context & Problem Statement

The `laptop` NixOS workstation requires access to the complete Google Antigravity developer ecosystem across all three primary operational surfaces:
1. `google-antigravity-cli`: The terminal CLI binary (`agy`).
2. `google-antigravity`: The Electron-based desktop GUI application (Antigravity 2.0).
3. `google-antigravity-ide`: The VS Code-derived AI-first development environment.

Previously, incorporating rapidly evolving AI developer tools into a NixOS configuration posed maintenance friction:
- Packaging each component individually in `~/Config` requires tracking separate upstream tarballs, deb/rpm assets, and release hashes.
- Manual derivation maintenance introduces the risk of version desynchronization across the CLI, GUI, and IDE components.
- Upstream updates require manual derivation bumps and rebuild testing directly within the core workstation configuration.

## 2. Decision

We adopt `github:jacopone/antigravity-nix` as the single unified flake input (`inputs.antigravity`) in the workstation configuration (`Config/flake.nix`).

- **Upstream Repository**: `github:jacopone/antigravity-nix`
- **Flake Input**: `inputs.antigravity`
- **Exposed Packages**:
  - `inputs.antigravity.packages.${system}.google-antigravity-cli`
  - `inputs.antigravity.packages.${system}.google-antigravity`
  - `inputs.antigravity.packages.${system}.google-antigravity-ide`

## 3. Consequences

### Positive
- **Bundled 3-Component Ecosystem**: A single flake input packages and maintains all three surfaces, eliminating redundant derivation authoring.
- **Synchronized Upstream Cadence**: Automated upstream updates in the flake ensure the CLI, desktop GUI, and IDE remain version-aligned, preventing API or protocol mismatches.
- **Declarative Flake Decoupling**: Upstream tool updates are cleanly consumed via `nix flake update antigravity` without touching system configuration build recipes.

### Negative / Trade-offs
- **External Flake Dependency**: Introduces a dependency on an external flake repository (`jacopone/antigravity-nix`) for maintenance and packaging updates rather than official upstream Nixpkgs derivations.
