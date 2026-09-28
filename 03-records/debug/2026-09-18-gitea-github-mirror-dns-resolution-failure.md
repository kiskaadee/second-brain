---
type: debug
project: homelab
date: 2026-09-18
tags:
  - operations
  - homelab
  - troubleshooting
  - gitea
  - docker
  - dns
  - nixos
---

# Incident RCA: Gitea GitHub Mirror Push Failure & Docker DNS Forwarder Resolution

## Problem Statement

Push mirrors configured in Gitea (`gitea.roadtotech.me`) failed to synchronize repositories (`homelab-core`, `homelab-jellyfin`, `homelab-dashboard`, `homelab-doc2site`) with their respective upstream GitHub mirrors.

The Gitea error log sample:
```text
2026/09/18 12:05:33 .../mirror/mirror_push.go:166:runPushSync.1() [E] Error pushing kiskaadee/homelab-core.git mirror[7] remote remote_mirror_VijgRZ3O0n: push failed: exit status 128 - fatal: unable to access 'https://github.com/kiskaadee/homelab-core/': Could not resolve host: github.com (DNS server returned general failure)
```

---

## Research & Hypotheses

1. **GitHub Outage / Network Partition**: Upstream GitHub DNS or network availability issues.
2. **Host DNS Outage**: ISP DNS servers (`200.21.200.10`, `200.21.200.80`) unreachable from the physical host.
3. **Docker Embedded DNS Forwarder Race Condition**: Docker daemon initialized before host DHCP `/etc/resolv.conf` was established, leaving the internal `127.0.0.11` resolver without upstream forwarders.

---

## Diagnostics & Findings

1. **Host Connectivity & Upstream DNS**:
   * Host DNS resolution (`getent hosts github.com`) succeeded on `server` (`192.168.1.36`).
   * Ping and direct queries to Cloudflare (`1.1.1.1`) and ISP DNS servers succeeded.
2. **Container DNS Inspection**:
   * Inside the `gitea` container, `nslookup github.com` directly against `1.1.1.1` and `200.21.200.10` succeeded.
   * However, querying the embedded Docker resolver (`127.0.0.11`) failed with `SERVFAIL`.
3. **Container `/etc/resolv.conf` Metadata**:
   * Inspecting `/etc/resolv.conf` inside the running `gitea` container showed:
     ```text
     # Based on host file: '/etc/resolv.conf' (internal resolver)
     # NO EXTERNAL NAMESERVERS DEFINED
     ```
   * Newly spawned containers on the same `proxy-net` network showed:
     ```text
     # ExtServers: [host(200.21.200.10) host(200.21.200.80)]
     ```
4. **Root Cause**:
   Docker daemon and the container stack started during early boot before NetworkManager had fully populated `/etc/resolv.conf`. Consequently, the embedded DNS server recorded no upstream external nameservers, persisting `SERVFAIL` responses until container restart.

---

## Remediation / Fix

### 1. Immediate Runtime Recovery
Restarted the Gitea container via SSH to immediately refresh its DNS forwarders:
```bash
ssh server-local "docker restart gitea"
```
Verified that `docker exec gitea curl -I https://github.com` returned `HTTP/2 200`.

### 2. Permanent Declarative NixOS Configuration
Configured static fallback DNS servers for the Docker daemon in `Core/nixos/configuration.nix` to prevent boot race conditions:
```nix
  # ── Virtualisation ───────────────────────────────────────────────────────────
  virtualisation.docker = {
    enable = true;
    daemon.settings = {
      dns = [ "1.1.1.1" "1.0.0.1" ];
    };
  };
```

### 3. Validation & Rollout
* Verified with `nix flake check /home/kiskaadee/Homelab/Core` (all 35 invariant and structural checks passed).
* Committed (`d119ca1: fix(docker): configure static DNS daemon settings to prevent container DNS lookup failure`) and pushed to `main`.

---

## Results & Verification

* Gitea push mirror triggers completed with exit code 0.
* Verified that manual push syncs for all mirrored repositories now succeed with no DNS failures.

---

## Takeaways & Prevention

* **Static Docker Daemon DNS**: Always provide explicit fallback DNS servers (`daemon.settings.dns`) in NixOS host definitions rather than relying solely on ephemeral DHCP `/etc/resolv.conf` states.
