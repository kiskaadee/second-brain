# The Anatomy of a devShell

## Motivation
A devShell is the Nix solution to the eternal development issue of "it works on my machine" at the system level. 

With one important caveat: it is not primarily about installing packages. It is about reproducing an entire development environment. Rather than assuming the host machine already contains the correct compiler, linker, libraries, and development tools, a devShell declares those requirements explicitly and recreates them whenever the project is opened.

## Why I needed one
While bootstrapping BiteTrack, I discovered that several tools installed by `uv` did not execute correctly under NixOS. For example, Ruff is distributed as a native executable. The executable expected libraries (like `glibc`) to exist in standard Linux FHS locations (e.g., `/lib64/ld-linux-x86-64.so.2`) that do not exist on NixOS, causing:

> `Could not start dynamically linked executable...`

Instead of modifying my operating system with `nix-ld`, I decided to make the project self-contained by declaring its system dependencies inside a project-local `flake.nix`.

## What a devShell Provides
A Nix devShell constructed via `mkShell` manipulates the shell environment to expose specific software and libraries without installing them globally. 

* **System Executables (`PATH`):** Packages declared in `packages` (like `uv` and `ruff`) have their `/bin` directories prepended to `$PATH`. The shell uses the Nix store paths directly.
* **Shared Libraries:** Standard Linux distributions rely on global library paths. Nix compiles packages to look for their dependencies via absolute paths in the Nix store (using `RPATH`). 
* **Environment Variables:** Standard builder variables are set automatically. Custom variables can be injected (e.g., `env.FOO = "bar";`), but manual manipulation of `LD_LIBRARY_PATH` often leads to symbol collisions if not handled carefully, as it overrides the explicitly linked `RPATH` of other Nix-provided binaries.
* **Compilers & Toolchains:** By providing `stdenv` or specific libraries (like `zlib`, `openssl`, `libffi`), the shell ensures that any tools compiled dynamically inside the environment (such as Python C-extensions) link against the exact library versions declared in the flake.

## devShell and UV: Separation of Concerns

To avoid system-level conflicts, dependencies are strictly partitioned based on their execution requirements:

| Component | Managed By | Rationale |
| :--- | :--- | :--- |
| `uv` executable | Nix | Requires native execution and dynamically linked system libraries. |
| `ruff` | Nix | Pre-compiled native Rust executable. Fails under FHS assumptions without `nix-ld`. |
| Compiler Toolchain | Nix | Provides `glibc`, `stdenv`, `libffi` for compiling native extensions. |
| System Libraries | Nix | OpenSSL, PostgreSQL (`libpq.so`) needed by Python packages at runtime. |
| Python Virtualenv | `uv` | Strictly isolates project-specific Python dependencies. |
| `pytest` | `uv` | Pure Python package/script; executes safely within the interpreter. |
| `pyright` | `uv` | Node-based but wrapped via PyPI; executes via the local interpreter environment. |
| FastAPI / App Code | `uv` | Core application logic; belongs in the isolated Python environment. |

## Why Not `nix-ld`?

A common workaround for dynamic linker issues in NixOS is enabling `nix-ld` in the declarative global configuration. `nix-ld` provides a shim at the standard FHS linker path that redirects executions to the Nix store. 

**nix-ld**
* **Pros:** Fixes the whole machine. Pre-compiled binaries downloaded from the internet (via `uv`, `npm`, `cargo`) usually execute without modification.
* **Cons:** Requires global system configuration. Compromises the strict purity and reproducibility of Nix, as projects will suddenly rely on the host machine having `nix-ld` enabled rather than declaring their own dependencies.

**devShell**
* **Pros:** Strictly project-local and reproducible. Documents exact system requirements. Highly portable across any system running the Nix package manager (including macOS or Ubuntu via WSL).
* **Cons:** Requires an extra `flake.nix` file. Requires manually triaging which tools must be moved from standard package managers (like `uv`) into Nix.

The commitment in the BiteTrack project is to achieve a declarative and reproducible environment. Using a devShell saves time for any hypothetical developer onboarding to the project by eliminating "environment-related" setup bugs.

## Lessons Learned

* **Native executables and Python packages are different concerns:** Tools distributed as binaries (Ruff) belong in Nix. Tools executing strictly via the Python interpreter belong in `uv`.
* **A tool failing first is not necessarily the source of the bug:** The `glibc` symbol mismatch affecting Starship was a downstream casualty of manually forcing `LD_LIBRARY_PATH` into the environment. 
* **`LD_LIBRARY_PATH` should not be modified casually:** It overrides library lookups globally for the shell, breaking tools that rely on specific, different versions of those libraries.
* **`direnv` simply loads the shell:** It is an orchestrator, not the underlying problem when a shell fails to load correctly.
* **A reproducible environment is easier to debug than a globally configured one:** Isolation prevents cross-contamination of dependencies.

## Future Improvements

Investigate the following approaches to further optimize or simplify the Nix/Python bridge:
* `devenv.sh`
* `dream2nix`
* `uv2nix`
* `devenv` test support
* Managing multiple Python versions within the flake

## External Resources
* [Easy development environments with Nix and Nix flakes!](https://dev.to/arnu515/easy-development-environments-with-nix-and-nix-flakes-21mb)
* [Declarative shell environments with `shell.nix`](https://nix.dev/tutorials/first-steps/declarative-shell.html)
* [Making a dev shell with nix flakes](https://fasterthanli.me/series/building-a-rust-service-with-nix/part-10)
* [Development shells with Nix: four quick examples (2025)](https://michael.stapelberg.ch/posts/2025-07-27-dev-shells-with-nix-4-quick-examples/)

