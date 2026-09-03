# 🌐 Homelab & Infrastructure Planning

This section documents the architectural roadmaps, infrastructure designs, deployment automation, and system administration workflows for the homelab ecosystem.

---

## 📑 Index of Plans

1. [**NixOS Server & Laptop Migration**](nixos-server-laptop-migration.md)
   - Converting the desktop into a 24/7 headless production server.
   - Setting up the laptop as the primary graphical development workstation.
   - Decoupling visual configurations (Niri, Hyprland, Waybar, GUI apps) from the server.
2. [**Domain Migration (`roadtotech.me`)**](domain-migration-roadtotech.md)
   - Step-by-step strategy for cutting over from `arch-services.mywire.org` to `roadtotech.me`.
   - DNS delegation options (Dynu vs. Cloudflare), Traefik ACME wildcard SSL, and Authelia session cookie updates.
3. [**Homelab Infrastructure & Appctl Architecture**](homelab-appctl-architecture.md)
   - Making `appctl` a first-class homelab orchestrator.
   - Decoupling monolithic deployments into individual standalone Git repositories.
4. [**CI/CD & Deployment Strategy**](deployment-and-cicd-strategy.md)
   - Automating image builds, GitOps updates, Gitea Actions/GitHub Actions, and production rollouts.
5. [**Production Folder Structure Reorganization**](folder-structure-reorganization.md)
   - Establishing strict directory boundaries (`/home/kiskaadee/Production`, `/home/kiskaadee/Deployments`, `/home/kiskaadee/Projects`).
   - Removing development traces and non-production scratchpads from the server.
