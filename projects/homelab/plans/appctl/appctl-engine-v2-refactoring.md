---
type: plan
status: active
project: homelab
date: 2026-09-21
tags:
  - operations
  - architecture
  - homelab
  - appctl
  - python
  - refactoring
  - testing
  - pytest
---

# 🚀 appctl Engine V2: Architectural Modernization & Type-Safe Refactoring Plan

## 1. Executive Summary & Intent

The `appctl` control utility is the central metadata, discovery, and inspection engine for the `roadtotech.me` homelab. It derives operational views (Docker status, Git sync status, SSL/TLS validation, Homepage dashboard generation, shell completion) from application manifests (`Sites/*/app.yaml`) and Core platform definitions.

This plan modernizes the engine from a procedural ~900-line script with a hand-rolled YAML parser into a clean, strongly-typed, test-driven Python engine (`appctl_engine_v2.py`) with zero breaking changes to the bash caller interface (`scripts/appctl`).

---

## 2. Problem Statement & Motivation

| Issue in V1 Engine | Architectural Risk | V2 Solution |
| :--- | :--- | :--- |
| **Handmade YAML Parser** (`parse_yaml_simple`) | Fragile indentation parser; silently mishandled complex structures, quotes, multiline strings, or standard YAML types. | Replace with standard `yaml.safe_load()` via PyYAML (`flake.nix` & `nixos`). |
| **Silent Error Suppression** (`contextlib.suppress`) | Swallowed all YAML errors; syntax mistakes in `app.yaml` silently degraded into empty defaults without operator notification. | Define `class ManifestError(Exception)` and capture errors into `app.manifest_error` for explicit reporting. |
| **Stringly-Typed Dictionaries** | Unstructured `dict[str, Any]` passed everywhere with loose key lookups (`app["domain"]`, `app["name"]`). | Strict `@dataclass` hierarchy: `App`, `SitesApp`, `CoreService`, `HomepageConfig`, `SSLCertResult`. |
| **Domain Hardcoding** | Hardcoded `roadtotech.me` strings throughout code, violating portability and open-source reusability. | Dynamic `HOMELAB_DOMAIN = os.environ.get("HOMELAB_DOMAIN")` + fail-fast `validate_environment()`. |
| **Zero Test Coverage** | No automated tests for resolution precedence, manifest parsing, or Homepage compilation. | Comprehensive TDD test suite in `tests/unit/test_appctl_engine_v2.py` with `AppFactory` fixture. |

---

## 3. Architecture & Domain Model

