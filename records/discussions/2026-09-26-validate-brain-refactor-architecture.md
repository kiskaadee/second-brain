---
type: discussion
date: 2026-09-26
tags: [brain, tooling, validation, architecture, python]
---

# Architectural Discussion: validate-brain.py Three-Phase Refactor

## Problem Statement

`scripts/validate-brain.py` grew organically. Each check was added in isolation, which kept individual additions small, but the accumulated design had several structural liabilities by the time the script was operating over 138 documents.

**Global mutable state.** `error_count` was a module-level integer incremented by side effects distributed across every check function. No function returned a value indicating what it found; the only observable output was the running count and printed strings. This made it impossible to test any individual check in isolation or compose checks without also running all of them.

**Four independent traversals.** The script called `rglob("*.md")` four separate times — once each for frontmatter checks, type-field checks, link checks, and code fence checks. Each traversal read the file from disk. For 138 files this was not a performance problem, but it was a correctness and maintainability problem: the set of files visited by each check was not guaranteed to be identical (if a file appeared between traversals, it would be seen by some checks and not others), and adding a new check required either a fifth traversal or threading new logic into one of the existing four in a way that was non-obvious.

**Error reporting by string inspection.** Callers determined whether a check had found anything by examining whether certain strings had been printed. There was no structured return value to aggregate, filter, or categorize.

**Two independent Markdown fence parsers.** A fence counter (tracking triple-backtick depth) and a `re.DOTALL` regex operating on the full file string both existed and were applied to different checks. They could disagree on the same file because they did not share state or a common model of the document. A file with an unclosed fence would confuse each of them differently.

**The missed Mermaid bug.** These structural problems had a concrete consequence: a check for Mermaid edge labels only matched lines containing `-->` and failed to check for parentheses in node labels. The Mermaid renderer rejects parentheses in node labels that are not quoted. The check passed on files that would fail at render time. The bug was not found by the test regime because there was no structured representation of what the parser had actually visited — the check was a line-level grep with no understanding of whether it was inside a code block of type `mermaid` or inside a generic code block or outside any block at all.

---

## Context and Analysis

### Two Feedback Sources

Two distinct sets of feedback were received. They agreed on the diagnosis but diverged sharply on prescription.

**The functional refactor proposal** identified the correct minimal changes: replace global state with functions that return lists, eliminate repeated traversals with a single-pass discovery step, introduce a `main()` entry point, and make the check registry explicit. It did not propose adding dependencies, splitting into multiple modules, or introducing configuration objects. The scope matched the actual complexity of the problem: a single-author script over a corpus of 138 documents, with a zero-dependency constraint.

What this proposal got right: it identified the smallest set of structural changes that would remove the liabilities. What it did not address: it left the two Markdown parsers intact and did not propose a unified model of document structure at the code-block level.

**The full architectural redesign proposal** went further. It proposed: PyYAML for frontmatter parsing (replacing ad-hoc regex), a Mermaid CLI integration for diagram validation (replacing heuristic label checks), a `ValidationConfig` dataclass for rule parameterization, and a multi-module package split (`validator/core.py`, `validator/checks/`, `validator/reporters/`). It identified the correct long-term direction for a team-owned, dependency-tolerant validation library.

What this proposal got right: the `Document` NamedTuple with a `validates_frontmatter` field, and the scan_code_blocks() linear scanner as the single shared parser for code fences. Both of these were adopted. What it over-prescribed: the external dependencies and module split impose a maintenance surface that is not justified by the corpus size or authorship model. A validator for 138 documents maintained by one author should not require a Node.js Mermaid CLI binary in the environment to run `git commit`.

### The Stopping-Point Decision

The team drew the scope boundary at: zero new external dependencies, single-file script, no configuration dataclass.

The rationale is not that PyYAML or a multi-module design is wrong — it is that those choices carry costs that are not yet justified. PyYAML as a dependency means the script can fail to run in a fresh environment where the package is absent. The current regex-based frontmatter extraction is brittle for complex YAML, but the Brain's frontmatter is structurally simple and consistent enough that the regex surface area is bounded. The cost of a parsing error from ad-hoc regex is a false negative (a file passes that should not). The cost of a missing dependency is that the entire validator is unavailable. For a pre-commit gate, the latter failure mode is worse.

The Mermaid CLI integration was rejected for the same reason: it introduces a runtime dependency on a Node.js binary and requires the binary's version to match the renderer's version. The heuristic label check, corrected to handle parentheses, is sufficient for the actual error class that was being missed. A false positive from the heuristic (flagging a valid diagram) is recoverable; a broken pre-commit hook is not.

