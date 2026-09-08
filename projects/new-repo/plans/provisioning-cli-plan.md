---
type: plan
status: active
project: new-repo
tags:
  - gitea
  - github
  - rust
  - automation
  - cli
  - sops
---
# 📋 Implementation Plan — `new-repo` Provisioning CLI

## 🎯 Objective
Build a fast, type-safe, and self-contained Rust command-line tool (`new-repo`) to provision repositories across self-hosted Gitea and GitHub with automated push mirroring, template generation, and zero plaintext secret leakage.

**Repository Location**: [`/home/kiskaadee/Projects/active/new-repo`](file:///home/kiskaadee/Projects/active/new-repo)

---

## 🛠️ CLI Interface Specification

Built with `clap` derive macros:

```text
Usage: new-repo <NAME> [OPTIONS]

Arguments:
  <NAME>                  Name of the repository to create

Options:
  -s, --source <FORGE>    Primary forge: 'gitea' (default) or 'github' [default: gitea]
  -M, --no-mirror         Disable offsite push mirroring to GitHub
  -t, --template <NAME>   Optional Gitea template repository to generate from
  -l, --license <NAME>    License identifier [default: UNLICENSE]
  -p, --public            Make repository public (default is private)
  -c, --clone             Automatically clone repository to local directory after creation
  -h, --help              Print help information
  -V, --version           Print version information
```

---

## 🏛️ Core Architecture & Traits

The utility adheres to a decoupled architecture separating orchestration from network and secret I/O:

```text
                    ┌─────────────────────────┐
                    │         main.rs         │
                    │  (CLI Parse & Config)   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     RepoManagerService  │
                    │   (Domain Orchestration)│
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
    SecretProvider         GiteaClient            GitHubClient
          │                      │                      │
          ▼                      ▼                      ▼
     sops CLI (RAM)         HTTPS REST             HTTPS REST
```

### Key Traits:

1. **`SecretProvider`**:
   - `fn get_github_mirror_token(&self) -> Result<SecretString, Error>`
   - Invokes `sops -d --extract '["github_mirror_token"]' <secrets_file>` and captures stdout in-memory.
2. **`GiteaClient`**:
   - `fn create_repo(&self, opts: &CreateRepoOptions) -> Result<RepoInfo, Error>`
   - `fn generate_from_template(&self, template: &str, opts: &GenerateOptions) -> Result<RepoInfo, Error>`
   - `fn create_push_mirror(&self, repo: &str, mirror: &PushMirrorOptions) -> Result<(), Error>`
3. **`GitHubClient`**:
   - `fn create_repo(&self, name: &str, is_private: bool, license: &str) -> Result<(), Error>`

---

## 🔒 Security Invariants

1. **No Tokens in CLI Flags**: Tokens are injected exclusively via HTTP request headers (`Authorization: token <token>`), preventing process table visibility in `/proc/$PID/cmdline`.
2. **In-Memory Lifetime**: Tokens exist only for the duration of the API call and are dropped/zeroized immediately.
3. **Fallback Safety**: If GitHub repo creation fails or mirror attachment fails, the Gitea repo is retained and clear diagnostic error messages are returned.

---

## 📋 Implementation Milestones

### Milestone 1 — CLI & Config Definition
- Configure `Cargo.toml` dependencies: `clap` (derive), `reqwest` (json, blocking), `serde`, `serde_json`, `thiserror`, `secrecy`.
- Define CLI arguments, default values, and parsed configuration structs.

### Milestone 2 — SOPS Secret Extraction
- Implement `SopsSecretProvider` executing `sops` subprocess.
- Secure capture of `github_mirror_token` into `SecretString`.

### Milestone 3 — Gitea API Client
- Implement standard repository creation (`POST /user/repos`).
- Implement template-based repository generation (`POST /repos/{owner}/{template}/generate`).
- Implement push mirror configuration (`POST /repos/{owner}/{repo}/push_mirrors`).

### Milestone 4 — GitHub API Client
- Implement empty repository creation on GitHub (`POST /user/repos`) using the extracted token.

### Milestone 5 — Service Orchestration & Local Git Workflow
- Implement `RepoManagerService` tying together Gitea creation, GitHub target creation, and mirror setup.
- Add optional `-c / --clone` execution running `git clone`.

### Milestone 6 — Testing & Nix Packaging
- Write unit tests with mock client implementations.
- Package `new-repo` via Nix flake / Home Manager.
