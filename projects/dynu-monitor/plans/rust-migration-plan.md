---
type: plan
status: active
project: dynu-monitor
tags:
  - dynu
  - ddns
  - rust
  - migration
---
# 🦀 Rust Migration Plan: Standalone `dynu-monitor` Daemon

## 🎯 Motivation & Objectives

While the Python implementation in `hosts/server/monitor.py` verified the core logic (30-second polling, 5-provider round-robin rotation, atomic state persistence), migrating the monitor to a native **Rust** binary provides:

1. **Zero Runtime Dependencies**: Removes Python runtime and interpreter startup overhead from headless NixOS servers.
2. **Strict Type Safety & Robust Error Handling**: Eliminates runtime type errors and unhandled exceptions using `Option<T>`, `Result<T, E>`, and custom error types.
3. **Decoupled Architecture**: Clean domain orchestration (`IpMonitorService`) abstracted from I/O mechanisms via traits for unit testing without network or systemd dependencies.
4. **Hands-on Rust Learning**: Serves as a practical project for idiomatic Rust patterns (traits, structs/enums, dependency injection, and Cargo).

**Project Location**: `/home/kiskaadee/Projects/active/dynu-monitor`

---

## 🏛️ Target Architecture

```text
                    ┌───────────────┐
                    │    main.rs    │
                    │ (Composition) │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │IpMonitorService│
                    │(Domain Engine)│
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          IpResolver   StateRepository  DdnsUpdater
              │             │             │
              ▼             ▼             ▼
            HTTP           JSON        systemctl
                            │
                            ▼
                     HistoryRepository
                            │
                            ▼
                          JSONL
```

---

## 🔒 Critical Invariants

1. `last_ip` strictly represents the IP address for which a DDNS update **completed successfully**.
2. Discovering a new IP does **not** update `last_ip` until `ddclient.service` exits with success.
3. A failed DDNS update preserves the previous `last_ip` in `state.json`.
4. If current IP matches `last_ip`, `ddclient.service` is never invoked.
5. Provider rotation index is persisted on every poll independently of IP changes.

---

## 📋 Implementation Milestones

### Milestone 1: Domain Core & Provider Rotation
- Define `MonitorState`, `IpDiscoveryResult`, and `HistoryEntry`.
- Implement IPv4 validation and circular round-robin provider rotation logic.
- Pure Rust standard library with zero external dependencies.

### Milestone 2: State Persistence
- Implement `StateRepository` trait and atomic JSON file writer (`state.json.tmp` -> `state.json`).
- Ensure state loading gracefully handles missing or corrupt initial state.

### Milestone 3: Application Orchestration (`IpMonitorService`)
- Implement `IpMonitorService` coordinating discovery, comparison, update dispatch, and state recording.
- Write full unit test suite with mock dependencies for resolvers and updaters.

### Milestone 4: HTTP Resolvers & Fallbacks
- Implement `IpResolver` using `reqwest` (blocking) or lightweight HTTP client.
- Implement fallback sequence across the 5 providers upon timeouts or non-200 responses.

### Milestone 5: Systemd Updater
- Implement `DdnsUpdater` invoking `systemctl start --wait ddclient.service`.
- Handle subprocess exit codes and timeout safety.

### Milestone 6: Audit History Logging
- Implement `HistoryRepository` appending structured events to `/var/lib/dynu/ip_history.jsonl`.

### Milestone 7: NixOS Integration & Packaging
- Package `dynu-monitor` via Nix flake (`pkgs.rustPlatform.buildRustPackage`).
- Replace Python `dynu-ip-monitor` derivation in `hosts/server/dynu.nix`.
- Verify 30-second timer execution and live rotation on the server.
