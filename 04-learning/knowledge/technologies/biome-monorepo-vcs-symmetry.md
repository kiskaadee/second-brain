---
type: knowledge
status: stable
topics: ['frontend', 'biome', 'tooling', 'monorepo']
---

# Biome Linter Monorepo Symmetry & VCS Root Resolution

## 1. Problem: Configuration Asymmetry in Polyglot Repositories

In modern fullstack or polyglot application repositories (e.g. FastAPI/Go/Rust backend + React/Vite SPA frontend), developer tooling presents a layout dilemma:

* **Backend Tooling Autonomy**: Python tools like `uv`, `ruff`, or `pytest` locate their configuration strictly via directory traversal for `pyproject.toml`. They operate completely indifferent to Git repository root boundaries.
* **Frontend Tooling Creep**: By contrast, JS/TS linters historically placed configuration files (`.eslintrc.json`, `prettierrc`, or `biome.json`) at the repository root. When Biome has Git integration enabled (`vcs: { enabled: true, useIgnoreFile: true }`), placing `biome.json` inside `frontend/` causes Biome to fail if executed from a subfolder without its own local `.gitignore`:
  ```text
  internalError/fs: Biome couldn't find an ignore file
  ```
* **The Asymmetry**: This often pushes developers to put `biome.json` at the root, making the repository root asymmetric: Python is cleanly encapsulated in `backend/`, while JavaScript tooling pollutes the top-level directory.

---

## 2. Solution: VCS Root Resolution (`vcs.root`)

Biome v2 introduces explicit version control root configuration via `vcs.root`. By pointing the VCS root to the parent directory (`".."`), `biome.json` can live strictly inside `frontend/` while honoring the root `.gitignore`:

```json
{
  "$schema": "https://biomejs.dev/schemas/2.5.14/schema.json",
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true,
    "root": ".."
  },
  "files": {
    "ignoreUnknown": true,
    "includes": ["src/**", "vite.config.ts"]
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 90
  },
  "linter": {
    "enabled": true,
    "rules": {
      "preset": "recommended"
    }
  }
}
```

---

## 3. Structural Comparison

```text
Asymmetric Layout (Avoid)             Symmetric Layout (Preferred)
----------------------------------     ----------------------------------
repo/                                  repo/
├── backend/                           ├── backend/
│   ├── app/                           │   ├── app/
│   └── pyproject.toml                 │   └── pyproject.toml
├── frontend/                          ├── frontend/
│   ├── src/                           │   ├── src/
│   └── package.json                   │   ├── biome.json   <-- vcs.root = ".."
├── biome.json      <-- Leaks out      │   └── package.json
├── shell.nix                          ├── shell.nix
└── .gitignore                         └── .gitignore
```

### Operational Ergonomics
1. **Isolated Sub-Workspaces**: `frontend/` and `backend/` are both completely self-contained. Deleting, copying, or testing either layer requires no root cleanup.
2. **Seamless CI & DevShell**: From the repository root, commands can target the folder directly (`cd frontend && biome check .` or `nix-shell --run "cd frontend && npm run lint"`).
3. **Zero Ignore Duplication**: All ignore rules remain centralized in the root `.gitignore`.
