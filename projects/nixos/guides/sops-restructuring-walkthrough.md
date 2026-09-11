---
type: guide
project: nixos
tags:
  - nixos
  - sops
  - secrets
  - authelia
---

# Walkthrough: SOPS Secrets Restructuring & Multi-User Authelia Support

Restructured the flat SOPS secrets into clean, service-first namespaces (`authelia/*`, `traefik/*`, `dynu/*`, `postgres/*`, `mongo/*`, `ollama/*`, `gitea/*`, `learning/*`, `system/*`) and added declarative multi-user support for Authelia in NixOS.

---

## What Changed

### 1. Re-encrypted Secrets (`~/Config/hosts/server/secrets.yaml`)
Restructured all flat keys into nested YAML mappings encrypted with Age:
* **`authelia/`**:
  * `session_secret`, `storage_encryption_key`, `jwt_secret`
  * `users/kiskaadee/password_hash`
  * `users/misa/password_hash`
  * `users/valenvg/password_hash`
* **`traefik/`**: `acme_email`
* **`dynu/`**: `api_key`, `user`, `domain`, `password`
* **`postgres/`**: `user`, `password`, `db`
* **`mongo/`**: `root_username`, `root_password`
* **`ollama/`**: `api_key`
* **`gitea/`**: `runner_token`
* **`learning/`**: `turso_db_url`, `turso_auth_token`
* **`system/`**: `gh_repo_token`, `pdf_decrypt_password`

### 2. Declarative Authelia User Schema (`~/Config/hosts/server/homeserver.nix`)
* Defined a declarative `autheliaUsers` map in Nix containing metadata (display name, email, group memberships) for `kiskaadee`, `misa`, and `valenvg`.
* Configured `sops.templates."users.yml"` to dynamically generate the Authelia user database at `/run/secrets/rendered/users.yml` using `config.sops.placeholder."authelia/users/<username>/password_hash"`.
* Updated all core secret placeholders (`authelia/*`, `traefik/*`, `dynu/*`).

### 3. Application & DDNS Modules
* **[`hosts/server/traefik-deployments.nix`](file:///home/kiskaadee/Config/hosts/server/traefik-deployments.nix)**: Updated secret references to service-scoped keys (`postgres/*`, `mongo/*`, `ollama/*`, `learning/*`, `gitea/*`).
* **[`hosts/server/dynu.nix`](file:///home/kiskaadee/Config/hosts/server/dynu.nix)**: Updated DDNS configuration placeholders to `dynu/*` and `system/pdf_decrypt_password`.

---

## Verification Results

### 1. SOPS Decryption & Round-trip Verification
Decrypted `secrets.yaml` with `sops -d` to confirm every value parses correctly into the target hierarchy.

### 2. NixOS Flake Dry-Build
Evaluated and built derivations for `server` host (`nixos-rebuild dry-build --flake .#server`), confirming all 4 templates (`users.yml`, `homeserver.env`, `traefik-deployments.env`, `ddclient.conf`) evaluate cleanly.

---

## Deployment Instructions

To activate the changes on the target server host:

```bash
cd ~/Config
sudo nixos-rebuild switch --flake .#server
```

Once activated, restart Authelia to load the new users database:
```bash
appctl restart authelia
```
