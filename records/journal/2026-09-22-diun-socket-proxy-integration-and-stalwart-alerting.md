---
type: journal
project: homelab
date: 2026-09-22
tags:
  - operations
  - homelab
  - troubleshooting
  - diun
  - docker
  - stalwart
  - smtp
  - socket-proxy
---

# Incident RCA & System Integration: Diun Docker Provider Connectivity & Stalwart Mail Notification

## System Context & Fundamentals

The `roadtotech.me` homelab Core platform runs several platform and monitoring services inside a unified Docker Compose stack (`~/Core/docker-compose.yml`), orchestrated under NixOS.
* **`socket-proxy`**: A security barrier running HAProxy that exposes a strictly read-only Docker API subset (`POST=0`, `DELETE=0`) on the isolated `socket-net` network at `tcp://socket-proxy:2375`.
* **`diun`** (Docker Image Update Notifier): An autonomous scanner designed to inspect running containers, query remote image registries (Docker Hub, GHCR, Quay) for updated image digests/tags, and publish update notifications.
* **`stalwart`**: An all-in-one mail server handling inbound/outbound SMTP (25, 465, 587) and IMAPS (993) on `proxy-net`, using LLDAP for user authentication.

---

## Problem & Observations

The operator reported that Diun was failing to connect to the homelab infrastructure. Container logs displayed the following recurring pattern:

```text
diun | INF Starting Diun version=v4.33.0
diun | INF Configuration loaded from 5 environment variable(s)
diun | WRN No notifier available
diun | INF Cron triggered
diun | INF gRPC server listening addr=[::]:42286
diun | ERR Cannot create Docker client error="Cannot connect to the Docker daemon at tcp://socket-proxy:2375. Is the docker daemon running?" provider=docker
diun | WRN No image found
diun | INF Jobs completed added=0 failed=0 skipped=0 unchanged=0 updated=0
diun | INF Cron initialized with schedule 0 */6 * * *
diun | INF Next run in 5 hours
...
diun | INF Cron triggered
diun | WRN No image found
diun | INF Jobs completed added=0 failed=0 skipped=0 unchanged=0 updated=0
```

### Initial Symptoms:
1. **Startup Error**: `ERR Cannot create Docker client error="Cannot connect to the Docker daemon at tcp://socket-proxy:2375. Is the docker daemon running?"`
2. **Zero Tracked Images**: `WRN No image found` with `Jobs completed added=0 failed=0 skipped=0 unchanged=0 updated=0` across all scheduled cron triggers.
3. **No Alerting Channel**: `WRN No notifier available`.

---

## Diagnostic Inquiries

1. Is `socket-proxy` reachable from the `diun` container over the `socket-net` bridge?
2. Why does the Docker client creation error occur at startup, yet subsequent cron runs attempt execution?
3. Why does Diun discover zero container images during its cron execution?
4. How can Diun dispatch notifications to `kiskaadee@roadtotech.me` through the local Stalwart mail service without compromising spam filtering or relay boundaries?

---

## Investigation & Hypothesis Testing

### 1. Inspecting Socket Proxy Access Logs
* **Command**: `ssh server-local "docker logs --tail 50 socket-proxy"`
* **Evidence**:
  ```text
  ::ffff:172.19.0.2:39952 [22/Sep/2026:12:00:20.621] dockerfrontend dockerbackend/dockersocket ... "HEAD /_ping HTTP/1.1" 200
  ::ffff:172.19.0.2:39952 [22/Sep/2026:12:00:20.622] dockerfrontend dockerbackend/dockersocket ... "GET /v1.54/version HTTP/1.1" 200
  ::ffff:172.19.0.2:39952 [22/Sep/2026:12:00:20.628] dockerfrontend dockerbackend/dockersocket ... "GET /v1.54/containers/json?filters=%7B%22status%22%3A%7B%22running%22%3Atrue%7D%7D HTTP/1.1" 200
  ::ffff:172.19.0.2:39952 [22/Sep/2026:12:00:20.655] dockerfrontend dockerbackend/dockersocket ... "GET /v1.54/images/amir20/dozzle:latest/json HTTP/1.1" 200
  ```
* **Status**: Refutes total network disconnection. Diun *was* successfully querying container lists and image metadata on scheduled cron runs, but failed during initial container startup.

### 2. Startup Race Condition
* **Rationale**: Compose services without explicit dependencies initialize in parallel.
* **Evidence**: `diun` in `docker-compose.yml` lacked a `depends_on: [socket-proxy]` directive. At container initialization, Diun immediately pinged port 2375 before HAProxy finished binding its listener socket.
* **Status**: Confirmed as root cause for the startup `ERR Cannot create Docker client`.

### 3. Container Label Filter Invariant
* **Rationale**: Diun's Docker provider documentation specifies that `watchByDefault` defaults to `false`. When `false`, containers without `diun.enable=true` are ignored.
* **Evidence**: Grepping the repository for `diun.enable` yielded 0 results. Diun inspected all containers via `socket-proxy`, found none with the label, and logged `WRN No image found`.
* **Status**: Confirmed as root cause for zero analyzed images.

### 4. Stalwart SMTP Integration & Anti-Spam Evaluation
* **Diagnostic**: Tested internal SMTP communication from `proxy-net` to `stalwart:25` using a Python container script:
  ```python
  s = smtplib.SMTP("stalwart", 25)
  s.mail("diun@roadtotech.me")
  print(s.rcpt("kiskaadee@roadtotech.me"))  # (250, b'2.1.5 OK')
  print(s.rcpt("fcortesbio@gmail.com"))     # (550, b'5.1.2 Relay not allowed.')
  ```
