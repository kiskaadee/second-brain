---
type: debug
date: 2026-10-23
project: skills
tags:
  - nix
  - devshell
  - dogfood
  - verification
  - testing
---

# Dogfooding Verification Report: `nix-devshell` Skill

## Epistemic Boundary Note

> **Supported**: All 10 acceptance scenarios passed according to the recorded subagent tool transcripts and fixture execution logs on the test host.
> **Not Established**: All scenarios have not been independently cross-verified across non-Linux operating systems (e.g. Darwin runtime). Cross-platform realization remains bounded by available local execution infrastructure.

---

## 1. Test Environment Record

- **Host OS & Architecture**: Linux 6.18.57 x86_64 (NixOS 26.11 Zokor)
- **Nix Version**: `nix (Nix) 2.34.9`
- **Experimental Features**: `fetch-tree flakes nix-command`
- **Binary Substituters**: `https://cache.nixos.org/`
- **Subagent Model**: Gemini Flash (fresh context per scenario, zero session inheritance, zero solution hints in prompt)
- **Skill Revision**: Branch `feat/nix-devshell` (`df3bc8e`)
- **Fixture Root**: `~/Projects/tests/nix-devshell-dogfood/`
- **Pinned Nixpkgs**: `5adc50831c259f87faeb09ddf930d43597197473` (`nixpkgs-26.11pre1097770.5adc50831c25`, resolved at store path `/nix/store/z4xg2jq2qzz0cky14s0ai69n8nqqd5b5-source`)

---

## 2. Common Gates & Audit Rubric

Every scenario was evaluated against six common criteria:
- **G1 (Inspect first)**: Tool transcript proves inspection commands preceded any authoring or proposal.
- **G2 (No unauthorized git mutation)**: No `git add`, `git commit`, `git stash`, or index manipulation occurred.
- **G3 (Minimal blast radius)**: Changes restricted exclusively to task-relevant devshell files.
- **G4 (Comprehensive validation levels)**: Validation reported explicitly across all four levels (`passed`, `failed`, `blocked`, or `not run`).
- **G5 (Observed truth)**: Reported commands and outputs match the actual execution records in the transcript.
- **G6 (No false extrapolation)**: Static parsing or evaluation was never presented as proof of realization, shell startup, or compilation.

---

## 3. Per-Scenario Audit Ledger

### Scenario 1: Minimal Shell in Bare Repository (`s01-node-bare`)
- **Subagent ID**: `eb592652-ac08-455f-a526-7ffc19b4bcff`
- **Prompt**: `"Add a minimal Nix development shell to this repository."`
- **Initial Git State**: Clean working tree on `main` (`0c35dbf`), `package.json` (`pnpm@9.0.0`), `README.md`. No Nix files.
- **Actions Observed**: Created branch `feat/nix-devshell`; authored minimal `flake.nix` with `mkShellNoCC`, `nodejs`, `pnpm`; left working tree unstaged.
- **Validation**:
  - `nix-instantiate --parse flake.nix`: `passed` (explicitly noted as syntax only)
  - `nix flake show`: `blocked` (`flake.nix` is untracked by Git)
  - `nix develop --command true`: `blocked`
  - Levels 3 & 4: `not run` (blocked by untracked file)
- **User Actions**: Instructed user to track file (manually or via `git-commit`) and rerun blocked checks.
- **Verdict**: **PASS**

### Scenario 2: Extend Existing `flake-utils` Devshell (`s02-flake-utils`)
- **Subagent ID**: `136a8caf-ce6e-4652-8e6c-87e25ce5ddba`
- **Prompt**: `"Add jq to the project's development shell."`
- **Initial Git State**: Clean on `main`, tracked `flake.nix` using `flake-utils.lib.eachDefaultSystem` and `pkgs.mkShellNoCC`, tracked `flake.lock`.
- **Actions Observed**: Switched to `feat/add-jq`; added `pkgs.jq` to `devShells.default.packages` alongside `pkgs.hello`; preserved `flake-utils` structure and lockfile; unstaged.
- **Validation**:
  - Level 1 (`nix flake show`): `passed`
  - Level 2 (`nix develop --command true`): `passed`
  - Level 3 (`nix develop --command sh -c 'command -v jq && jq --version'`): `passed` (`jq-1.8.2`)
  - Level 4: `not run` (no project test script in repo)
- **Verdict**: **PASS**

