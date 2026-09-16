---
type: guide
project: homelab
tags:
  - operations
  - security
  - architecture
  - homelab
  - lldap
  - authelia
  - auth
  - gitops
---

# LLDAP + Authelia Integration & Pre-Commit Quality Gate Walkthrough

## Summary of Completed Implementations

### 1. Repository Tests in Pre-Commit Hook
- **Hook Location**: `.githooks/pre-commit` (executable, tracked in git).
- **Git Hooks Path**: Configured via `git config core.hooksPath .githooks` on both local dev and production server environments.
- **Flake Integration**: `flake.nix` now includes a `shellHook` that automatically ensures `core.hooksPath` is registered whenever entering the Nix development shell.
- **Structural Invariant Test**: Added `.githooks/pre-commit` presence and executable bit verification in `tests/structural/test_repository_structure.py`.
- **Verification**: Verified automatically on `git commit` — executes Ruff linter and the full 35 Pytest invariant tests in ~0.12s before allowing commits.

---

### 2. LLDAP Service & Dynamic User Backend
- **Service Container**: `nitnelave/lldap:stable` deployed in `docker-compose.yml` on `proxy-net`.
- **Public Admin & Self-Service UI**: [https://users.roadtotech.me](https://users.roadtotech.me) (secured with Traefik TLS ACME certificate).
- **Internal LDAP Endpoint**: `ldap://lldap:3890` with Base DN `dc=roadtotech,dc=me`.
- **Decoupled SOPS Secrets**:
  - `LLDAP_JWT_SECRET`
  - `LLDAP_KEY_SEED`
  - `LLDAP_LDAP_USER_PASS` / `AUTHELIA_LDAP_PASSWORD`
  - Added to encrypted `nixos/secrets.yaml` and exposed via `nixos/modules/homeserver.nix`.

---

### 3. Authelia LDAP Reconfiguration
- **Backend Switched**: `config/authelia/configuration.yml` replaced the static `file` backend with `ldap` pointing to `ldap://lldap:3890`.
- **Users File Removed**: Removed `/run/secrets/rendered/users.yml:/config/users.yml:ro` mount from Authelia.
- **Bypass Rule**: Added `users.{{ env "DOMAIN" }}` to Authelia's bypass list so users can access LLDAP's login and self-service portal directly.
- **Appctl Integration**: Registered `lldap` under **Core Infrastructure** in `scripts/appctl_engine.py` and Homepage dashboard card (`lldap.png` icon).

---

### 4. Directory Seeding & Verification
- Created `scripts/bootstrap_lldap_users.py`.
- Groups created in LLDAP: `admins`, `dev`, `users`.
- Users migrated:
  - `kiskaadee` (`fcortesbio@gmail.com`) -> Groups: `admins`, `dev`
  - `misa` (`icdf0728@gmail.com`) -> Groups: `users`
  - `valenvg` (`vegavalentina069@gmail.com`) -> Groups: `users`
- **Live Authelia Authentication Test**:
  - `POST https://auth.roadtotech.me/api/firstfactor` verified in real time: returns `{"status":"OK"}` for valid LLDAP credentials and rejects invalid passwords.

---

## Managing Users Going Forward (Zero Secrets Touched)

### Web Interface
Navigate to **[https://users.roadtotech.me](https://users.roadtotech.me)**:
1. Log in as `admin` (or as user `kiskaadee` with admin privileges).
2. **Add User**: Click **Add user**, enter display name, username, and email.
3. **Assign Groups**: Assign `admins`, `dev`, or `users` with checkboxes.
4. **Reset/Set Passwords**: Click on the user -> **Change password** or send an invitation link.
5. Changes take effect in Authelia **immediately** with zero downtime and without modifying any git files or SOPS secrets.

### CLI Password Reset
To set/reset any user's password from the server terminal:
```bash
docker exec lldap /app/lldap_set_password \
  --base-url http://localhost:17170 \
  --admin-username admin \
  --admin-password <ADMIN_PASSWORD> \
  --username <USERNAME> \
  --password <NEW_PASSWORD>
```
