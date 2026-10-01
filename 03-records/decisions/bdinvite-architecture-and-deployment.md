---
type: decision
status: accepted
project: bdinvite
date: 2026-10-01
tags:
  - architecture
  - fastapi
  - react
  - traefik
  - authelia
  - docker
  - security
---

# BDInvite Single-Container Architecture, Split Traefik Routing & ForwardAuth Integration

## Context and Problem Statement

When deploying lightweight, event-specific web applications (such as the interactive birthday invitation `bdinvite` with guest RSVP and admin management) into the personal homelab ecosystem at `roadtotech.me`, the infrastructure must balance developer ergonomics, resource efficiency, and perimeter security.

The application requires:
1. A frictionless, zero-barrier public portal for guests to view event details and submit RSVPs.
2. A strictly secured administration portal for reviewing the guest list, exporting CSVs, and editing event configuration in real time.
3. Hosting under a shared domain (`demos.roadtotech.me`) alongside future demonstration sites, without incurring unnecessary multi-container memory and orchestration overhead on the host.

How should the application packaging, edge ingress routing, and authentication boundaries be structured to satisfy these requirements?

---

## Decision Drivers

* **Resource Footprint & Operational Simplicity**: Avoid deploying multi-container stacks (separate Nginx reverse proxy containers, dedicated database daemons, or separate frontend webservers) for small micro-sites.
* **Perimeter Security without Auth Duplication**: Protect administrative endpoints using the platform's central single sign-on (Authelia SSO over ForwardAuth) rather than implementing custom username/password forms, JWT sessions, or credential databases inside the application.
* **Granular Access Control on a Single Subdomain**: Allow public guest access on `demos.roadtotech.me/birthday` while enforcing SSO strictly on `demos.roadtotech.me/birthday/admin*`.
* **Zero External Data Leakage & Offline Resilience**: Prevent client browsers from making runtime requests to third-party CDNs (such as Google Fonts) to preserve guest privacy and guarantee aesthetic consistency across all devices.
* **Defense-in-Depth**: Ensure administrative API routes cannot be accessed anonymously even if edge routing rules are misconfigured or bypassed.

---

## Considered Options

* **Option 1: Multi-Container Microservices Stack** — Separate Nginx container serving the static React build, separate FastAPI container for the API, and an external PostgreSQL database container, managed via Docker Compose.
* **Option 2: Single-Container Multi-Stage Build with Embedded SQLite and Split Traefik Routing** — Single container containing the compiled React SPA served directly by FastAPI and `uvicorn`, SQLite WAL database persisted on a volume mount, and Traefik path-based priority routing with Authelia ForwardAuth.
* **Option 3: External Jamstack / Serverless Form Integration** — Static site hosted on GitHub Pages or Cloudflare Pages, forwarding RSVPs to a third-party form aggregator (Airtable or Formspree).

---

## Decision Outcome

Chosen option: **Option 2: Single-Container Multi-Stage Build with Embedded SQLite and Split Traefik Routing**, because it maximizes operational simplicity and resource efficiency on the homelab host while maintaining strict defense-in-depth security and full data sovereignty.

### Summary of Architectural Commitments

1. **Single-Container Multi-Stage Deployment**:
   - The production container is built using a two-stage Dockerfile: Stage 1 (`node:20-alpine`) compiles the Vite React 19 application; Stage 2 (`ghcr.io/astral-sh/uv:python3.11-bookworm-slim`) installs Python dependencies and copies the compiled `dist/` directory into `./static`.
   - FastAPI serves both API endpoints under `/birthday/api/*` and the static SPA assets under `/birthday/assets/*`, routing all unhandled sub-paths under `/birthday/*` to `static/index.html` to support client-side React Router navigation.

2. **Split Path-Based Routing & Ingress Priority**:
   - The workload exposes container port 8000 to the shared `proxy-net` network.
   - Traefik defines two overlapping HTTPS routers on `demos.roadtotech.me`:
     - **Public Router (`bdinvite-public`)**: Rule `Host(\`demos.roadtotech.me\`) && PathPrefix(\`/birthday\`)`, `priority: 10`, no authentication middleware.
     - **Admin Router (`bdinvite-admin`)**: Rule `Host(\`demos.roadtotech.me\`) && PathPrefix(\`/birthday/admin\`)`, `priority: 20`, middleware `authelia-auth@docker`.
   - Because Traefik prioritizes higher-priority rules, any request beginning with `/birthday/admin` is intercepted by Authelia ForwardAuth before reaching the container, while all other `/birthday` requests remain publicly accessible.

