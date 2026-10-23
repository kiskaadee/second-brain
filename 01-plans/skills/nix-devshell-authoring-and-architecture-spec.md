---
type: plan
status: completed
project: skills
date: 2026-10-23
tags:
  - nix
  - devshell
  - agent-skills
  - build-skill
  - specification
---

# Plan: Nix Development Shell Authoring Skill (`nix-devshell`)

## Epistemic Role & Purpose

This document is the approved technical specification and implementation plan for transforming the reconciled Nix development-shell manifesto (`manifesto-revised.md` and `audit/compatibility-verification.md`) into a portable, evidence-based agent skill (`skills/nix-devshell/`).

It defines the skill's operational boundaries, source authority hierarchy, progressive validation levels, Git ownership invariants, canonical reference division, and acceptance criteria.

---

## 1. Source Authority Hierarchy

Claims and guidance in the skill follow a strict 3-tier hierarchy:

1. **Primary Authority (`manifesto-revised.md`)**: The authoritative technical specification. All core operational prescriptions in the skill trace directly to manifesto sections.
2. **Constraint & Qualification Layer (`audit/compatibility-verification.md`)**: Narrows, bounds, and flags version-sensitive or unresolved manifesto claims. Does not introduce ungrounded rules.
3. **Provenance & Context Only (`audit/manifesto-audit.md`, `audit/manifesto-revision-log.md`)**: Documents the rationale for historical revisions; never cited as independent technical authority.

### Bounded Claims & Explicit Evidence Labels

| Manifesto Area | Constraint Applied | Evidence & Applicability in Skill |
|---|---|---|
| §6.2 Environment attributes | Flat, non-reserved attributes become shell variables; protected variables require `shellHook`. Nested `env` is excluded from portable guidance. | `Established` for nixpkgs 24.05 tutorial; `Unresolved` across older revisions. Verify against project lock. |
| §5 D4 Compiler selection | Changing the compiler requires selecting a toolchain/stdenv (`mkShell.override { stdenv = ...; }`). Adding a compiler package to `packages` does not guarantee `CC`. | `Established` pattern in nixpkgs, version-sensitive. Check target revision and platform. |
| §4.5 Foreign binaries on NixOS | Diagnosis split by failure mode: missing ELF interpreter vs. missing shared objects vs. FHS path assumptions. | `Established` in nix.dev FAQ. Linux/NixOS only; `nix-ld` is host-level configuration. |
| §5 D2 Tarball & Renovate inputs | Nix locking an input and a bot updating it are separate concerns. Cache availability is a third, separate question. | Renovate Nix manager docs (v44.181.0, beta/opt-in). Check project tooling. |
| §2, §9.1 Compatibility matrix | No numeric minimum version or universal nixpkgs release range is declared. | Policy from verification audit: verify against target lock and host Nix baseline. |

---

## 2. Operational Invariants & Git Boundaries

1. **Evidence-First Inspection**: The agent must inspect existing Nix files, `flake.lock` (or record that none is present), `.envrc`, language manifests, build scripts, CI, and host Nix capabilities *before* deciding on an architecture.
2. **Strict Git Ownership**:
   - `nix-devshell` may create and modify project files.
   - It **must never** run `git add`, `git commit`, `git stash`, or mutate the Git index or history.
   - Staging and committing are strictly handed off to `git-commit`.
3. **Untracked File Blockage vs. Failure**:
   - In a Git-backed flake, newly created untracked files are omitted by Nix's Git source filtering.
   - The skill must **not** stage files to bypass this.
   - It must **not** substitute `path:.` by default (as this copies untracked files and potential secrets to `/nix/store` and does not test the Git-filtered workflow).
   - Flake evaluation must be reported as `blocked: <file> untracked by Git`, while running independent checks (e.g. `nix-instantiate --parse`).
   - The user is instructed under *User actions* to track files (manually or via `git-commit`) and rerun blocked levels.

---

## 3. Four-Level Progressive Validation Semantics

Validation must proceed progressively through distinct phases; earlier levels never prove later ones:

| Level | Commands (Project-Aligned) | What It Proves | What It Does NOT Prove |
|---|---|---|---|
| **1. Evaluation** | `nix flake show`; `nix eval .#devShells.<sys>.default.drvPath`; `nix-instantiate shell.nix` | Expression evaluates and produces derivation for that system | That inputs can be fetched or built, or that the shell starts |
| **2. Realization + Shell Start** | `nix develop --command true`; `nix-shell --run true` | Store paths exist on host and shell initializes in command mode | That tools have correct versions or that project builds |
| **3. Environment Check** | `nix develop --command <tool> --version`; `command -v <tool>`; `pkg-config --modversion` (only if build uses it) | Named tools, versions, and variables are present in shell | That compilation, linking, or runtime commands succeed |
| **4. Project Command** | `nix develop --command <build/test/lint command>` | That specific command succeeded on tested host with current inputs | Other commands, platforms, or unpinned ecosystem downloads |

`nix flake check` sits beside this hierarchy: it evaluates recognized outputs and builds `checks.<system>`, but does not enter `devShells` or run project build commands unless a check explicitly does so.

---

## 4. Reference Architecture

The skill follows `build-skill/references/skeleton.md`: `SKILL.md` stays strictly $\le 80$ lines, while technical depth is organized into 5 dedicated reference files:

```text
skills/nix-devshell/
├── SKILL.md                               # Operational steps, report format, Your call (<= 80 lines)
└── references/
    ├── design-decisions.md                # Workflow, commands, inputs, systems, constructors, deps
    ├── native-deps.md                     # Outputs, hooks, pkg-config, compiler overrides, FHS/nix-ld
    ├── authoring-patterns.md              # Syntax pitfalls, mkShell arguments, standalone minimal patterns
    ├── validation-troubleshooting.md      # 6 execution phases, 4 validation levels, symptom table
    └── compatibility.md                  # Epistemic labels, inspection protocol, version caveats, sources
```

---

## 5. Repository Integration & Verification Gates

- **Installation**: Registered in `install.sh` under `ACTIVE_PORTABLE_SKILLS` in alphabetical order.
- **Documentation**: Documented in `README.md` under Portable Core table.
- **Change Management**: Authored on feature branch `feat/nix-devshell`; zero unapproved commits to `main`.
- **Dogfooding**: Validated through fresh-context subagents executing in 10 isolated fixture repositories under `~/Projects/tests/nix-devshell-dogfood/`.
