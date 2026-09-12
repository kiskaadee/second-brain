---
type: guide
project: homelab
tags:
  - homelab
  - sops
  - secrets
  - authelia
  - auth
---

# 🔐 Managing Secrets and Authelia Users

This guide describes how to update encrypted runtime secrets, add or modify Authelia user accounts, and generate secure password hashes in the **Homelab Core** appliance.

---

## 🏛️ How Secrets Work in Homelab Core

All secrets are encrypted with [SOPS](https://github.com/getsops/sops) using [age](https://github.com/FiloSottile/age) keys and stored inside `nixos/secrets.yaml` in the `~/Core` repository.

At server boot, the `sops-nix` systemd module decrypts these secrets and renders them to RAM-backed environment files:
- `/run/secrets/rendered/homeserver.env` — Consumed by Core infrastructure (Traefik, Authelia, Socket-Proxy).
- `/run/secrets/rendered/traefik-deployments.env` — Consumed by application workloads via `appctl`.
- `/run/secrets/rendered/users.yml` — The user database mounted into the Authelia container.

---

## 👤 Adding or Modifying Authelia Users

Authelia users are declared declaratively in `~/Core/nixos/modules/homeserver.nix`, while their password hashes are stored encrypted in `nixos/secrets.yaml`.

### Step 1: Generate an Argon2 Password Hash
Run the official Authelia CLI in a temporary container to compute a secure Argon2id hash:

```bash
docker run --rm -it authelia/authelia:latest authelia crypto hash generate argon2
```
Enter your password when prompted. The output will look like:
```text
$argon2id$v=19$m=65536,t=3,p=4$qH...
```

### Step 2: Store the Password Hash in SOPS
1. Navigate to the core repository:
   ```bash
   cd ~/Core
   ```
2. Open the encrypted secrets file:
   ```bash
   sops nixos/secrets.yaml
   ```
3. Add the user's password hash under `authelia.users`:
   ```yaml
   authelia:
     users:
       newuser:
         password_hash: "$argon2id$v=19$m=65536,t=3,p=4$..."
   ```
4. Save and close. SOPS will re-encrypt the file automatically.

### Step 3: Register the User in `homeserver.nix`
Open `nixos/modules/homeserver.nix` and add the user metadata to `autheliaUsers`:

```nix
autheliaUsers = {
  # Existing users...

  newuser = {
    displayName = "New User";
    email = "newuser@example.com";
    groups = [ "users" ]; # or [ "admins" "dev" ]
    passwordPlaceholder = config.sops.placeholder."authelia/users/newuser/password_hash";
  };
};
```
Also register the secret key in `sops.secrets`:
```nix
sops.secrets = lib.genAttrs [
  # Existing secrets...
  "authelia/users/newuser/password_hash"
] (name: { owner = "kiskaadee"; });
```

### Step 4: Apply the Update
Rebuild the NixOS server generation to regenerate `/run/secrets/rendered/users.yml` and reload Authelia:

```bash
sudo nixos-rebuild switch --flake ~/Core#server
docker restart authelia
```

---

## 🔑 Updating General Secrets (Tokens, DB Passwords, API Keys)

To update API keys or database passwords:

1. Open the encrypted file:
   ```bash
   sops ~/Core/nixos/secrets.yaml
   ```
2. Edit the required value (e.g. `dynu/api_key`, `postgres/password`).
3. Save and close.
4. Apply changes to the host:
   ```bash
   sudo nixos-rebuild switch --flake ~/Core#server
   ```
5. Restart affected container stacks using `appctl`:
   ```bash
   appctl restart <service-name>
   ```

---

## 🚨 Troubleshooting Secret Decryption

If a container fails to start due to missing environment variables:
1. Verify rendered secret files exist on the host:
   ```bash
   sudo ls -la /run/secrets/rendered/
   ```
2. Inspect the content of the generated environment file:
   ```bash
   sudo head /run/secrets/rendered/homeserver.env
   ```
3. Check `sops-nix` activation logs:
   ```bash
   systemctl status sops-nix.service
   ```
