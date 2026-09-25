---
type: debug
project: homelab
date: 2026-09-24
tags:
  - operations
  - homelab
  - troubleshooting
  - diun
  - docker
  - stalwart
  - smtp
  - sops
---

# Incident RCA & Architectural Tuning: Diun Load-Shaping, Workload Exemption & Authenticated SMTPS Delivery

## System Context & Fundamentals

The `roadtotech.me` homelab operates an autonomous container image update notifier ([Diun](https://crazymax.dev/diun/)) in the Core Compose stack. Diun queries Docker state via `socket-proxy` (`tcp://socket-proxy:2375`) and dispatches notification emails through the local Stalwart mail server (`stalwart`).

Platform boundaries follow a clear operational contract:
* **Core Platform**: Manages shared infrastructure, platform listeners, secrets, and global scanner defaults (`DIUN_PROVIDERS_DOCKER_WATCHBYDEFAULT=true`).
* **Sites Workloads**: Independent application stacks (`Sites/*`) that declare workload-specific traits and exemptions.

---

## Problem & Initial Observations

Following the initial Diun setup and routine operational monitoring, several distinct classes of issues and warnings emerged across container and mail logs:

1. **Compose Variable Warning**:
   ```text
   WARN[0000] The "PxkuR3uP0bQtqJnPfehtenptbPl" variable is not set. Defaulting to a blank string.
   ```
2. **Registry Manifest DNS Timeouts**:
   ```text
   WRN Cannot get remote manifest error="... dial tcp: lookup registry-1.docker.io on 127.0.0.11:53: read udp ...: i/o timeout"
   ```
3. **Startup Socket Proxy Race**:
   ```text
   ERR Cannot create Docker client error="Cannot connect to the Docker daemon at tcp://socket-proxy:2375. Is the docker daemon running?"
   ```
4. **Registry Access Denied on Local Builds**:
   ```text
   WRN Cannot get remote manifest error="reading digest latest in docker.io/library/homelab-doc2site-docs: requested access to the resource is denied"
   WRN Cannot get remote manifest error="reading digest latest in docker.io/library/homelab-minecraft-web: requested access to the resource is denied"
   ```
5. **Notification Distrusted & Spam Flagging**:
   Alert emails arriving from `diun@roadtotech.me` displayed a maximum red spam score bar in SnappyMail and routed directly to the `Junk` mailbox.
6. **Port 587 Submission Connection Refusal**:
   When configuring authenticated submission on standard STARTTLS port 587, Diun reported:
   ```text
   dial failed: dial tcp 172.18.0.16:587: connect: connection refused
   ```

---

## Diagnostic Inquiries & Root Cause Analysis

### 1. Bcrypt Variable Interpolation in Docker Compose

* **Investigation**: Grepping the variable name across the server environment revealed it originated from `PORTAINER_ADMIN_PASSWORD` in `/run/secrets/rendered/homeserver.env`. Portainer's bcrypt string (`$2y$05$...`) contained three `$` delimiters. The first two were escaped (`$$2y$$05`), but the third was left unescaped before the salt/hash string `PxkuR3uP0bQtqJnPfehtenptbPl`. Docker Compose parsed it as a variable reference and defaulted it to a blank string.
* **Resolution**: Portainer was subsequently deprecated and cleanly pruned from the entire Core platform (containers, SOPS secrets, volumes, and docs), naturally eliminating this warning and corrupt password state.
  - See: [Core Service Qualification & Portainer Deprecation](../../projects/homelab/discussions/core-service-qualification-and-portainer-deprecation.md)

### 2. High-Concurrency Registry Scan vs. DNS Blip

* **Investigation**: During a single scan at 13:26:18 UTC, 22 images were evaluated concurrently with `DIUN_WATCH_WORKERS=20`. Subsequent runs succeeded cleanly across the exact same public registries without code changes.
* **Epistemic Distinction**: The 20 concurrent workers were an **exacerbating load factor**, not the proven root cause of the network drop. Rather than diagnosing a persistent DNS failure, the appropriate engineering action was **load-shaping**:
  * **Concurrency Limit**: Reduced `DIUN_WATCH_WORKERS` from `20` to `6` to shape the peak request volume against Docker's internal DNS forwarder (`127.0.0.11:53`).
  * **Synchronization Limit**: Enabled `DIUN_WATCH_JITTER=30s` to randomize scheduled job dispatches and prevent simultaneous request bursts upon cron ticks.

### 3. Startup Readiness Race

* **Investigation**: `ERR Cannot create Docker client` occurred exclusively during the sub-second window of `docker compose restart`.
* **Mechanism**: Standard Compose `depends_on: [socket-proxy]` gates container startup, not TCP port readiness. Because Diun boots in under 50ms, it probes port 2375 before HAProxy finishes binding its listener.
* **Decision**: Accepted as benign transient startup noise (Option A). Diun handles the initial connection failure gracefully and runs its periodic cron triggers without issue once `socket-proxy` binds.

### 4. Decentralized Workload Image Exemption

* **Investigation**: `homelab-doc2site-docs` and `homelab-minecraft-web` are locally built images (`build: .`) without remote registry mirrors. With `watchByDefault=true`, Diun assumed Docker Hub as the default registry and queried `docker.io/library/*`, which returned 401 Unauthorized.
* **Architectural Fix**: Maintained decentralized workload ownership by adding `diun.enable=false` directly to the application manifests:
  * `Sites/doc2site/docker-compose.yml` (`docs` service)
  * `Sites/minecraft/docker-compose.yml` (`web` service)
  Core continues to watch by default, while workloads explicitly opt out if they do not publish to remote registries.

### 5. Inbound Mail Trust & Stalwart Listener Topography

* **Investigation**:
  * Diun's mail notifier does not support arbitrary custom headers.
  * When sending unauthenticated mail over port 25 claiming to be `@roadtotech.me`, Stalwart treated it as external ingress. Because the internal Docker bridge IP (`172.18.0.x`) does not match the public SPF record for `roadtotech.me` and lacked DKIM or SMTP AUTH, Stalwart's anti-spoofing engine penalized it as a forged sender.
  * Probing Stalwart's active listener catalog revealed:
    * `listenerId = "smtp"` (Port 25): Active, but explicitly disables authentication (MTA ingress only).
    * `listenerId = "submission"` (Port 587): Disabled / inactive in Stalwart.
    * `listenerId = "submissions"` (Port 465): Active, listening with implicit TLS (SMTPS), and enforcing `AUTH PLAIN LOGIN XOAUTH2 OAUTHBEARER`.
* **Architectural Fix**:
  * Created dedicated service account `notifier@roadtotech.me` in LLDAP.
  * Encrypted password in `nixos/secrets.yaml` under `diun/smtp_password` and projected it declaratively into `/run/secrets/rendered/homeserver.env` via `homeserver.nix`.
  * Configured Diun to use **Port 465 with implicit TLS (`DIUN_NOTIF_MAIL_SSL=true`)** and aligned sender identity `DIUN_NOTIF_MAIL_FROM=notifier@${DOMAIN:-roadtotech.me}`.

---

## Declarative Remediation Summary

### `Core/docker-compose.yml`

```yaml
      - DIUN_WATCH_WORKERS=6
      - DIUN_WATCH_JITTER=30s
      - DIUN_WATCH_SCHEDULE=0 */6 * * *
      - DIUN_NOTIF_MAIL_HOST=stalwart
      - DIUN_NOTIF_MAIL_PORT=465
      - DIUN_NOTIF_MAIL_USERNAME=notifier@${DOMAIN:-roadtotech.me}
      - DIUN_NOTIF_MAIL_PASSWORD=${DIUN_SMTP_PASSWORD}
      - DIUN_NOTIF_MAIL_SSL=true
      - DIUN_NOTIF_MAIL_INSECURESKIPVERIFY=true
      - DIUN_NOTIF_MAIL_FROM=notifier@${DOMAIN:-roadtotech.me}
      - DIUN_NOTIF_MAIL_TO=kiskaadee@${DOMAIN:-roadtotech.me}
```

### `Core/nixos/modules/homeserver.nix`

```nix
  sops.secrets = lib.genAttrs [
    # ...
    "diun/smtp_password"
  ] (name: { owner = "kiskaadee"; });

  sops.templates."homeserver.env" = {
    owner = "kiskaadee";
    content = lib.generators.toKeyValue {} {
      # ...
      DIUN_SMTP_PASSWORD = config.sops.placeholder."diun/smtp_password";
    };
  };
```

### `Sites/doc2site/docker-compose.yml` & `Sites/minecraft/docker-compose.yml`

```yaml
    labels:
      - "diun.enable=false"
      - "traefik.enable=true"
```

---

## Post-Deployment Verification

1. **Image Scan & Filtering Output**:
   ```text
   INF Found 19 image(s) to analyze provider=docker
   INF Jobs completed added=0 failed=0 skipped=0 unchanged=19 updated=0
   INF Cron initialized with schedule 0 */6 * * *
   INF Next run in 53 minutes (2026-09-25 00:00:27.868114284 +0000 UTC)
   ```
   * Monitored exactly 19 upstream images (22 minus Portainer [1] and local custom builds [2]).
   * Zero failures (`failed=0`).
   * Jitter active (`00:00:27` desynchronization).

2. **Mail Authentication & Delivery**:
   * Direct probe and Diun test notification succeeded:
     ```text
     Notification sent for mail notifier(s)
     ```
   * Stalwart logs confirmed authenticated submission:
     ```text
     INFO Authentication successful (auth.success)
         listenerId = "submissions", remotePort = 465, accountName = "notifier@roadtotech.me"
     INFO Delivery completed (delivery.completed)
         to = ["kiskaadee@roadtotech.me"], code = 250, details = "OK"
     ```
   * Messages land directly in `INBOX` with clean spam scores and `auth=pass` trust verification.

---

## Architectural Lessons Learned

1. **Load Shaping Over Speculative Repair**: Distinguish correlation from causation. When an external service experiences transient timeouts, avoid over-engineering network plumbing; use concurrency limits and desynchronization jitter to keep system load predictable.
2. **Workload Sovereignty in Declarative GitOps**: Exceptions belong to the domain that creates them. Local build exemptions belong in `Sites/*` compose manifests, keeping the Core platform generic and declarative.
3. **MTA Ingress vs. Client Submission Topography**:
   * Port 25 is strictly for unauthenticated MX exchange; internal infrastructure must never send unauthenticated alerts over port 25 claiming internal domain identities, as anti-spoofing filters will correctly penalize them.
   * Service accounts must authenticate via dedicated submission endpoints (Port 465 SMTPS / Port 587 STARTTLS) matching the specific active listeners of the mail appliance.

---

## Related

* [Diun Initial Integration & Socket Proxy RCA (2026-09-22)](../debug/2026-09-22-diun-socket-proxy-integration-and-stalwart-alerting.md) — Previous incident establishing the Diun foundation this session built upon.
* [Diun Documentation](https://crazymax.dev/diun/)
* [Stalwart Mail Server Docs](https://stalw.art/docs/)
