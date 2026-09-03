# 🧠 Second Brain

Central repository for personal knowledge management, architecture plans, roadmaps, homelab infrastructure designs, and project tracking.

---

## 🧭 Navigation & Areas

| Area | Focus & Purpose | Key Documents |
| :--- | :--- | :--- |
| [**Homelab & Infrastructure**](homelab/README.md) | Systems architecture, NixOS migrations, DNS, CI/CD, and `appctl`. | [NixOS Server & Laptop Migration](homelab/nixos-server-laptop-migration.md)<br>[Domain Migration (`roadtotech.me`)](homelab/domain-migration-roadtotech.md)<br>[Appctl & Repositories Architecture](homelab/homelab-appctl-architecture.md)<br>[CI/CD & Deployment Strategy](homelab/deployment-and-cicd-strategy.md)<br>[Production Folder Structure](homelab/folder-structure-reorganization.md) |
| [**Projects**](projects/README.md) | Active software projects, architecture notes, and feature roadmaps. | [MagNetFlix](projects/magnetflix.md)<br>[Nekoweb](projects/nekoweb.md) |
| [**Learning & Growth**](learning/README.md) | Academic tracking, residency curriculum milestones, and notes. | [Backend Residency Roadmap](learning/backend-residency.md) |

---

## 🎯 Active Strategic Goals

1. **Host Roles Separation**: Transition the desktop workstation into a dedicated 24/7 headless NixOS production server, making the laptop the primary graphical workstation.
2. **Domain Migration**: Move from Dynu's free subdomain (`arch-services.mywire.org`) to owned domain (`roadtotech.me`).
3. **Repository Decoupling**: Extract monolithic deployments into standalone Git repositories with CI/CD and manage lifecycles using `appctl`.
4. **Clean Production State**: Remove non-production and development artifacts from the server machine.
