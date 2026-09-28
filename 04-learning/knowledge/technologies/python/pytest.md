---
type: knowledge
status: stable
topics: ['pytest', 'python', 'testing', 'dependency-injection']
related: ['../../methods/testing.md']
---

# Pytest Fixtures & Dependency Injection Guide

## 1. Core Concept: Dependency Injection (DI)

**Dependency Injection** is a design pattern where an object or function receives its dependencies (collaborators, state, configuration, clients) from the outside rather than creating or importing them internally.

```
Without DI (Hardcoded Global Dependency):
┌────────────────────────────┐
│    test_resolve_app()      │───▶ Hardcodes SITES_DIR = "~/Sites" (Untestable, leaks state)
└────────────────────────────┘

With Dependency Injection (DI):
┌────────────────────────────┐
│ tmp_path, monkeypatch (DI) │───▶ Injected by Pytest per-test (Isolated, automatically torn down)
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│    test_resolve_app()      │
└────────────────────────────┘
```

---

## 2. Essential Built-in Pytest Fixtures

| Fixture | Type | Primary Use Case |
| :--- | :--- | :--- |
| **`monkeypatch`** | `pytest.MonkeyPatch` | Safely patch environment variables (`setenv`), module attributes (`setattr`), or dictionary keys with guaranteed teardown. |
| **`tmp_path`** | `pathlib.Path` | Creates a unique, temporary directory per test function. Cleaned up after test runs. |
| **`capsys`** | `CaptureFixture` | Captures text written to `sys.stdout` and `sys.stderr` for asserting CLI output. |
| **`caplog`** | `LogCaptureFixture` | Captures log messages emitted via Python's standard `logging` library. |
| **`request`** | `FixtureRequest` | Provides introspection into the requesting test (e.g. test name, markers, parameterized values). |

---

## 3. Writing Custom Fixtures (`conftest.py`)

When you define fixtures in a root `conftest.py` file, they become globally available to every test in the repository without needing imports.

### A. Factory & Data Fixtures
```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def mock_sites_dir(tmp_path: Path) -> Path:
    """Create a mock ~/Sites directory with sample apps."""
    sites = tmp_path / "Sites"
    app_dir = sites / "homelab-jellyfin"
    app_dir.mkdir(parents=True)
    (app_dir / "app.yaml").write_text("name: jellyfin\naliases: [media]\n")
    return sites
```

### B. Setup & Teardown with `yield`
```python
@pytest.fixture
def clean_database():
    # 1. Setup (runs before test)
    db = start_test_db()
    
    yield db  # 2. Injected into test
    
    # 3. Teardown (runs after test completes)
    db.truncate_all()
```

### C. Fixture Scopes
Control how frequently a fixture is created:
* `scope="function"` *(default)*: Fresh instance for every single test function.
* `scope="module"`: Instantiated once per Python test file.
* `scope="session"`: Instantiated once for the entire `pytest` test run (e.g. spinning up a Docker container).

---

## 4. Curated Learning Resources

### Definitive Books
1. **[Python Testing with pytest](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)** by Brian Okken (Pragmatic Bookshelf)
   - *The industry standard reference on pytest fixtures, test parametrization, and fixture scopes.*
2. **[Architecture Patterns with Python (Cosmic Python)](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html)** by Harry Percival & Bob Gregory (O'Reilly, free online)
   - *Chapter 13 specifically explains the theory, design patterns, and benefits of Dependency Injection in modern Python applications.*

### Official Documentation & Deep Dives
* **[Official Pytest Fixtures Explanation](https://docs.pytest.org/en/stable/explanation/fixtures.html)** — Pytest's official conceptual guide explaining the philosophy behind fixture dependency injection.
* **[Pytest Monkeypatch Reference](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)** — Comprehensive examples of `setattr`, `setenv`, `delenv`, and `syspath_prepend`.
