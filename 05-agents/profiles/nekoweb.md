---
type: agent
status: active
name: nekoweb
target_workspace: git@github.com:kiskaadee/nekoweb.git
project: nekoweb
tags:
  - nekoweb
  - python
  - fastapi
  - react
  - tanstack
  - sqlite
  - uv
  - pnpm
---

# NekoWeb Manga Platform Agent

## 1. Overview & Operational Scope

* **Target Workspace**: `git@github.com:kiskaadee/nekoweb.git` (`/home/kiskaadee/Projects/active/nekoweb`)
* **Primary Role**: Develops and maintains the full-stack self-hosted manga web platform (FastAPI backend, UV package manager, SQLite WAL persistence, React/TanStack frontend, and Headless HakuNeko daemon).
* **Core Invariants & Safety Constraints**:
  * **Working Tree Authority**: Always run `git status` and inspect files first; destructive git operations (`reset --hard`, `clean -fd`, `stash`) are strictly prohibited.
  * **Architectural Invariants**: Respect accepted ADRs (`docs/adr/`) and system architecture (`docs/ARCHITECTURE.md`) before changing API routes, WebSocket schemas, or persistence layers.
  * **Tooling Environment**: Root `.envrc` evaluates Nix flakes; `backend/.envrc` chains via `source_up` and activates `backend/.venv`; Python dependencies use `uv` while frontend uses `pnpm` under Node 22.

---

## 2. Canonical Agent Specification

The following specification represents the active behavioral contract configured for `/home/kiskaadee/Projects/active/nekoweb/AGENTS.md`:

````markdown
# Project Guidelines & Safety Rules for AI Agents

## 1. Mission & Authority

NekoWeb is a self-hosted web manga platform currently built around **FastAPI + UV + SQLite3 WAL + React/TanStack + Headless HakuNeko Daemon**.
- **Accepted ADRs** (`docs/adr/`) and **Architecture Documentation** (`docs/ARCHITECTURE.md`) define the authoritative design.
- **Implementation autonomy ≠ Architectural autonomy.** Do not replace technologies, dependencies, or storage strategies without explicit approval.

---

## 2. Working Tree Authority & Safety (MANDATORY)

The working tree represents the user's active work.
1. **Inspect First:** Run `git status` and read target files before modifying anything.
2. **Never Overwrite Blindly:** Use available file-reading tools. Preserve user comments, links, and conventions. Prefer surgical edits over wholesale overwrites.
3. **No Destructive Git Commands:** Never run `reset --hard`, `clean -fd`, `restore`, `checkout`, `stash`, `rebase`, or `amend` without explicit permission.
4. **Final Diff Verification:** Before completing work, run `git status` and `git diff` to verify that no unrelated user changes were modified or discarded. Distinguish user changes from agent changes in completion reports.

---

## 3. Architecture & Component Contracts (Progressive Triggers)

- **Read `docs/ARCHITECTURE.md`** before modifying API contracts, changing WebSocket event schemas, or crossing Backend/Frontend/Daemon boundaries.
- **Read `docs/adr/`** before altering persistence, networking, deployment, or dependencies.
- **Stop and Ask:** If an implementation conflicts with an accepted ADR or an ambiguous requirement materially affects architecture, stop and ask the user rather than guessing or silently changing the design.
- **No Speculative Robustness:** Do not add unrequested fallback layers, complex generic abstractions, or future-proofing bloat.

---

## 4. Operational Invariants

### 4.1 Persistence (SQLite3 WAL)
- Database must operate in **WAL mode** (`PRAGMA journal_mode=WAL;`) with foreign keys enabled (`PRAGMA foreign_keys=ON;`).
- Use SQLAlchemy's async interface via `aiosqlite`.
- Do not create ad-hoc connections outside the application session/engine lifecycle.
- Store database strictly on local volume mounts (`/app/data/nekoweb.db`). Never place SQLite on network shares (NFS/SMB).
- All schema changes must be managed through Alembic migrations.

### 4.2 Tooling & Dependencies
- **Nix & Direnv:** Root `.envrc` evaluates `use flake`. `backend/.envrc` chains via `source_up` and activates `backend/.venv`. Never move the venv to the repository root.
- **Python (Backend):** Use `uv`. Never manually edit `uv.lock` (run `uv lock`). Never use raw `pip`.
- **JavaScript (Frontend/Daemon):** Use `pnpm` and respect Node 22 from the Nix devShell.
- **Generated / External Code:** Treat copied code as untrusted until verified against project dependency versions and conventions.

---

## 5. Verification & Completion

Every task must be verified before declaring completion:
- Run appropriate linters, type checks (`tsc`, `pyright`), or test suites (`uv run pytest`).
- Verify database migrations and schema initialization for persistence changes.
- Report: (1) What changed, (2) Files modified/created, (3) Verification performed, (4) Unverified areas/risks.
````

---

## 3. Related Resources & Context

* [NekoWeb Project Landing Page](../projects/nekoweb/README.md)
* [Testing & Quality Assurance Guide](../knowledge/methods/testing.md)
* [SQL & Relational Persistence Methods](../knowledge/methods/sql.md)
