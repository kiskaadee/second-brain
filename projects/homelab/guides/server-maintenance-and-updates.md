---
type: guide
project: homelab
tags:
  - homelab
  - nixos
  - maintenance
  - systemd
  - docker
---

# 🛠️ Server Maintenance and System Updates Runbook

This runbook outlines routine maintenance procedures for the **Homelab Core** appliance, including NixOS system upgrades, service health verification, garbage collection, and Docker pruning.

---

## 🔄 Updating the NixOS Server Appliance

The server operating system is defined entirely inside `~/Core`.

### Step 1: Update Flake Inputs
To fetch the latest versions of Nixpkgs and `sops-nix`:

```bash
cd ~/Core
nix flake update
```

### Step 2: Validate the Build Dryly
Always dry-build before switching to catch compilation, syntax, or package evaluation errors:

```bash
nix flake check
nix build .#nixosConfigurations.server.config.system.build.toplevel --no-link
```

### Step 3: Switch to the New System Generation
Once the dry build completes cleanly:

```bash
sudo nixos-rebuild switch --flake ~/Core#server
# (or simply run: nix-switch)
```

---

## 🏥 Post-Update Health Checklist

Run this quick verification checklist following any system switch or server reboot:

1. **Systemd Daemon Health**:
   Ensure no core background units failed:
   ```bash
   systemctl --failed
   ```

2. **Core Homelab Stack**:
   Verify Traefik, Authelia, and the control plane containers are active:
   ```bash
   systemctl status homeserver-core.service
   ```

3. **Dynamic DNS (Dynu) Monitor**:
   Ensure the IP change detector timer and service are active:
   ```bash
   systemctl status dynu-monitor.timer
   systemctl status dynu-monitor.service
   ```

4. **GitOps Webhook Dispatcher**:
   Verify the webhook listener is listening on port 9000:
   ```bash
   systemctl status homelab-gitops.service
   ```

5. **Secrets Integrity**:
   Verify rendered environment files were generated in RAM:
   ```bash
   sudo ls -la /run/secrets/rendered/
   ```

6. **Application Workload Status**:
   Inspect the status of all application stacks:
   ```bash
   appctl list
   ```

---

## 🧹 Disk Space Reclamation & Garbage Collection

Over time, older Nix generations, build artifacts, and Docker layers accumulate on disk. Follow this clean-up routine:

### 1. Collect Nix Garbage
To prune unreachable store paths and older generations:

```bash
# Delete older system generations (older than 7 days)
sudo nix-env --delete-generations +7d --profile /nix/var/nix/profiles/system

# Prune the store
sudo nix-collect-garbage -d
```

### 2. Prune Unused Docker Resources
Remove dangling container images, stopped containers, and build cache:

```bash
# Prune dangling images and build cache safely
docker system prune -a --volumes --filter "until=168h"
```
*(Only prunes containers stopped for longer than 7 days).*

---

## 🚨 Emergency System Rollback

If a newly applied NixOS generation causes system issues:

```bash
# Roll back to the previous generation immediately
sudo nixos-rebuild switch --rollback
```
*(Or select the previous generation from the systemd-boot menu upon reboot).*
