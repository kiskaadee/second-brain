---
type: plan
status: active
project: homelab
tags:
  - homelab
  - cicd
  - gitops
  - appctl
  - automation
---

# 🚀 Smart Selective Deployment Pipeline Plan for Homelab Core

## Goal Description
Implement an intelligent, change-aware deployment pipeline for `homelab-core` that:
1. Analyzes incoming commits on `main` (via Gitea GitOps webhooks and manual `appctl update core` CLI invocations) and selectively executes **only** the required actions.
2. Automatically keeps server-side bash autocompletion in sync whenever CLI scripts are modified.
3. Introduces a lightweight, zero-dependency automated test suite (`tests/`) to validate CLI resolution, YAML parsing, completion generation, and diff analysis.

Unchanged services remain completely untouched:
- **Scripts & Tools** (`scripts/**`): Fast-forwards repository files, runs test suite validation, and auto-refreshes `~/.local/share/bash-completion/completions/appctl` on the host; **zero container restarts**.
- **Documentation & Metadata** (`docs/**`, `*.md`, `.gitignore`, `UNLICENSE`): Fast-forwards repository files only; **zero container restarts**.
- **Service Configuration** (`config/authelia/**`, `config/diun/**`): Fast-forwards repository files and restarts **only** the affected container (e.g. `authelia` reloads its updated config while Traefik and edge routing remain 100% online).
- **Core Orchestration** (`docker-compose.yml`): Executes declarative `docker compose up -d --remove-orphans` which natively compares container configurations and recreates only modified container definitions.

---

## User Review Required

> [!IMPORTANT]
> **Server-Side Autocompletion Auto-Installation**:
> Whenever `scripts/appctl` or `scripts/appctl_engine.py` is updated by the pipeline (or manually via `appctl completion --install`), the pipeline will automatically regenerate and write the bash completion script to:
> `~/.local/share/bash-completion/completions/appctl`
> No manual re-installation steps are needed on the server when `appctl` options or commands evolve.

> [!NOTE]
> **Zero-Dependency Test Suite**:
> All unit and integration tests will use Python's built-in `unittest` framework (`python3 -m unittest discover tests`). This guarantees tests can run anywhere (in local dev, in CI/CD, or during server-side deployment validation) without needing `pip install` or external packages.

---

## Architecture & Change Classification Matrix

```
                        Push to main (Gitea Webhook / CLI)
                                        │
                                        ▼
                         [ Inspect Changed Files ]
                        (git diff or webhook commits)
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
     [ Scripts / Docs ]       [ Service Config ]        [ docker-compose.yml ]
      (scripts/*, *.md)       (config/authelia/*)       (Container topology)
             │                          │                          │
             ▼                          ▼                          ▼
      git pull --ff-only        git pull --ff-only         git pull --ff-only
      Run test suite            restart ONLY authelia      docker compose up -d
      Auto-install completion                              (recreates only delta)
      (NO container action)
```

### File Classification Rules

| Path Pattern | Classification | Actions Executed | Impact on Running Services |
| :--- | :--- | :--- | :--- |
| `scripts/**` | `tooling` | `git_pull`, `run_tests`, `install_completion` | **None** (Tooling & bash completion updated on host) |
| `docs/**`, `*.md`, `.gitignore`, `LICENSE`, `UNLICENSE`, `.env-example` | `documentation` | `git_pull` | **None** |
| `config/authelia/**` | `service_config:authelia` | `git_pull`, `restart_service(authelia)` | Restarts Authelia; Traefik & others untouched |
| `config/diun/**` | `service_config:diun` | `git_pull`, `restart_service(diun)` | Restarts Diun; others untouched |
| `config/traefik/**` | `service_config:traefik` | `git_pull`, `restart_service(traefik)` | Restarts Traefik |
| `docker-compose.yml` | `orchestration` | `git_pull`, `compose_up_delta` | Docker Compose recreates only changed services |
| Any other unclassified file | `fallback` | `git_pull`, `compose_up_delta` | Safe fallback ensures changes take effect |

### Multi-File Aggregation Rules
When a push touches multiple files across different categories:
1. Actions are deduplicated and merged into a minimal execution plan.
2. If `scripts/**` changed: test suite is executed and completion is auto-installed.
3. If `docker-compose.yml` changed: `docker compose up -d` handles container recreations.
4. If specific service config files (like `config/authelia/configuration.yml`) were also modified, explicit targeted restarts for those containers are executed.
5. If only `tooling` and/or `documentation` files changed, the pipeline outputs:
   `"✨ Core repository and bash completion updated. No container restarts required."` and exits with code 0.