```
┌─────────────────────────────────────────────────────────────┐
│                    scripts/appctl (Bash)                    │
│           (Mutation: up, down, restart, update, logs)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON via `resolve` & stdout
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                scripts/appctl_engine_v2.py                  │
│          (Inspection, Metadata, Discovery & Sync)           │
├─────────────────────────────────────────────────────────────┤
│ 1. Domain Hierarchy                                         │
│    ├── App (Base: name, description, domain, dir_path)     │
│    ├── SitesApp (Sites: aliases, visible, auth, env, etc.)  │
│    └── CoreService (Core: container, weight, icon)          │
├─────────────────────────────────────────────────────────────┤
│ 2. Ingestion & Normalization                                │
│    ├── load_manifest() -> raw dict (PyYAML)                 │
│    └── sites_app_from_manifest() -> SitesApp (Pure Seam)    │
├─────────────────────────────────────────────────────────────┤
│ 3. Inspection Engines                                       │
│    ├── Docker Status (Compose ps -q & inspect Running)      │
│    ├── Git Sync Status (plumbing porcelain & rev-list)      │
│    └── TLS/SSL Validation (stdlib socket/ssl via ThreadPool)│
├─────────────────────────────────────────────────────────────┤
│ 4. CLI Dispatch Layer                                       │
│    ├── cmd_list / cmd_status (polymorphic table rendering)  │
│    ├── cmd_info (unified diagnostics view)                  │
│    ├── cmd_ssl (TLS overview across apps and Core)          │
│    ├── cmd_resolve (JSON emitter for bash caller)           │
│    ├── cmd_sync_homepage (compiles services.yaml)           │
│    └── cmd_complete (bash autocomplete generator)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Deliverables & Execution Roadmap

### Deliverable 1: Domain Model, Manifest Ingestion & TDD Scaffold (COMPLETE / GREEN)
- [x] Create isolated Git worktree at `~/Projects/active/appctl-refactor`.
- [x] Configure Pyright and Nix devShell (`python3.withPackages [ pyyaml types-pyyaml pytest ruff pyright ]`).
- [x] Implement `@dataclass class App`, `SitesApp`, `CoreService`, and `HomepageConfig`.
- [x] Implement `load_manifest(manifest_path)` with `ManifestError`.
- [x] Implement pure normalization seam `sites_app_from_manifest(app_dir, manifest, manifest_error)`.
- [x] Implement dynamic discovery `get_sites_apps(sites_dir)` and `resolve_app(query, apps)`.
- [x] Implement typed Core registry `get_core_services(core_dir)`.
- [x] Implement `validate_environment()` for fail-fast domain and path verification.
- [x] Scaffold test suite in `tests/unit/test_appctl_engine_v2.py` with `mock_sites_dir`, `mock_core_dir`, and `AppFactory`.

### Deliverable 2: Inspection Layer (IN PROGRESS)
- [ ] **Docker Inspection Engine**:
  - Implement `get_docker_status(dir_path: Path | str, container_name: str | None = None) -> str`.
  - Handle Compose directory inspection (`docker compose ps -q` + inspect).
  - Handle Core single container inspection (`docker inspect -f '{{.State.Running}}' <name>`).
  - Return standardized status badges (`🟢 Running (N)`, `🟡 Degraded (M/N)`, `🔴 Stopped`, `⚪ Not Stack`, `❓ Unknown`).
- [ ] **Git Sync & Diagnostics Engine**:
  - Implement `get_git_sync_status(dir_path: Path | str) -> str`.
  - Parse `git status --porcelain` and `git rev-list --left-right --count HEAD...@{u}`.
  - Return standardized badges (`✓ Synced`, `⬆ N Ahead`, `⬇ N Behind`, `⚡ N⬆ M⬇`, `⚪ Untracked`, `*` dirty indicator).
  - Implement `get_git_diagnostics(dir_path: Path | str) -> dict[str, Any] | None`.
- [ ] **SSL / TLS Inspection Engine**:
  - Define `@dataclass class SSLCertResult`.
  - Implement `check_ssl_cert(domain: str, port: int = 443, timeout: float = 3.0) -> SSLCertResult`.
  - Implement `check_all_ssl_certs(domains: list[str]) -> dict[str, SSLCertResult]` with `ThreadPoolExecutor`.
- [ ] **Concurrent Remote Fetching**:
  - Implement `fetch_all_repositories(apps: list[SitesApp], include_core: bool = True)` with worker pool.

### Deliverable 3: Presentation & CLI Dispatch Layer
- [ ] **`cmd_list` / `cmd_status`**:
  - Support `--core` / `-c`, `--fetch` / `-f`, `--ssl` / `-s`, and `--all` / `-a` flags.
  - Polymorphic table formatting for both `SitesApp` and `CoreService`.
  - Render manifest warning indicators if `app.manifest_error` is populated.
- [ ] **`cmd_info`**:
  - Formatted deep diagnostic view for a single application or Core service.
  - Display metadata, Authelia guard status, Compose status, Git diagnostics, and TLS certificate info.
- [ ] **`cmd_ssl`**:
  - Formatted TLS certificate table for all public domains or deep inspection of a single target.
- [ ] **`cmd_resolve`**:
  - Emit JSON payload via `app.to_dict()` ensuring 100% compatibility with `scripts/appctl`.
- [ ] **`cmd_sync_homepage`**:
  - Compile `SitesApp` cards and `CoreService` definitions into `Core/config/homepage/services.yaml`.
  - Group by `homepage.group`, sort by `homepage.weight`, and resolve local SVG/PNG icons from `icons/`.
- [ ] **`cmd_complete`**:
  - Generate bash autocompletion candidates for commands, apps, aliases, and Core services.

### Deliverable 4: Verification, Cutover & Documentation
- [ ] Run full automated test suite: `pytest tests/` (100% Green).
- [ ] Run code linter: `ruff check .` with zero errors.
- [ ] Run type checker: `pyright` with zero errors.
- [ ] Replace `scripts/appctl_engine.py` with `scripts/appctl_engine_v2.py`.
- [ ] Run `./scripts/test` and live verification (`appctl list`, `appctl info`, `appctl sync`).
- [ ] Update `docs/appctl.md` with V2 architecture and developer documentation.

---

## 5. Invariants & Acceptance Criteria

1. **Zero Breaking Changes to Bash Contract**:
   `scripts/appctl` must function identically with `appctl list`, `appctl info <app>`, `appctl up <app>`, `appctl sync`, and autocompletions without requiring syntax or argument changes.
2. **Deterministic Test Suite**:
   Unit tests in `tests/unit/test_appctl_engine_v2.py` must run hermetically without requiring a live Docker daemon, live network access, or mutating the user's real `~/Sites` or `~/Core`.
3. **The Unlicense Integrity**:
   All new files and refactored code preserve public domain status under The Unlicense.
