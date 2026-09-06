# 🛡️ Custom API Security Hardening & Threat Analysis

## 🎯 Objective
Address identified attack surfaces and implement defense-in-depth hardening across custom microservices and APIs in the homelab ecosystem, specifically the **Learning Hub API** (`learning.roadtotech.me`) and the **Minecraft Identity Manager Web Admin** (`minecraft.roadtotech.me`).

---

## 🔍 Identified Attack Surfaces & Risk Assessment

### 1. Learning Hub API (`homelab-dashboard/learning`)
* **Endpoint**: `https://learning.roadtotech.me` / `learning-hub:8000`
* **Risks**:
  - **Unauthenticated Mutating Routes**: `POST /api/courses`, `PUT /api/courses/{id}`, and `DELETE /api/courses/{id}` in `app/routes.py` do not enforce authentication, allowing anyone on the Internet to alter the Turso cloud database.
  - **Overly Permissive CORS**: `allow_origins=["*"]` allows arbitrary web origins to send requests.
  - **Rate Limiting / DoS**: No request throttling or quota enforcement on database writes.

### 2. Minecraft Identity Manager Web Admin (`homelab-minecraft/web`)
* **Endpoint**: `https://minecraft.roadtotech.me` / `minecraft-web-admin:8000`
* **Risks**:
  - **Fallback JWT Secret**: In `docker-compose.yml`, `JWT_SECRET` defaults to a known hardcoded string if `MINECRAFT_JWT_SECRET` is unset, which could permit offline JWT forgery.
  - **Direct SQLite File Concurrency**: Web admin shares read/write access to AuthMe's `./data/plugins/AuthMe/authme.db` while PaperMC is running.
  - **Password Reset Flooding**: Unauthenticated `/api/auth/reset-request` endpoint could be spammed by automated bots without rate limiting.

---

## 📋 Security Hardening Action Items & Roadmap

### Priority 1: High Impact (Authentication & Secret Integrity)
- [ ] **Enforce Authelia SSO or API Key on Learning Hub API**
  - Option A: Attach `traefik.http.routers.learning.middlewares=authelia-auth@docker` in `homelab-dashboard/docker-compose.yml`.
  - Option B: Add API Token / Bearer Header dependency for mutating routes in `app/routes.py`.
- [ ] **Fail-Fast on Insecure JWT Secret in Minecraft Web Admin**
  - Ensure `MINECRAFT_JWT_SECRET` is supplied exclusively via SOPS template (`/run/secrets/rendered/traefik-deployments.env`).
  - Add startup validation in `web/main.py` to abort immediately if `JWT_SECRET` equals the default fallback string.

### Priority 2: Medium Impact (Rate Limiting & Ingress Filtering)
- [ ] **Attach Traefik Rate Limiting Middlewares**
  - Add `traefik.http.middlewares.learning-ratelimit.ratelimit.average=50` to prevent database exhaustion.
  - Add `traefik.http.middlewares.minecraft-ratelimit.ratelimit.average=30` to protect login and reset request endpoints.
- [ ] **Restrict CORS in Learning Hub API**
  - Restrict `allow_origins` in `app/main.py` to `["https://dashboard.roadtotech.me", "https://learning.roadtotech.me"]`.

---

## 🔒 Implemented Security Hardening History

- [x] **Socket Proxy Read-Only Enforcement (`2026-09-04`)**
  - Configured `POST=0` and `DELETE=0` on `tecnativa/docker-socket-proxy` in `Core/docker-compose.yml` to prevent arbitrary container creation/destruction from `socket-net`.
- [x] **Git Tracking Hygiene & Secrets Removal (`2026-09-04`)**
  - Removed and ignored `config/authelia/users.yml` from `~/Core`.
  - Ignored compiled `homelab-dashboard/config/services.yaml`.
  - Verified all database files (`*.db`, `*.sqlite3`), `.env` files, and SSL keys are covered by `.gitignore`.
- [x] **Let's Encrypt DNS-01 Wildcard SSL (`2026-09-04`)**
  - Fixed Traefik CLI flags and provisioned valid wildcard certs for `roadtotech.me` and `*.roadtotech.me`.
