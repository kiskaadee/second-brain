---
type: debug
date: 2026-09-26
tags: [brain, tooling, validation, python, mermaid, regex]
---

# validate-brain.py Refactor — Debug Postmortem

## Initial Incident

`validate-brain.py` reported 0 errors. Obsidian disagreed: it displayed a Mermaid parse error inside `projects/magnetflix/README.md`.

```
Error parsing Mermaid diagram!
Parse error on line 35:
...>|gRPC Event Stream (SSE)| Worker    Wo
----------------------------^
Expecting 'SQE', 'DOUBLECIRCLEEND', 'PE', '-)', 'STADIUMEND', 'SUBROUTINEEND',
'PIPE', 'CYLINDEREND', 'DIAMOND_STOP', 'TAGEND', 'TRAPEND', 'INVTRAPEND',
'UNICODE_TEXT', 'TEXT', 'TAGSTART', got 'PS'
```

The validator gave a clean pass on a diagram that Mermaid's own Jison parser rejected. The discrepancy is the incident.

---

## Root Cause Analysis

Two independent bugs in Check 7 (Mermaid edge label validation).

### Bug 1 — Arrow regex too narrow

The edge label extraction regex was:

```python
r'-->\|([^|]+)\|'
```

This matched only forward arrows (`-->`). The failing line was:

```
BFF <-->|gRPC Event Stream (SSE)| Worker
```

A bidirectional arrow (`<-->`) does not begin with `-->`, so the regex produced no match. The label was never extracted, never inspected, and the parentheses inside it were never flagged.

### Bug 2 — Special character set incomplete

Even when a label was extracted, the check only tested for `['*', '/']`:

```python
if any(ch in label for ch in ['*', '/']):
```

The comment above the check read *"or unescaped parens"*, but `(` and `)` were not in the list. In Mermaid's Jison grammar, an unquoted `(` in an edge label is tokenized as `PS` (Paren Start) — the same token that begins a stadium-shape node definition. The grammar does not expect `PS` at that position, so parsing fails at the character that triggers the token.

The validator's comment described behaviour the code did not implement. The claim and the implementation diverged silently.

---

## Immediate Fix

Two targeted changes:

1. **Arrow regex broadened** to match any arrow variant:
   ```python
   r'[-.=~<>]*\|([^|]+)\|'
   ```
2. **Character set expanded** to include parentheses, brackets, and braces:
   ```python
   ['*', '/', '(', ')', '[', ']', '{', '}']
   ```

Three edge labels across two files were then quoted to satisfy the check.

---

## Architectural Finding

The two bugs were symptoms of a script structure that made them easy to introduce and hard to detect:

- **Global mutable `errors: list[str]`** — a single flat list shared across all checks; no structured result type, no source location, no check identity attached to each entry.
- **`any('Deprecated' in e for e in errors)` pattern** — the presentation layer inspected error message strings to make control-flow decisions. Behaviour was encoded in prose rather than in data.
- **4× `rglob` traversals** — each check independently walked the directory tree. No shared document model; no single point to enforce exemption policy.
- **Two independent Markdown fence parsers** — a line-by-line counter used by the fence-balance check and a `re.DOTALL` regex used by the Mermaid check. Both parsed the same documents using different logic, producing results that could contradict each other.
- **All execution at module scope** — `main()` did not exist; the script was not importable, not testable, and not composable.

The bugs in Check 7 survived because there was no test harness and no shared fence model against which the Mermaid extractor's output could be verified.

---

## Refactor

Three phases, each independently verifiable against the baseline output captured before Phase 1 began.

### Phase 1 — Structural skeleton

- Introduced `Issue` and `Document` `NamedTuple`s as the canonical result and input types.
- Wrote `discover_documents()` as the single file-discovery entry point, encoding all exemption policy in one place.
- Converted every check to a function returning `list[Issue]`.
- Introduced `main()` and `report()` as the only module-scope execution sites.

### Phase 2 — Precise source locations

- Added `_line_of(path, text)` — a helper that locates the line number of any substring within a file.
- Every `Issue` produced by every check now carries a line number.
- `report()` formats all output as `path:line: message`, matching the convention used by most editors and CI tools.

### Phase 3 — Shared fence model

- Replaced both independent fence parsers with a single `scan_code_blocks()` linear scanner.
- Introduced the `CodeBlock` `NamedTuple` (`language`, `body`, `start_line`, `end_line`).
- `check_code_fences()` and `check_mermaid()` both consume the output of `scan_code_blocks()`. They share the same fence model; contradictory results on the same document are structurally impossible.

---

## False-Positive Class Eliminated

The original DOTALL regex:

```python
r'```mermaid\s*\n(.*?)\n```'
```

would extract a `mermaid` block from inside a ` ````markdown ` documentation fence — treating inner fence lines as top-level Mermaid source. The linear scanner correctly identifies the outer fence as `language=markdown` and treats all content between the outer delimiters as body text. Inner fence lines are never interpreted as fence boundaries.

This was verified with an explicit test case containing a nested fence before Phase 3 was committed.

---

## Declarative Remediation Summary

| Commit | Phase | Change |
| :--- | :--- | :--- |
| `fd4bdb1` | Phase 1 | Structural skeleton: `Issue`, `Document`, `discover_documents()`, check functions, `main()`, `report()` |
| `7018822` | Phase 2 | Precise line numbers: `_line_of()`, `path:line` prefix in all output |
| `c7780b3` | Phase 3 | Shared fence model: `scan_code_blocks()`, `CodeBlock`, unified `check_code_fences()` and `check_mermaid()` |

Final state: exit 0, Pyright 0 errors, 0 warnings.

---

## Lessons Learned

1. **An uncovered check comment is a lie.** The Mermaid validator's comment said *"or unescaped parens"* but the code did not check for them. Comments that describe intended behaviour without being verified by tests are misinformation.

2. **Parsing and validation must share a model.** Two independent fence parsers can produce contradictory results on the same document. A shared model makes that class of disagreement structurally impossible.

3. **Behavioural specification before refactor.** Capturing the exact output before Phase 1 began gave a concrete regression target. Phase 1 was required to produce identical pass/fail decisions and identical error messages — not approximately the same, exactly the same.

4. **Stopped at the right size.** PyYAML, the Mermaid CLI, and a multi-module package split were all considered and rejected. At 138 documents and 1 author, the architecture must be proportional to the problem.

---

## Related

- [Architecture Discussion](../discussions/2026-09-26-validate-brain-refactor-architecture.md)
- [Daily Journal](../journal/2026-09-26.md)