* **Findings**:
  * Unauthenticated local delivery on port 25 to `@roadtotech.me` succeeds natively.
  * Unauthenticated relaying to external domains (`@gmail.com`) is blocked to prevent open mail relaying.
  * Direct test emails landed in SnappyMail's `Junk` folder because the test client sent unauthenticated internal mail claiming `@roadtotech.me` with bare headers and default container hostnames (`diun` / container ID) rather than an RFC-compliant FQDN EHLO domain.
  * Explicitly configuring `DIUN_NOTIF_MAIL_LOCALNAME=roadtotech.me` satisfies the SMTP HELO/EHLO validation policy on Stalwart.

---

## Findings & Root Cause Analysis

1. **Startup Dependency Gap**: Diun failed on boot due to missing `depends_on: [socket-proxy]`.
2. **Opt-in Filtering**: Diun ignored running containers because `DIUN_PROVIDERS_DOCKER_WATCHBYDEFAULT` was unset (default `false`).
3. **Missing Notifier Definition**: Diun operated without notification backends configured.
4. **SMTP EHLO Hostname Validation**: Stalwart required a valid domain for EHLO handshakes, requiring `DIUN_NOTIF_MAIL_LOCALNAME` to avoid `550 5.5.0 Invalid EHLO domain` rejection.

---

## Declarative Remediation & Local Validation

In `~/Core/docker-compose.yml`, updated the `diun` service configuration:

```yaml
  diun:
    image: crazymax/diun:latest
    container_name: diun
    restart: always
    command: serve
    depends_on:
      - socket-proxy
      - stalwart
    environment:
      - TZ=UTC
      - LOG_LEVEL=info
      - LOG_JSON=false
      - DIUN_WATCH_WORKERS=20
      - DIUN_WATCH_SCHEDULE=0 */6 * * *
      - DIUN_PROVIDERS_DOCKER=true
      - DIUN_PROVIDERS_DOCKER_ENDPOINT=tcp://socket-proxy:2375
      - DIUN_PROVIDERS_DOCKER_WATCHBYDEFAULT=true
      - DIUN_PROVIDERS_DOCKER_APIVERSION=${DOCKER_API_VERSION:-1.40}
      - DIUN_NOTIF_MAIL_HOST=stalwart
      - DIUN_NOTIF_MAIL_PORT=25
      - DIUN_NOTIF_MAIL_LOCALNAME=${DOMAIN:-roadtotech.me}
      - DIUN_NOTIF_MAIL_SSL=false
      - DIUN_NOTIF_MAIL_INSECURESKIPVERIFY=true
      - DIUN_NOTIF_MAIL_FROM=diun@${DOMAIN:-roadtotech.me}
      - DIUN_NOTIF_MAIL_TO=kiskaadee@${DOMAIN:-roadtotech.me}
    volumes:
      - ./config/diun:/data
    networks:
      - socket-net
      - proxy-net
```

### Local Validation
Executed `./scripts/test` on the workstation:
* Ruff linting passed.
* Pytest security invariants (socket-proxy read-only enforcement, unprivileged container checks) passed (35/35).
* Nix flake evaluation passed.

---

## Deployment & Recovery Runbook

1. **Commit & Push**:
   ```bash
   git commit -am "feat(core): configure diun mail notifications via stalwart"
   git push origin main
   ```
2. **Pull & Recreate on Server**:
   ```bash
   ssh server-local "cd ~/Core && git pull && appctl up diun"
   ```
3. **Trigger Notification Test**:
   ```bash
   ssh server-local "docker exec diun diun notif test"
   ```
4. **Post-Deployment Verification**:
   * Diun logs:
     ```text
     INF Configuration loaded from 13 environment variable(s)
     INF Found 22 image(s) to analyze provider=docker
     INF Jobs completed added=0 failed=3 skipped=0 unchanged=19 updated=0
     Notification sent for mail notifier(s)
     ```
   * Stalwart logs:
     ```text
     INFO Delivery completed (delivery.completed)
         queueId = 330944359985840128
         queueName = "local"
         from = "diun@roadtotech.me"
         to = ["kiskaadee@roadtotech.me"]
         code = 250
     ```

---

## Discussion & Generalization

1. **Log Illusion vs. Transient Failure**: An error occurring only during the container's entrypoint initialization must be distinguished from ongoing operational failure. Inspecting access logs on the target service (`socket-proxy`) immediately showed that scheduled cron requests were healthy.
2. **Default-Deny Filters in Daemon Notifiers**: Daemon monitoring tools (Diun, Watchtower) frequently default to label-only discovery. Explicitly defining global watch behavior (`watchByDefault: true`) is necessary in homelab architectures where services are deployed via individual compose files without centralized label boilerplate.
3. **Internal Mail Server Anti-Spoofing**: Internal microservices delivering unauthenticated alerts over port 25 to local mailboxes must provide valid EHLO domains (`localName`) to pass MTA ingress checks and prevent false-positive spam flagging.

---

## References

* Core Manifest: [`/home/kiskaadee/Homelab/Core/docker-compose.yml`](file:///home/kiskaadee/Homelab/Core/docker-compose.yml)
* Diun Documentation: [https://crazymax.dev/diun/](https://crazymax.dev/diun/)
* Stalwart Mail Server: [https://stalw.art/docs/](https://stalw.art/docs/)