The multi-module split was rejected because it complicates deployment (the script is currently copied or symlinked as a single file) and provides no benefit for a single-author codebase where the module boundaries would not be maintained across contributors.

---

## Options Evaluation

| Decision Point | Option A (Adopted) | Option B (Rejected) |
|---|---|---|
| Frontmatter parsing | Regex extraction (existing approach, bounded surface) | PyYAML (correct, but adds external dependency) |
| Mermaid validation | Heuristic label check with parenthesis correction | Mermaid CLI subprocess (correct, but Node.js runtime dependency) |
| Code fence parsing | `scan_code_blocks()` linear scanner (single shared parser) | Retain both fence counter + DOTALL regex (two parsers, can disagree) |
| Script structure | Single file, `main()`, explicit check registry | Multi-module package with `ValidationConfig` dataclass |
| Phase sequencing | Three explicit phases with different behavioral contracts | Single large refactor (harder to attribute regressions) |

---

## Consensus and Resolution

### Phase Sequencing Rationale

The refactor was divided into three phases with different behavioral contracts. This separation is load-bearing for reasoning about regressions.

**Phase 1** introduces structural changes only: `Document` and `Issue` NamedTuples, single-pass discovery, functions returning `list[Issue]`, `main()`, explicit check registry. The behavioral contract of Phase 1 is that every error previously detected is still detected, at the same location, with the same message, and no new errors are introduced. If Phase 1 causes a previously-passing file to fail, that is a regression. This constraint allows Phase 1 to be reviewed purely as a refactor without needing to evaluate whether any new validation logic is correct.

**Phase 2** adds line numbers to all diagnostics via a `_line_of()` helper. This explicitly changes diagnostic output — the same error now includes a line number it did not include before. This is not a behavioral regression, but it is a visible change to the output format. Separating it from Phase 1 means that any output diff between Phase 1 and Phase 2 can be attributed entirely to the addition of line numbers, not to structural changes.

**Phase 3** replaces both the fence counter and the DOTALL regex with `scan_code_blocks()`. This explicitly changes parsing behavior. Files with ambiguous fence structures may be classified differently. Any new errors surfaced by Phase 3 are genuine new detections, not regressions from Phase 1 or Phase 2. Separating Phase 3 makes that attribution clear.

The sequencing is designed so that each phase boundary is a stable checkpoint: if the post-Phase-3 state surfaces a false positive, the team can bisect to the phase that introduced it without re-examining the entire change.

### `scan_code_blocks()` Design

The linear scanner walks the file line by line. It tracks whether the current line opens a code fence (a line matching the pattern of three or more backticks, optionally followed by a language tag), accumulates lines inside the fence, and emits a `CodeBlock` (offset, language, content) when the matching closing fence is found.

A linear walker is preferable to a DOTALL regex for two reasons.

First, the CommonMark spec permits variable-width backtick fences: a fence opened with four backticks closes only on a line containing four or more backticks, not on a line containing three. A DOTALL regex of the form `` ` ``{3}.*?`` ` ``{3} will misparse nested or variable-width fences because the lazy quantifier does not track backtick count. The linear scanner tracks the opening fence width and requires the closing line to match or exceed it, which is the correct CommonMark rule.

Second, a DOTALL regex applied to the full file string produces a match object with a start and end offset. Translating that offset to a line number requires a second pass over the file to count newlines, or a precomputed offset-to-line index. The linear scanner knows the current line number at each point without additional bookkeeping.

The cost of the linear scanner is that it is more code than a regex. For a validator script where correctness of the parser matters (the Mermaid bug was directly caused by the parser not knowing what kind of block it was in), that cost is acceptable.

### `Document.validates_frontmatter` Field

The `Document` NamedTuple carries a `validates_frontmatter: bool` field populated at discovery time. Files in `inbox/` are exempt from frontmatter enforcement; all other committed documents are not.

The alternative would be to let each frontmatter validator check the file path itself and skip `inbox/` files inline. This was rejected for two reasons. First, it duplicates the exemption logic across every check that touches frontmatter — if the exemption rule changes (for example, if a new staging directory is added), every check must be updated. Second, it means a check function must inspect the path of the document it is checking, which is knowledge that belongs to discovery, not to validation. The `validates_frontmatter` field moves the policy decision to the single place where it can be maintained: the `discover_documents()` function. Check functions receive a `Document` and operate on its fields without needing to reason about path semantics.

The tradeoff is that `Document` now carries a field that is not derived from the file's content but from its location. This is a mild violation of the principle that a document object represents only what is in the file. It is justified because the exemption is a property of the document's role in the repository, which is determined by its location, and that property is relevant to multiple downstream checks.
