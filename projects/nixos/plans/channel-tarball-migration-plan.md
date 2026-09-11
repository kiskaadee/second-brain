---
type: plan
status: active
project: nixos
tags:
  - nixos
  - flake
  - optimization
  - hydra
---

# 📦 Evaluation & Implementation Plan: Adopting Official `channels.nixos.org` Tarballs

## 🎯 Goal Description

An evaluation of transitioning from GitHub-hosted Nixpkgs flake references (`github:nixos/nixpkgs/nixos-unstable`) to the official project-hosted channel tarballs (`https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst`), based on the NixOS Discourse community discussion *"PSA: Use nixos.org tarballs for your flake inputs!"*.

This plan identifies:
1. Every location in the [`/home/kiskaadee/Config`](file:///home/kiskaadee/Config) repository and system configuration where this change can be applied.
2. The architectural, performance, and operational trade-offs of making the change.
3. A safe execution strategy respecting repository invariants (Build, Never Switch).

---

## 🔍 Technical Analysis & Trade-offs

### Why the Community Proposes This
* **Zstandard (zstd) vs Gzip**: `channels.nixos.org/nixos-unstable/nixexprs.tar.zst` is compressed with `zstd -19` on official NixOS infrastructure. GitHub repository archives only provide gzip compression. Switching reduces download payload by ~20–33%.
* **Forge Independence**: Decreases reliance on GitHub's infrastructure and reduces vulnerability to GitHub rate-limiting (`403 API rate limit exceeded`), service outages, or API changes.
* **Metadata & Channel Integrity**: Channel tarballs are released only when Hydra channel jobs succeed and binary caches (`cache.nixos.org`) are populated. They also bundle channel metadata (such as `programs.sqlite` for `command-not-found`).
* **IPv6 Support**: Fastly / NixOS CDN provides native IPv6 support, which GitHub tarball downloads historically struggled with or throttled.

### Trade-offs & Caveats in This Configuration
* **Scope of Tarballs**: Only `nixpkgs` is hosted on `channels.nixos.org`. Third-party flake inputs in this configuration (`home-manager`, `dms`, `dgop`, `dank-greeter`, `zen-browser`, `sops-nix`, `antigravity`) do not have official project tarballs and will remain on GitHub.
* **`flake.lock` Invalidation**: Modifying `nixpkgs.url` changes the input node type from `github` to `tarball`. This triggers an update of `nixpkgs` in `flake.lock` to the latest channel snapshot, causing all downstream inputs (`inputs.nixpkgs.follows = "nixpkgs"`) to re-lock against that new channel evaluation.
* **Evaluation Ergonomics**: `https://channels.nixos.org/...` does not have a short URL prefix like `github:`.
* **Tarball Unpack**: A tarball flake input unpacks the full expression tree into `/nix/store` or the Git cache. In incremental Git checkouts, git delta fetching can sometimes be faster than a cold tarball unpack if git objects are already present locally.

---

## 📋 Audit of Candidate Areas

| Area | Current Declaration | Candidate Change | Recommendation |
| :--- | :--- | :--- | :--- |
| **System Flake Input**<br>[`flake.nix:L8`](file:///home/kiskaadee/Config/flake.nix#L8) | `nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";` | `nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst";` | **Recommended** (Primary candidate) |
| **System Flake Registry**<br>(CLI `nix run nixpkgs#...`) | Unconfigured (falls back to global registry pointing to `github:NixOS/nixpkgs`) | Add `nix.registry.nixpkgs.flake = inputs.nixpkgs;` to system base | **Recommended** (Ensures CLI tools share the exact channel cache without querying GitHub) |
| **Dev Environments Guide**<br>[`docs/development-environments.md:L34`](file:///home/kiskaadee/Config/docs/development-environments.md#L34) | `nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";` | `nixpkgs.url = "https://channels.nixos.org/nixpkgs-unstable/nixexprs.tar.zst";` | **Recommended** (Documents the faster `nixpkgs-unstable` channel for standalone dev flakes) |
| **Antigravity Guide**<br>[`docs/antigravity.md:L97`](file:///home/kiskaadee/Config/docs/antigravity.md#L97) | `nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";` | `nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst";` | **Optional** (Documentation reference) |

---

## 🛠️ Proposed Changes

### 1. Flake Configuration

#### [MODIFY] `flake.nix` in `~/Config`

```diff
   inputs = {
     # NixOS Unstable channel - used for bleeding-edge package releases
-    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
+    nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst";

     # Home Manager - manages user-space configurations, dotfiles, and shell environments
     home-manager = {
```

---

### 2. System Base Module (Optional CLI Registry Pinning)

#### [MODIFY] `modules/system/base.nix` in `~/Config`

```diff
+  # Pin nixpkgs flake registry to the flake input to prevent ad-hoc CLI queries to GitHub
+  nix.registry.nixpkgs.flake = inputs.nixpkgs;
```

---

### 3. Documentation

* **`docs/development-environments.md`**: Update the boilerplate example to point to `https://channels.nixos.org/nixpkgs-unstable/nixexprs.tar.zst` with a note explaining the zstd download efficiency and forge independence.
* **`docs/antigravity.md`**: Update example reference flake input from GitHub URL to the channel tarball URL.

---

## 🧪 Verification Plan

### Automated Tests
1. **Flake Metadata & Lock Validation**:
   ```bash
   nix flake lock --update-input nixpkgs
   nix flake check
   ```
2. **Dry-Build System Targets (Build, Never Switch)**:
   ```bash
   nix build .#nixosConfigurations.laptop.config.system.build.toplevel --no-link
   nix build .#nixosConfigurations.server.config.system.build.toplevel --no-link
   ```

### Manual Verification
1. Inspect `git diff` in `~/Config` to confirm only `nixpkgs` input and lockfile were modified.
2. Verify `nix flake metadata` shows:
   - `Resolved URL: https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst`
   - Valid locked `tarball` type with `narHash`.
