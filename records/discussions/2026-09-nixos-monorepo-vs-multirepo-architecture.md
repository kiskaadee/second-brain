---
type: discussion
project: nixos
tags:
  - nixos
  - architecture
  - homelab
  - monorepo
date: 2026-09-11
---

# Architectural Analysis: NixOS Monorepo vs. Multi-Repo for Homelab & Workstations

## The Dilemma

In the NixOS ecosystem, putting all machines into a single `flake.nix` repository is the most common default pattern. However, as an infrastructure grows, pairing a **bleeding-edge personal workstation (`laptop`)** with an **always-on, service-hosting node (`server`)** in the same repository creates real operational friction.

---

## 1. Why Monorepos Feel Natural Initially (The Benefits)

1. **Shared CLI Muscle Memory**:
   - Your shell aliases (`git.sh`, `todo.sh`), Neovim keymaps, Tmux configurations, and Starship prompt look and behave identically whether you are in a local terminal on your laptop or SSH'd into your server.
2. **Single Codebase & Single Lockfile**:
   - You only have one repository to clone, commit to, and push.
   - Both machines reference identical pinned package revisions when sharing a channel.
3. **Refactoring Reusability**:
   - Base system settings (like timezones, locale, Docker configurations, and base utilities) are declared once in `modules/system/base.nix`.

---

## 2. The Hidden Architectural Costs of the Monorepo (The Pain Points)

1. **Coupled Dependency Graph & Lockfile Drift**:
   - Every graphical or desktop tool added for the laptop (e.g., `zen-browser`, `dms`, `dank-greeter`, `dankcalendar`, `hyprland`) lives in the same `flake.nix` and `flake.lock`.
   - When you update `nixpkgs` to fix a laptop browser issue, the server's kernel, Docker daemon, and systemd services are simultaneously bumped.
   - If an unstable upstream package fails evaluation on the desktop/laptop side, `nix flake check` fails globally, blocking server builds.
2. **Conflicting Release Lifecycles & Risk Tolerance**:
   - **Laptop**: Experimental, rapidly iterated, customized frequently, running bleeding-edge packages. If a daily update breaks a Wayland shortcut or status bar widget, it's a minor inconvenience.
   - **Server**: Production infrastructure running Traefik, Gitea, Authelia, and containers. It demands stability, minimal churn, and zero downtime.
3. **GitOps Trigger Inefficiencies**:
   - With `homelab-gitops.service` watching the repository, pushing a cosmetic prompt tweak or desktop keybinding to `main` triggers a webhook pull and evaluation on the homelab server, even if nothing server-related changed.
4. **Channel Mismatch**:
   - In a monorepo with `specialArgs = { inherit inputs; }`, both machines are strongly pressured to follow the same channel (e.g. `nixos-unstable`).
   - A server often benefits from running `nixos-24.11` (stable) with security backports, while a Wayland workstation demands `nixos-unstable` for graphics drivers and compositor updates.

---

## 3. The Separated Model: Turning `homelab-core` into an Independent NixOS Host

The proposed brainstorm—*purging server content from this repo and making `homelab-core` a self-contained NixOS definition*—is an industry-standard architectural pattern (often called the **Service-Oriented Infrastructure Split**).

### Benefits of Full Separation:

1. **Zero Blast Radius**:
   - Pushing breaking experimental changes to your laptop configuration physically **cannot** impact the homelab server.
2. **Co-location of Infrastructure**:
   - In `homelab-core`, the host configuration (`configuration.nix`, `traefik-deployments.nix`, `homeserver.nix`) lives directly next to the Docker compose files, dynamic proxy rules, and deployment scripts that it configures.
3. **Independent Release Channels**:
   - Server can pin `nixos-stable` or conservative channel tarballs.
   - Laptop can freely track `nixos-unstable` without risk.
4. **Clean Webhooks & GitOps**:
   - GitOps webhooks on the server only trigger when actual server infrastructure changes are pushed.
5. **Separation of Secrets Boundaries**:
   - The laptop repository never needs to carry server secret hashes or keys.

---

## 4. How to Handle Shared Utilities (The Middle Ground)

If you separate the repositories, what happens to your shared CLI tools (`neovim`, `tmux`, `terminal.nix`, shell scripts)?

There are three clean approaches:

1. **Pure Multi-Repo (Minimal Duplication)**:
   - Keep the server CLI minimal (standard server packages like `htop`, `tmux`, `curl`, `git`, and simple stock configs).
   - Reserve rich custom development tools, custom Neovim plugins, and desktop scripts strictly for the laptop.
2. **Dotfiles as a Flake Input (Composable Architecture)**:
   - Extract `modules/user/` (or your dotfiles) into a lightweight `dotfiles` or `nix-profile` repository.
   - Both `nixos-config` (laptop) and `homelab-core` (server) import your dotfiles flake as a dependency.
3. **Submodule / Git Tree Sharing**:
   - A shared `common/` git submodule imported into both repos.

---

## 5. Strategic Recommendation

- If you frequently find yourself having to ensure laptop changes don't break the server, or if the server's GitOps triggers on unrelated laptop work, **separating them is the right architectural move**.
- Merging the server's NixOS definition directly into `homelab-core` turns `homelab-core` into a true single-node appliance: you clone `homelab-core` on the server, and it provisions the entire machine from the bare OS up to the running container services.