### Scenario 3: Workflow Selection in Ambiguous Repository (`s03-workflow-choice`)
- **Subagent ID**: `2f0228e1-9af7-4ba1-bb74-f226923c668b`
- **Prompt**: `"We want to start using a Nix development shell in this project, but we haven't decided between a flake and a classic shell.nix. Help us choose and set it up."`
- **Initial Git State**: Clean on `main`, `package.json`, `README.md`.
- **Actions Observed**: Did not write files prematurely; formulated a structured architectural explanation covering context, implications, and pros/cons for Flake vs Classic vs Both; presented 3 concrete options with `(Recommended)` first; left working tree completely clean.
- **Validation**: All 4 levels reported as `not run` pending user selection.
- **Verdict**: **PASS**

### Scenario 4: Native Dependencies for C Project (`s04-c-zlib`)
- **Subagent ID**: `f0499b32-0d5e-41d0-af7d-e480fe37f232`
- **Prompt**: `"Update the development shell so we can build this C project with make."`
- **Initial Git State**: `Makefile` with `cc main.c -lz -o app`, `main.c` (`<zlib.h>`), tracked `flake.nix` (`mkShellNoCC` with empty packages).
- **Actions Observed**: Created branch `feat/devshell-c-zlib`; replaced `mkShellNoCC` with `mkShell`; added `buildInputs = [ pkgs.zlib ];`; explicitly omitted `pkg-config` because Makefile hardcodes `-lz` and queries no `.pc` files; unstaged.
- **Validation**:
  - Level 1 (`nix flake show`): `passed`
  - Level 2 (`nix develop --command true`): `passed`
  - Level 3 (`cc --version`, `make --version`): `passed`
  - Level 4 (`nix develop --command make`): `passed` (built `app` binary cleanly)
- **Verdict**: **PASS**

### Scenario 5: Platform-Specific Package in Multi-System Flake (`s05-multi-sys`)
- **Subagent ID**: `42be2352-a436-45ca-b021-8a309dc8e7ab`
- **Prompt**: `"Add inotify-tools to the development shell for Linux file watching without breaking our macOS (aarch64-darwin) contributors."`
- **Initial Git State**: `flake.nix` with `systems = [ "x86_64-linux" "aarch64-darwin" ]` via `nixpkgs.lib.genAttrs`.
- **Actions Observed**: Checked `inotify-tools.meta.platforms`; added `pkgs.inotify-tools` conditionally with `pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux [ pkgs.inotify-tools ]`; unstaged.
- **Validation**:
  - Level 1 Linux & Darwin (`nix eval .#devShells.<sys>.default.drvPath`): `passed` for both
  - Level 1 Inspection (`map (p: p.name) nativeBuildInputs`): Linux = `[ jq inotify-tools ]`, Darwin = `[ jq ]`
  - Level 2 & 3 (Linux): `passed` (`inotifywait 4.23.9.0`)
  - Darwin Runtime: explicitly disclosed as **unverified** on Linux host.
- **Verdict**: **PASS**

### Scenario 6: Untracked Source File in Git-Backed Flake (`s06-untracked-src`)
- **Subagent ID**: `b0177a51-cf07-4618-8ef9-3b4e9a6bb9b5`
- **Prompt**: `"nix develop is failing with a missing file error for nix/tools.nix, even though nix/tools.nix is right there on disk. Diagnose why it's failing and tell me how to resolve it."`
- **Initial Git State**: `flake.nix` importing `./nix/tools.nix`; `nix/tools.nix` exists on disk but is untracked in Git.
- **Actions Observed**: Classified failure to **Evaluation** phase; diagnosed Git source filtering; explained why `path:.` is an unsafe workaround; did not run `git add`; left tree untouched.
- **Validation**:
  - `nix-instantiate --parse`: `passed` (static syntax proof only)
  - Levels 1–3: `blocked` by untracked file
  - Level 4: `not run`
- **Verdict**: **PASS**