---

## Proposed Changes

### Component 1: Automated Test Suite (`tests/`)
Create comprehensive unit tests covering:
- `tests/test_yaml_parser.py`: Simple YAML parsing logic, edge cases, lists, and dict nesting.
- `tests/test_appctl_resolution.py`: Core stack resolution, core services (`authelia`, `traefik`), app resolution under `SITES_DIR`, and `cmd_complete` outputs.
- `tests/test_diff_analyzer.py`: Classification of file lists (tooling, docs, authelia, compose, mixed), verifying exact action plans.
- `tests/test_gitops_dispatcher.py`: Webhook payload parsing, target resolution for `homelab-core`, `Brain`, and sites.

### Component 2: Core Engine (`scripts/appctl_engine.py`)
Add analysis and planning functions:
- `analyze_core_diff(changed_files: list[str]) -> dict`:
  Categorizes changed files into:
  - `services_to_restart`: list of service names (e.g. `["authelia"]`)
  - `compose_recreate`: bool (whether `docker-compose.yml` changed)
  - `tooling_changed`: bool (whether `scripts/**` changed, triggering tests & completion install)
  - `tooling_only`: bool (whether changes are strictly scripts/docs)
  - `details`: human-readable breakdown of changes
- `cmd_plan_core_update(args)`:
  CLI command (`python3 scripts/appctl_engine.py plan-core-update [--commit-range <range>] [--dry-run]`) that inspects git diff, outputs the resolved plan as JSON or formatted text, and allows dry-run previewing.

### Component 3: GitOps Dispatcher (`scripts/gitops_dispatcher.py`)
- Add support for `homelab-core` and `Core` repository names in `resolve_target()`.
- When repository is `homelab-core`:
  - Extract changed files from `payload["commits"]` (or fallback to `git diff` against `payload["before"]..payload["after"]`).
  - Use `analyze_core_diff()` to determine the required actions.
  - Execute targeted deployment actions:
    1. `git pull --ff-only origin main`
    2. If `tooling_changed`: run `python3 -m unittest discover tests` and install bash completion to `~/.local/share/bash-completion/completions/appctl`.
    3. If `compose_recreate`: run `docker compose up -d --remove-orphans` with `/run/secrets/rendered/homeserver.env`
    4. For each service in `services_to_restart` (not already recreated by compose): run `docker compose restart <service>`
    5. If `tooling_only`: log that no container restarts were needed.

### Component 4: CLI Orchestrator (`scripts/appctl`)
- Add `appctl completion --install` / `appctl completion install` command:
  Automatically creates `~/.local/share/bash-completion/completions` if missing and writes the generated completion script.
- Add `appctl test` command:
  Runs `python3 -m unittest discover "$SCRIPT_DIR/../tests"` with clean test output.
- Update `appctl update core`:
  - Before pulling, check remote vs local `git rev-parse`.
  - Obtain the list of incoming changed files via `git diff --name-only HEAD origin/main`.
  - Pass the changed files to the engine to compute the plan.
  - Display the planned actions to the operator:
    ```
    📥 Pulling latest changes for Core (3 commits)...
    📝 Detected changes:
       - scripts/appctl (tooling)
       - config/authelia/configuration.yml (authelia)
    🧪 Running test suite... OK (12 tests passed)
    🔄 Selectively restarting only 'authelia' container...
    ✨ Core update completed with zero disruption to remaining services!
    ```
  - Support `--dry-run` flag on `appctl update core --dry-run` to preview the impact of upstream changes before pulling.

---

## Verification Plan

### Automated Tests
1. **Linter & Type Integrity**:
   ```bash
   ruff check scripts/ tests/
   ```
2. **Execute New Test Suite**:
   ```bash
   python3 -m unittest discover -s tests -v
   # or via new CLI shortcut:
   ./scripts/appctl test
   ```
3. **Completion Auto-Installer Test**:
   ```bash
   ./scripts/appctl completion install
   test -f ~/.local/share/bash-completion/completions/appctl
   ```
4. **Webhook Simulation**:
   Run `python3 scripts/gitops_dispatcher.py` with mock Gitea webhook JSON payloads for `homelab-core` in test mode.

### Manual Verification
1. Run `appctl update core --dry-run` to verify dry-run output.
2. Verify `appctl update core` when no remote changes exist.
3. Test a mock commit touching `scripts/` only to confirm zero container disruption and automatic completion refresh.
