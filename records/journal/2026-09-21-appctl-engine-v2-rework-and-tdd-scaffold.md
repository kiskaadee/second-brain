---
type: journal
project: homelab
date: 2026-09-21
tags:
  - homelab
  - orchestration
  - appctl
  - python
  - architecture
  - testing
  - pytest
---

# Architecture & TDD: appctl Engine V2 Domain Modeling and Test Suite Scaffold

## Summary & Objectives
Initiated a comprehensive architectural rework of [`scripts/appctl_engine.py`](file:///home/kiskaadee/Projects/active/appctl-refactor/scripts/appctl_engine.py) to elevate the homelab control utility into clean, type-safe engineering code (`appctl_engine_v2.py`). Development is conducted in an isolated Git worktree at `~/Projects/active/appctl-refactor`.

---

## Key Architectural Decisions & Progress

### 1. Standardized YAML Parsing & Custom Exception Handling
- **Replaced Custom Parser**: Deprecated the hand-rolled `parse_yaml_simple()` in favor of standard `yaml.safe_load()` using PyYAML.
- **Explicit Failure Boundary**: Defined `class ManifestError(Exception): pass` to cleanly catch and isolate malformed YAML syntax without crashing the whole application inventory.

### 2. Explicit Domain Model Hierarchy
- **Base Domain Model**: Established `@dataclass class App` representing common operational primitives:
  ```python
  name: str
  description: str
  domain: str
  dir_path: str
  has_compose: bool
  ```
- **Layer-Specific Models**:
  - `SitesApp(App)`: Represents dynamic `~/Sites/*` workloads with `app.yaml` metadata (`aliases`, `visible`, `auth`, `networks`, `env`, `homepage`, `manifest_error`).
  - `CoreService(App)`: Represents Core platform services (`container`, `weight`, `icon`).
  - `HomepageConfig`: Strongly-typed representation for dashboard cards.

### 3. Pure Normalization Boundary
- Extracted `sites_app_from_manifest(app_dir, manifest, manifest_error) -> SitesApp` as a pure normalization seam.
- Separates filesystem discovery from domain instantiation, enabling unit tests to verify manifest coercion without disk I/O.

### 4. Domain-Agnostic Infrastructure & Strict Validation
- Decoupled hardcoded personal domains by parameterizing `HOMELAB_DOMAIN = os.environ.get("HOMELAB_DOMAIN") or os.environ.get("DOMAIN", "")`.
- Added `validate_environment()` to fail fast if mandatory environment variables or Core directories are missing.

### 5. TDD Test Suite Scaffold
- Created `tests/unit/test_appctl_engine_v2.py` with custom Pytest fixtures:
  - `mock_sites_dir` & `mock_core_dir`: Isolated temporary directories with automatic `monkeypatch` teardown.
  - `AppFactory`: Object Mother/Factory class to generate test app directories with `app.yaml` and Compose manifests in one line.
- Verified passing tests for resolution hierarchy, manifest overrides, and type normalization.
- Established failing (Red) acceptance criteria for upcoming Docker inspection and Homepage YAML compilation.

---

## Key Lessons & Technical Insights
- **Nix `buildInputs` Function Call Syntax**: Calling `python3.withPackages` inside Nix lists `[ ... ]` requires outer parentheses `(python3.withPackages (ps: [ ... ]))`, otherwise Nix evaluates the function and lambda as two separate invalid list elements.
- **Python `str(None)` Truthiness Trap**: Calling `str(manifest.get("key")) or "fallback"` returns `"None"` (a truthy string) when the key is missing, completely breaking fallback evaluation. Safe normalization requires checking `manifest.get("key") is not None` before string casting.
- **Pytest Name-Based Dependency Injection**: Pytest inspects parameter names via reflection to inject fixtures. Factory helpers benefit from real helper classes (`AppFactory`) for native LSP autocompletion without separate `Protocol` stubs.

---

## Next Steps
1. Port and implement the inspection layer in `scripts/appctl_engine_v2.py`:
   - `get_docker_status(dir_path, container_name)`
   - `get_git_sync_status(dir_path)` & `get_git_diagnostics(dir_path)`
   - `check_ssl_cert(domain)` & `check_all_ssl_certs(domains)`
2. Port CLI command handlers (`cmd_sync_homepage`, `cmd_list`, `cmd_info`, `cmd_ssl`, `cmd_resolve`, `cmd_complete`).
3. Turn remaining unit tests green and swap V2 into production [`scripts/appctl_engine.py`](file:///home/kiskaadee/Homelab/Core/scripts/appctl_engine.py).
