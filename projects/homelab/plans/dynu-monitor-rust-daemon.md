---
type: plan
status: active
project: homelab
tags:
  - operations
  - architecture
  - homelab
  - dynu
  - ddns
  - rust
  - migration
---

# 🦀 Rust Daemon Migration Plan: Standalone `ddns-monitor` (formerly `dynu-monitor`)

## 🎯 Goal Description

Migrate the dynamic DNS gatekeeper daemon from the current Python script to a native, statically compiled **Rust daemon** located at `~/Projects/active/ddns-monitor`.

This implementation introduces high-frequency 30-second polling and stateful round-robin resolver rotation across 5 public echo providers while eliminating Python interpreter overhead on the headless server. Crucially, it decouples the DDNS update mechanism behind a pluggable `DdnsConnector` trait to support both **Dynu** and **Cloudflare** (overcoming Dynu's free-tier 4-alias quota limit).

---

## 🏛️ Target Domain Architecture

```
                    ┌────────────────────────┐
                    │        main.rs         │
                    │   (Dependency Wiring)  │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │    IpMonitorService    │
                    │     (Domain Core)      │
                    └───────────┬────────────┘
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
        Box<dyn IpResolver> Box<dyn StateRepo> Box<dyn DdnsConnector>
               │                │                │
               ▼                ▼                ▼
         HttpEchoPool       StateFile       [Pluggable Connectors]
          (5 endpoints)    (state.json)     ├── DynuConnector (REST / ddclient)
                                │           └── CloudflareConnector (API v4)
                                ▼
                           HistoryFile
                        (ip_history.jsonl)
```

---

## 🔒 Non-Negotiable Invariants

1. `last_ip` strictly represents the IP address for which a DDNS update **completed successfully**.
2. Discovering a new IP does **not** update `last_ip` until `ddclient.service` exits with code 0.
3. A failed DDNS update preserves the previous `last_ip` in `state.json` to trigger a retry on the next tick.
4. Resolver queries must enforce a strict 5-second timeout to prevent stalling the monitoring loop.

---

## 🗺️ Phased Implementation Milestones

### Milestone 1: Domain Entities & In-Memory Logic *(In Progress)*
- [x] Define domain types: `Ipv4Addr`, `ProviderId`, `MonitorEvent`.
- [ ] Implement `IpMonitorService` pure business logic.
- [ ] Mock traits `MockIpResolver`, `MockStateRepository`, `MockDdnsConnector`.
- [ ] Unit tests verifying:
  - No change detected $\rightarrow$ zero updater calls.
  - Change detected $\rightarrow$ updater triggered $\rightarrow$ state updated.
  - Updater fails $\rightarrow$ state remains unchanged.

### Milestone 2: Infrastructure Adapters & Provider Connectors
- [ ] Implement `ReqwestIpResolver` with 5-endpoint pool (`ipify`, `icanhazip`, `ifconfig.me`, `checkip.dynu`, `wtfismyip`).
- [ ] Implement `JsonStateRepository` with atomic write (write to `.tmp` then rename).
- [ ] Implement `JsonlHistoryRepository` for append-only audit logs.
- [ ] Implement `DynuConnector` calling `systemctl start ddclient.service` or Dynu REST API.
- [ ] Implement `CloudflareConnector` querying Cloudflare API v4 for zero-quota DNS record updates.

### Milestone 3: Nix Packaging & Flake Integration
- [ ] Write `flake.nix` in `Projects/active/dynu-monitor` producing a static package.
- [ ] Package `dynu-monitor` into `homelab-core/nixos/modules/dynu.nix`.
- [ ] Replace `ipMonitorScript = pkgs.writers.writePython3Bin ...` with the native binary derivation.

### Milestone 4: Production Deployment & Verification
- [ ] Deploy generation via `sudo nixos-rebuild switch --flake ~/Core#server`.
- [ ] Verify 30-second timer cadence and resolver rotation in `/var/lib/dynu/state.json`.
- [ ] Verify zero memory leaks or zombie processes.
