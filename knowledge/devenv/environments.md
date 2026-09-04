# Environment Management: devShells, direnv, and uv

Managing software dependencies spans multiple layers—from system-level shared libraries, to language-specific packages, to environment variables. Relying on a single tool to handle all layers inevitably leads to fragile environments, especially on a non-FHS distribution like NixOS. 

To maintain a reproducible architecture, responsibilities are strictly divided among three tools.

## The Responsibility Matrix

| Tool | Scope | Responsibilities |
| :--- | :--- | :--- |
| **Nix devShell** | System / OS level | Providing Python interpreters, C compilers, system libraries (e.g., `postgresql` client libs), and non-Python native CLI tools (e.g., `ruff`, `docker`). |
| **uv** | Python userland | Resolving Python packages (FastAPI, SQLAlchemy), writing the lockfile, and managing the local `.venv`. |
| **direnv** | Workflow / Shell level | Automating the activation of the devShell, the Python virtual environment, and exporting runtime secrets/environment variables. |

## Tool Overview

### 1. uv (The Package Manager)
`uv` handles the language layer. Its job is to resolve, lock, and install pure Python dependencies into an isolated virtual environment. 

*Boundary:* `uv` assumes a standard Linux environment. It cannot reliably manage or compile packages that require dynamically linked C-extensions or native system binaries on NixOS. *(See: Anatomy of a devShell for details on native dependency resolution).*

### 2. Nix devShell (The Workshop)
A devShell abstracts away the host operating system. Rather than installing libraries globally, it rewires the terminal's environment variables to point directly to the exact system dependencies required by the project.

*Boundary:* The devShell handles what the operating system *should* provide, ensuring any developer cloning the repository gets the exact same binaries, regardless of whether they use NixOS, macOS, or Ubuntu.

### 3. direnv (The Orchestrator)
`direnv` is a shell extension that watches directories. Upon entering a project folder with an `.envrc` file, it automatically loads the environment.

*Boundary:* `direnv` does not install or build software. It simply answers the question: *"What environment variables and shells should be active right now?"* ## Analyzing the Trade-offs

Choosing to implement this trifecta introduces specific trade-offs:

* **Complexity vs. Reproducibility:** * *Cost:* Introducing Nix syntax and flake evaluation into a standard Python project increases the cognitive load for developers unfamiliar with Nix.
    * *Benefit:* Absolute guarantee that the environment can be reproduced identically years from now.
* **Maintenance Cost:** * *Cost:* There are now two sources of truth for dependencies: `flake.nix` for system libraries and tools, and `pyproject.toml`/`uv.lock` for Python libraries. 
    * *Benefit:* Total isolation. You must deliberately decide where a dependency belongs, preventing Python packages from corrupting system tools and vice versa.

## Environment Management in BiteTrack

BiteTrack utilizes all three tools in tandem. 

The initial bootstrapping attempt relied solely on `uv` and `direnv`. However, the environment hit a hard limitation when native developer tooling (specifically, the pre-compiled Rust binary for Ruff) crashed due to missing dynamic libraries on NixOS. 

Instead of modifying the host OS, the project architecture was updated:
1.  **`devShell`** provisions the native tools (`ruff`, `uv` executable) and core libraries.
2.  **`uv`** manages the FastAPI application dependencies.
3.  **`direnv`** silently orchestrates both upon entering the directory.
