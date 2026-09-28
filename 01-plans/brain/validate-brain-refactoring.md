---
type: plan
status: active
project: brain
tags:
  - brain
  - tooling
  - validation
  - architecture
---

# Plan: Structural Refactoring for validate-brain.py Pipeline

## Status

- **Phase 1**: ✅ Implemented and passing (exit 0, Pyright clean)
- **Phase 2**: Diagnostics with line numbers — planned
- **Phase 3**: Shared linear fence parser — planned

## What Each Source Got Right

### Source 1 (Functional Refactor)
The incremental suggestion is **immediately actionable and safe**. Its core contributions:
- Single-pass file walk (eliminates 4× `rglob` traversals over 138 files)
- Checks as functions returning `list[str]` instead of mutating global state
- Unified `is_exempt()` that covers both `EXEMPT_PATTERNS` and `FRONTMATTER_EXEMPT_FILES`

These are correct and low-risk changes. The walrus operator (`DOTALL := re.DOTALL`) in the proposed `validate_mermaid` is a bug (`:=` is assignment, not argument), but the concept is sound.

### Source 2 (Architectural Redesign)
The extended critique is **accurate in almost every diagnosis**, but over-prescribes for this context. Points that are genuinely correct:

| Diagnosis | Verdict |
|---|---|
| Repeated `rglob` is wasteful | ✅ Correct — single-pass is better |
| Global mutable `errors` is fragile | ✅ Correct — hard to test, hard to trace |
| `any('Deprecated' in e for e in errors)` is a reporting smell | ✅ Strongly correct |
| Unused `warnings: list[str] = []` | ✅ Correct — dead code |
| Parsing and validation are coupled in frontmatter check | ✅ Correct |
| Fence-balance check and Mermaid extractor disagree on Markdown model | ✅ Correct — real risk as the repo grows |
| External tools (Ruff/Pyright) aren't modeled distinctly | ✅ Correct |
| Line numbers missing from diagnostics | ✅ High-value improvement |

Points that are over-engineered for this project:

| Suggestion | Verdict |
|---|---|
| `@dataclass ValidationConfig` | ❌ Over-engineered — constants at module scope are fine for one script |
| Separate `validation/` module tree (5–8 files) | ⚠️ Premature — 138 files, single author, single-purpose tool |
| `Issue` dataclass with `Severity` enum | ✅ Worth doing, but keep it minimal |
| `Document` dataclass | ✅ Worth doing — eliminates the repeated read problem cleanly |
| Actual Mermaid CLI invocation | ❌ Not yet — adds an external runtime dependency; the heuristic checks are sufficient for now |
| Full YAML parser for frontmatter | ⚠️ Desirable but blocked — `pyyaml` is not available without a dependency declaration |

---

## The Real Problems Worth Fixing Now

Ranked by impact vs. effort:

### 1. Repeated `rglob` + repeated file reads (High impact, Low effort)
The script reads each of the 138 files **four times**. A single-pass over a `Document` namedtuple fixes this completely.

### 2. Global mutable state at module scope (High impact, Low effort)
All execution currently runs at import time. A `main()` function with local state is the fix. This also makes the script importable for testing later.

### 3. The `any('Deprecated' in e...)` reporting smell (High impact, Trivial)
The per-check success/failure determination should use local error counts, not inspect the accumulated global error list.

### 4. Missing line numbers in diagnostics (Medium impact, Medium effort)
Currently: `Broken link in foo/bar.md: ../baz.md`
Should be: `foo/bar.md:47: broken relative link → ../baz.md`

This is the difference between a useful CI gate and a tool you have to go re-read to act on.

### 5. `Document` abstraction (Medium impact, Low effort)
A `NamedTuple` with `path`, `rel`, `content` eliminates the repeated variable binding (`rel = md.relative_to(ROOT)`, `content = md.read_text(...)`) across every loop.

### 6. `Issue` type (Low-Medium impact, Low effort)
Even a simple `NamedTuple(severity, path, line, message)` enables structured reporting — grouped by file, sortable by severity, extensible to warnings without a second global list.

---

## What NOT to Do

- **Don't split into multiple modules yet.** At 138 documents and one script, the complexity overhead of a `validation/` package outweighs the benefit. Do it if checks grow to 15+.
- **Don't add PyYAML.** It's not available without a dependency declaration. The regex frontmatter parser is adequate for the current schema (only `type` is enforced). If you add `status`, `tags`, `date` validation later, then declare the dependency properly.
- **Don't wire in the Mermaid CLI.** It's a large Node dependency, adds runtime setup to the Brain repo, and the heuristic checks already catch the class of errors the repo actually encounters.
- **Don't add a `ValidationConfig` dataclass.** The constants are already correctly separated at the top of the file. Wrapping them in a frozen dataclass adds type annotations without any behavioral benefit for a single-config tool.

---

## Target Architecture

Architecture implemented in [`scripts/validate-brain.py`](../../../scripts/validate-brain.py):

```
validate-brain.py
│
├── Configuration (module-level constants — unchanged)
│
├── Document NamedTuple
│   path: Path, rel: Path, content: str
│
├── Issue NamedTuple
│   severity: str, rel: Path | None, line: int | None, message: str
│
├── Discovery
│   discover_documents() → list[Document]  (single rglob pass)
│
├── Repository checks (no Document input needed)
│   check_deprecated_dirs() → list[Issue]
│   check_required_files() → list[Issue]
│
├── Document checks (accept Document, return list[Issue])
│   check_frontmatter(doc) → list[Issue]
│   check_links(doc) → list[Issue]
│   check_code_fences(doc) → list[Issue]
│   check_mermaid(doc) → list[Issue]
│
├── External checks
│   run_ruff() → list[Issue]
│   run_pyright() → list[Issue]
│
└── main()
    ├── discover
    ├── run all checks
    ├── collect issues
    └── report + exit
```

This is ~250–300 lines, stays in one file, requires zero new dependencies, and is backward-compatible with the pre-commit hook.

---

## Concrete False-Positive Risk the Second Source Identified

The mismatch between the fence-balance check and Mermaid extractor is a real latent bug. Consider this valid Markdown pattern:

````markdown
Here is an example of a mermaid block syntax:

```markdown
\```mermaid
flowchart LR
    A --> B
\```
```
````

The fence-balance check counts inner backtick lines; the Mermaid regex does too. They can disagree on what constitutes an "open" fence because neither builds a proper Markdown parse tree.

**Mitigation without a full parser:** strip code blocks before running both checks. Parse fences linearly (track open/close state) rather than counting. This eliminates the false-positive class without introducing a Markdown library dependency.

---

## Recommended Implementation Sequence

1. **Phase 1 (safe, immediate):** `main()` wrapper, `Document` namedtuple, single-pass discovery, `Issue` namedtuple, fix the reporting smell. No behavioral change. *(Complete)*
2. **Phase 2 (diagnostics):** Add line-number tracking to frontmatter, link, and Mermaid checks. Structured output by file.
3. **Phase 3 (Markdown model):** Replace the parallel fence-balance and Mermaid extraction with a shared linear fence parser that skips nested fences. Eliminates the false-positive class.
4. **Later / never:** Full YAML frontmatter parser, Mermaid CLI integration, multi-module split — only when the actual complexity warrants it.
