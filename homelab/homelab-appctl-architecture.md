# 📦 Homelab Architecture: Appctl & Independent Repositories

## 🎯 Vision & Goals
1. **Decouple Deployments**: Break monolithic multi-service compose stacks into isolated, independently version-controlled Git repositories.
2. **First-Class Orchestrator (`appctl`)**: Standardize service lifecycle management (start, stop, logs, update, backup, healthcheck) via `appctl`.

---

## 🏛️ Architecture Model

```text
/home/kiskaadee/Production/ (or /srv/deployments/)
├── core-ingress/          # Traefik, Authelia, Socket-Proxy (Git repo)
├── gitea/                 # Gitea & Gitea Actions runner (Git repo)
├── jellyfin/              # Media server stack (Git repo)
├── magnetflix/            # MagNetFlix app & microservices (Git repo)
├── nekoweb/               # Haruneko / Nekoweb deployments (Git repo)
└── docs/                  # Astro / Starlight documentation (Git repo)
```

Each service directory contains:
- `compose.yaml` (clean, self-contained Docker Compose file)
- `.env` / environment variable template linked to `/run/secrets/`
- Custom Dockerfiles or build scripts if applicable

---

## ⚙️ `appctl` Responsibilities

`appctl` acts as the unified CLI wrapper across all production services:
- `appctl list`: Discover registered production services and their operational statuses.
- `appctl up <app>`: Start container stack using standard networks (`proxy-net`, `socket-net`).
- `appctl down <app>`: Gracefully stop container stack.
- `appctl restart <app>`: Restart service.
- `appctl pull <app>`: Pull latest container images and trigger zero-downtime recreation.
- `appctl logs <app> [-f]`: Stream container logs.
- `appctl status <app>`: Inspect health status and resource consumption.
