---
type: project
status: active
tags:
  - dynu
  - ddns
  - rust
  - python
  - homelab
---
# 🔄 dynu-monitor — High-Frequency Smart DDNS Monitor

## 🎯 Project Overview

`dynu-monitor` is a lightweight, local-first dynamic DNS change detector and smart trigger daemon. It monitors the machine's public IPv4 address and triggers dynamic DNS updates (via `ddclient.service`) only when a verified IP change has occurred.

By acting as a local gatekeeper in front of the DNS updater, it prevents unnecessary API spam to DNS providers, avoids IP change detection latency, and distributes external IP lookup queries across multiple external echo services using a stateful round-robin rotation strategy.

---

## 🏛️ System Architecture

```mermaid
sequenceDiagram
    autonumber
    participant Timer as systemd.timers.dynu-monitor (30s)
    participant Monitor as dynu-ip-monitor
    participant State as /var/lib/dynu/state.json
    participant Resolvers as IP Resolvers (Round-Robin Pool)
    participant History as /var/lib/dynu/ip_history.jsonl
    participant DDClient as ddclient.service

    Timer->>Monitor: Trigger execution
    Monitor->>State: Read last successful provider index & last IP
    Monitor->>Resolvers: Query next provider (index + 1 mod N)
    alt Provider succeeds
        Resolvers-->>Monitor: Valid Public IPv4
        Monitor->>State: Persist updated provider index
    else Provider fails
        Monitor->>Resolvers: Fallback to next provider in sequence
    end

    alt IP changed (current_ip != last_ip)
        Monitor->>DDClient: systemctl start ddclient.service
        DDClient-->>Monitor: DDNS record updated
        Monitor->>History: Record transition event (status: success)
        Monitor->>State: Update last_ip = current_ip
    else IP unchanged
        Monitor->>Monitor: Exit 0 (zero API overhead)
    end
```

---

## 🗺️ Implementation Tracks

The project spans two iterative phases:

### 1. Python / NixOS Implementation *(Completed)*
- **Status**: Completed and verified on branch `refactor/dynu-monitor`.
- **Key Features**:
  - 30-second polling interval via `systemd.timers.dynu-monitor`.
  - Stateful round-robin rotation across 5 public providers (`api.ipify.org`, `icanhazip.com`, `ifconfig.me`, `checkip.dynu.com`, `wtfismyip.com`).
  - Atomic persistence to `/var/lib/dynu/state.json`.
  - Modernized UTC timezone handling (`datetime.now(timezone.utc)`).
- **Documentation**: [**High-Frequency Provider-Rotating Monitor Plan**](plans/provider-rotating-monitor-plan.md)

### 2. Standalone Rust Binary *(Active / In Planning)*
- **Status**: Planning and domain modeling phase at `/home/kiskaadee/Projects/active/dynu-monitor`.
- **Goals**:
  - Clean separation between domain orchestration (`IpMonitorService`) and external infrastructure (`IpResolver`, `StateRepository`, `DdnsUpdater`).
  - Zero Python runtime dependencies for minimal footprint on headless servers.
  - Comprehensive unit test coverage with dependency injection and trait mocks.
- **Documentation**: [**Rust Migration Plan & Milestones**](plans/rust-migration-plan.md)

---

## 📑 Project Documents & Plans

- [**High-Frequency Provider-Rotating Monitor Plan & Walkthrough**](plans/provider-rotating-monitor-plan.md) — Architectural design, 5-provider pool, systemd timer config, and verification results for the Python implementation.
- [**Rust Migration Plan**](plans/rust-migration-plan.md) — Architecture, domain entities, invariants, and phased milestones for the native Rust daemon.