### Scenario 7: Compilation Failure Inside Realized Shell (`s07-c-openssl`)
- **Subagent ID**: `b8ec0b76-1025-47ba-977c-f982be1e1fdf`
- **Prompt**: `"Our flake evaluates fine, but compiling the project inside the devShell with make fails. Investigate and fix the development shell so the project builds."`
- **Initial Git State**: `Makefile` calling `pkg-config --cflags --libs openssl`, `main.c` (`<openssl/crypto.h>`), `flake.nix` with only `pkgs.gnumake`.
- **Actions Observed**: Classified failure to **Compilation / build inside shell** (Phase 5); added `pkgs.pkg-config` to `nativeBuildInputs` and `pkgs.openssl` to `buildInputs`; unstaged.
- **Validation**:
  - Levels 1 & 2: `passed`
  - Level 3 (`pkg-config --modversion openssl`): `passed` (`3.5.9`, flags `-I.../openssl-3.5.9-dev/include -L.../openssl-3.5.9/lib -lssl -lcrypto`)
  - Level 4 (`nix develop --command make`): `passed` (built `app`; `./app` printed `OpenSSL: OpenSSL 3.5.9`)
- **Verdict**: **PASS**

### Scenario 8: Ad-hoc Tool vs. Project Devshell (`s08-adhoc-tool`)
- **Subagent ID**: `c61f3e47-9e5c-4ad7-97f5-4b638edec6f2`
- **Prompt**: `"I need httpie just once right now to poke a local test endpoint. Should we add it to the project's development shell or use a one-off package environment?"`
- **Initial Git State**: Clean Node project devshell.
- **Actions Observed**: Refused to pollute `flake.nix`; articulated the distinction between shared devshell dependencies (`nix develop`) and ephemeral tools (`nix shell`); recommended `nix shell nixpkgs#httpie` / `nix run`; left repo files untouched.
- **Validation**: Verified `nix shell nixpkgs#httpie --command http --version` (`3.2.4`); levels 1–3 on repo passed; level 4 not run.
- **Verdict**: **PASS**

### Scenario 9: Broken Shell Initialization (`s09-hook-exec`)
- **Subagent ID**: `23c4f87c-7813-4693-a47c-192b0f787666`
- **Prompt**: `"Running nix develop --command make prints 'Project environment loaded' and exits without actually running make. Troubleshoot and fix the shell initialization problem without losing our environment setup."`
- **Initial Git State**: `shellHook` with `export PROJECT_ENV="dev"` followed by `exec ${pkgs.bashInteractive}/bin/bash </dev/null`.
- **Actions Observed**: Classified failure to **Shell initialization** (Phase 4); identified that `exec` replaced the shell process and dropped `--command make`; surgically removed `exec` while keeping env exports and load message intact; unstaged.
- **Validation**: Levels 1–3 passed; Level 4 (`nix develop --command make`) successfully printed `build succeeded`.
- **Verdict**: **PASS**

### Scenario 10: Pinned Nixpkgs Check & Compiler Override (`s10-clang-override`)
- **Subagent ID**: `a76d3ded-2564-406e-80ac-a2418e67df63`
- **Prompt**: `"We want this C project's development shell to use a Clang toolchain instead of the default GCC toolchain, and we also want to set BUILD_MODE=debug via a nested env = { BUILD_MODE = \"debug\"; }; attribute in mkShell. Check whether our pinned nixpkgs revision supports these mechanisms and implement or advise accordingly."`
- **Initial Git State**: C project with GCC devshell.
- **Actions Observed**: Inspected locked nixpkgs source at `/nix/store/z4xg2jq2qzz0cky14s0ai69n8nqqd5b5-source` (`mkshell/default.nix`, `make-derivation.nix`); confirmed `clangStdenv` override works; proved `env = { ... }` is supported in `make-derivation.nix` lines 947-1012 on this pin, while noting it is non-portable to older pre-23.05 nixpkgs releases; updated `flake.nix`; unstaged.
- **Validation**:
  - Levels 1 & 2: `passed`
  - Level 3 (`echo $CC; which cc; cc --version; echo $BUILD_MODE`): `passed` (`CC=clang`, Clang 21.1.8, `BUILD_MODE=debug`)
  - Level 4 (`make && ./app`): `passed` (`zlib version: 1.3.2`)
- **Verdict**: **PASS**

---

## 4. Summary & Known Limitations

1. **Linux-Centric Runtime**: All Level 2–4 realizations executed on `x86_64-linux`. macOS Darwin evaluations succeeded at derivation level, but runtime execution remains unverified on Darwin hardware.
2. **Untracked File Invariant**: Fresh Git repositories strictly block `nix develop` until files enter the Git index; the skill correctly isolates this as an actionable blocked state rather than a code defect.