3. **Defense-in-Depth Backend Identity Verification**:
   - The application does not manage passwords or tokens.
   - When an admin request is authenticated, Authelia forwards the `Remote-User` header to the backend.
   - Every administrative API endpoint under `/birthday/api/admin/*` enforces a FastAPI dependency requiring the presence of `Remote-User`. Requests missing this header immediately return HTTP 401 Unauthorized, ensuring that private endpoints are secured independently of edge proxy behavior.

4. **Self-Hosted Typography & Static Asset Isolation**:
   - Brand fonts (`Playfair Display` and `Plus Jakarta Sans`) are packaged locally as `.woff2` files within `frontend/src/fonts/` and imported into CSS bundle assets.
   - Runtime dependencies on Google Fonts or external CDNs are strictly prohibited, ensuring zero external referrer tracking and guaranteed availability.

5. **Persistence Isolation via SQLite WAL**:
   - Data is stored in `./data/bdinvite.db` using SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
   - The database file is mounted from the host filesystem, providing full durability, instant atomic backups, and zero background daemon memory consumption.

---

## Pros and Cons of the Options

### Option 1: Multi-Container Microservices Stack
* Good, because it adheres to classic separation of static content from API processes.
* Good, because Nginx is highly optimized for static file delivery.
* Bad, because running 2–3 containers (Nginx, FastAPI, Postgres) for a small event invitation wastes container memory and orchestrator overhead.
* Bad, because managing inter-container networking for a single micro-workload increases Compose configuration complexity.

### Option 2: Single-Container Multi-Stage Build with Embedded SQLite and Split Traefik Routing (Adopted)
* Good, because total runtime overhead is confined to a single lightweight Python process consuming minimal RAM.
* Good, because deployments and updates are atomic: updating the container image deploys synchronized frontend and backend changes simultaneously.
* Good, because edge authentication is fully offloaded to central Authelia SSO without duplicating identity code.
* Good, because SQLite WAL mode provides concurrent read performance and zero maintenance operations.
* Bad, because static file delivery is handled by Starlette/FastAPI rather than dedicated Nginx; however, for the expected traffic scale of an invitation site, FastAPI's async file response is more than sufficient.

### Option 3: External Jamstack / Serverless Form Integration
* Good, because zero host resources are consumed.
* Bad, because it sacrifices data sovereignty and stores personal guest contact information (names, phone numbers) on third-party servers.
* Bad, because it breaks homelab platform integration, making unified monitoring, SSO, and local backups impossible.

---

## Consequences

### Positive Consequences
* **Streamlined Operations**: The workload can be inspected, stopped, restarted, or updated via a single `appctl` invocation (`appctl update bdinvite`).
* **Robust Access Boundary**: Guests experience zero friction when confirming attendance, while administrative dashboards and CSV exports remain safely behind multi-factor SSO.
* **Hermetic Local Development**: Developers can run the backend and frontend together or independently using the local Nix devShell (`nix develop`) without configuring local reverse proxies.

### Negative Consequences & Accepted Trade-offs
* **Path Prefix Sensitivity**: Frontend build assets and React Router must explicitly be configured with base path `/birthday` (`base: '/birthday/'` in Vite, `basename="/birthday"` in React Router) to avoid root path collisions on `demos.roadtotech.me`.
* **Traefik Priority Dependency**: Edge security relies on explicit Traefik router priorities (`priority: 20` for admin vs. `priority: 10` for public); however, this risk is mitigated by the mandatory `Remote-User` backend defense-in-depth check.

---

## More Information

* **Project Hub**: [BDInvite Project Hub](../../06-projects/bdinvite/README.md)
* **Infrastructure Context**: [Homelab Ecosystem & Core Infrastructure](../../06-projects/homelab/README.md)
* **Workstation DevShell & Tooling**: [Biome Monorepo VCS Symmetry](../../04-learning/knowledge/technologies/biome-monorepo-vcs-symmetry.md)
