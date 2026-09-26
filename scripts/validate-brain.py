#!/usr/bin/env python3
"""
Brain Structural Validator
Run from the repository root: python scripts/validate-brain.py

Checks:
  1. No deprecated top-level directories remain.
  2. Required root files exist.
  3. Every .md document (outside exempt paths) has YAML frontmatter.
  4. Every frontmatter block has a valid `type` field.
  5. Every relative markdown link resolves to an existing file.
  6. All markdown code fences are balanced.
  7. Mermaid diagrams are structurally valid.
  8. Python code passes Ruff linting.
  9. Python code passes Pyright type checking.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
from typing import Literal, NamedTuple

ROOT = pathlib.Path(__file__).parent.parent.resolve()

# ── Configuration ──────────────────────────────────────────────────────────────

VALID_TYPES: frozenset[str] = frozenset({
    "knowledge", "project", "plan", "guide", "decision",
    "journal", "discussion", "experiment", "practice", "inbox", "reference",
    "agent", "debug",
})

DEPRECATED_DIRS: tuple[str, ...] = (
    "homelab", "journal", "learning", "docs",
    "knowledge/dsa", "knowledge/python", "knowledge/tools",
    "knowledge/devenv", "knowledge/skills",
)

REQUIRED_ROOT_FILES: tuple[str, ...] = ("README.md", "AGENTS.md", "LICENSE")

# Paths (or path substrings) excluded entirely from validation.
EXEMPT_PATTERNS: tuple[str, ...] = (
    ".obsidian",
    "inbox",
    "practice/LeetCode/Solutions",
    "scripts",
    ".git",
)

# Navigational/meta files exempt from frontmatter and link validation.
# They are still validated for code fences and Mermaid diagrams.
FRONTMATTER_EXEMPT_FILES: frozenset[pathlib.Path] = frozenset({
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "inbox" / "README.md",
    ROOT / "agents" / "README.md",
})

MERMAID_TYPES: frozenset[str] = frozenset({
    "flowchart", "graph", "sequencediagram", "erdiagram", "classdiagram",
    "statediagram", "gantt", "pie", "gitgraph", "mindmap", "timeline",
    "quadrantchart", "c4context", "zenuml", "sankey-beta", "kanban",
    "block-beta", "packet-beta", "architecture-beta",
})

# ── Types ──────────────────────────────────────────────────────────────────────

Severity = Literal["error", "warning"]


class Document(NamedTuple):
    path: pathlib.Path
    rel: pathlib.Path
    content: str
    validates_frontmatter: bool  # False for navigational/meta files


class Issue(NamedTuple):
    severity: Severity
    path: pathlib.Path | None
    line: int | None
    message: str


class CodeBlock(NamedTuple):
    language: str | None  # lowercased first word of the info string, or None
    content: str          # raw text between the fences (newlines preserved)
    start_line: int       # 1-indexed line of the opening fence
    end_line: int         # 1-indexed line of the closing fence


# ── Discovery ──────────────────────────────────────────────────────────────────

def discover_documents(root: pathlib.Path) -> list[Document]:
    """Return every Markdown file that requires validation.

    All inclusion/exclusion policy lives here. A Document that reaches a
    document validator is already known to be one that should be validated.
    """
    documents: list[Document] = []
    for path in root.rglob("*.md"):
        rel_str = str(path.relative_to(root))
        if any(pattern in rel_str for pattern in EXEMPT_PATTERNS):
            continue
        documents.append(Document(
            path=path,
            rel=path.relative_to(root),
            content=path.read_text(errors="replace"),
            validates_frontmatter=path not in FRONTMATTER_EXEMPT_FILES,
        ))
    return documents


# ── Shared Markdown scanner ────────────────────────────────────────────────────

def scan_code_blocks(content: str) -> tuple[list[CodeBlock], list[int]]:
    """Linearly scan Markdown content and extract fenced code blocks.

    Walks the document line-by-line, tracking fence state. Handles
    variable-width backtick sequences (3+): a 4-backtick outer fence is
    not prematurely closed by a 3-backtick inner fence, matching the
    CommonMark specification. Up to 3 leading spaces are permitted on
    fence lines.

    Returns:
        blocks   — one CodeBlock per fully matched opening/closing fence pair,
                   in document order.
        unclosed — 1-indexed start_line of every opening fence that reaches
                   end-of-file without a matching close.
    """
    blocks: list[CodeBlock] = []
    unclosed: list[int] = []
    lines = content.splitlines()

    i = 0
    while i < len(lines):
        open_m = re.match(r'^[ \t]{0,3}(`{3,})(.*)', lines[i])
        if open_m:
            ticks = open_m.group(1)           # "```" or "````", etc.
            info  = open_m.group(2).strip()   # info string (e.g. "mermaid")
            lang  = info.split()[0].lower() if info else None
            start = i + 1                     # 1-indexed line of the opener

            i += 1
            body: list[str] = []
            closed = False

            while i < len(lines):
                # A closing fence uses the same backtick char, has >= the
                # opener's length, and carries no info string.
                close_m = re.match(r'^[ \t]{0,3}(`+)\s*$', lines[i])
                if close_m and len(close_m.group(1)) >= len(ticks):
                    blocks.append(CodeBlock(
                        language=lang,
                        content="\n".join(body),
                        start_line=start,
                        end_line=i + 1,
                    ))
                    closed = True
                    i += 1
                    break
                body.append(lines[i])
                i += 1

            if not closed:
                unclosed.append(start)
        else:
            i += 1

    return blocks, unclosed


# ── Helpers ────────────────────────────────────────────────────────────────────

def _line_of(content: str, pos: int) -> int:
    """Return the 1-indexed line number of character position `pos` in `content`."""
    return content[:pos].count('\n') + 1


# ── Repository checks ──────────────────────────────────────────────────────────

def check_deprecated_dirs(root: pathlib.Path) -> list[Issue]:
    return [
        Issue("error", root / d, None, f"Deprecated directory still exists: {d}/")
        for d in DEPRECATED_DIRS
        if (root / d).exists()
    ]


def check_required_files(root: pathlib.Path) -> list[Issue]:
    return [
        Issue("error", root / f, None, f"Missing required root file: {f}")
        for f in REQUIRED_ROOT_FILES
        if not (root / f).exists()
    ]


# ── Document checks ────────────────────────────────────────────────────────────

def check_frontmatter(doc: Document) -> list[Issue]:
    if not doc.validates_frontmatter:
        return []

    content = doc.content

    if not content.startswith("---"):
        return [Issue("error", doc.rel, 1, "Missing frontmatter")]

    end = content.find("\n---", 3)
    if end == -1:
        return [Issue("error", doc.rel, 1, "Malformed frontmatter: no closing ---")]

    fm_block = content[3:end]
    type_match = re.search(r'^type:\s*(\S+)', fm_block, re.MULTILINE)
    if not type_match:
        return [Issue("error", doc.rel, 1, "Frontmatter missing 'type' field")]

    # Position of 'type:' in the original content is 3 (the opening ---) + match start.
    type_line = _line_of(content, 3 + type_match.start())
    doc_type = type_match.group(1)
    if doc_type not in VALID_TYPES:
        return [Issue("error", doc.rel, type_line, f"Invalid type '{doc_type}'")]

    return []


def check_links(doc: Document) -> list[Issue]:
    if not doc.validates_frontmatter:
        return []

    issues: list[Issue] = []
    for m in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', doc.content):
        target = m.group(2).split('#')[0].strip()
        if not target or target.startswith(('http', 'file:', 'mailto:')):
            continue
        resolved = (doc.path.parent / target).resolve()
        if not resolved.exists():
            issues.append(Issue(
                "error", doc.rel, _line_of(doc.content, m.start()),
                f"Broken relative link: {target}",
            ))
    return issues


def check_code_fences(doc: Document) -> list[Issue]:
    """Report each unclosed opening fence as a separate, precisely located issue.

    Uses scan_code_blocks() so that fence state is tracked linearly and
    inner fences inside outer blocks are never miscounted.
    """
    _, unclosed = scan_code_blocks(doc.content)
    return [
        Issue("error", doc.rel, line_no, "Unclosed code fence")
        for line_no in unclosed
    ]


def check_mermaid(doc: Document) -> list[Issue]:
    """Validate all Mermaid diagrams in the document.

    Uses scan_code_blocks() so that only genuine top-level ```mermaid blocks
    are validated — example mermaid blocks inside documentation fences
    (e.g. inside a ````markdown outer fence) are correctly ignored.
    """
    blocks, _ = scan_code_blocks(doc.content)
    issues: list[Issue] = []

    for block in blocks:
        if block.language != "mermaid":
            continue

        # Pair each raw line with its file-level line number.
        # block.start_line is the opening ```mermaid fence;
        # the first body line is always at block.start_line + 1.
        raw_lines = block.content.splitlines()
        numbered: list[tuple[int, str]] = [
            (block.start_line + 1 + i, raw_line.strip())
            for i, raw_line in enumerate(raw_lines)
            if raw_line.strip() and not raw_line.strip().startswith("%%")
        ]

        if not numbered:
            issues.append(Issue("error", doc.rel, block.start_line + 1, "Empty Mermaid diagram block"))
            continue

        first_line_no, first_line = numbered[0]
        header = first_line.split()[0].lower()

        if header not in MERMAID_TYPES:
            issues.append(Issue(
                "error", doc.rel, first_line_no,
                f"Unknown Mermaid diagram type: '{header}'",
            ))
            continue

        content_lines = [line for _, line in numbered]

        # Structural balance checks — anchored to the diagram header line.
        if header in ("flowchart", "graph"):
            subgraphs = sum(1 for line in content_lines if line.startswith("subgraph"))
            ends = sum(1 for line in content_lines if line == "end" or line.startswith("end "))
            if subgraphs != ends:
                issues.append(Issue(
                    "error", doc.rel, first_line_no,
                    f"Unbalanced subgraph: {subgraphs} subgraph vs {ends} end",
                ))
        elif header == "sequencediagram":
            block_openers = sum(
                1 for line in content_lines
                if re.match(r'^(alt|opt|loop|par|critical|break|rect)\b', line)
            )
            ends = sum(1 for line in content_lines if re.match(r'^end\b', line))
            if block_openers != ends:
                issues.append(Issue(
                    "error", doc.rel, first_line_no,
                    f"Unbalanced sequenceDiagram blocks: {block_openers} openers vs {ends} end",
                ))

        # Edge-label syntax check — each issue anchored to its exact line.
        for line_no, line in numbered:
            for label_match in re.finditer(r'[-.=~<>]*\|([^|]+)\|', line):
                label = label_match.group(1).strip()
                if (
                    any(ch in label for ch in ('*', '/', '(', ')', '[', ']', '{', '}'))
                    and not (label.startswith('"') and label.endswith('"'))
                ):
                    issues.append(Issue(
                        "error", doc.rel, line_no,
                        f"Unquoted special character in edge label '|{label}|' — wrap in \"...\"",
                    ))

    return issues


# ── External checks ────────────────────────────────────────────────────────────

def run_ruff(root: pathlib.Path) -> list[Issue]:
    if not shutil.which("ruff"):
        print("  ℹ Ruff not in PATH — Python lint check skipped.")
        return []
    res = subprocess.run(["ruff", "check", str(root)], capture_output=True, text=True, check=False)
    if res.returncode != 0:
        return [Issue("error", None, None, f"Ruff linting failed:\n{res.stdout.strip()}")]
    return []


def run_pyright(root: pathlib.Path) -> list[Issue]:
    if not shutil.which("pyright"):
        print("  ℹ Pyright not in PATH — type check skipped.")
        return []
    res = subprocess.run(
        ["pyright", str(root / "scripts"), str(root / "practice")],
        capture_output=True, text=True, check=False,
    )
    if res.returncode != 0:
        return [Issue("error", None, None, f"Pyright type checks failed:\n{res.stdout.strip()}")]
    return []


# ── Reporting ──────────────────────────────────────────────────────────────────

def _location(issue: Issue) -> str:
    """Format a path:line location prefix for an issue."""
    if issue.path is None:
        return ""
    loc = str(issue.path)
    if issue.line is not None:
        loc = f"{loc}:{issue.line}"
    return loc


def report(issues: list[Issue]) -> None:
    """Render collected issues to stdout.

    The renderer is separated from validation logic so the output format
    can evolve (e.g. --format json) without touching any check function.
    """
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):\n")
        for issue in warnings:
            loc = _location(issue)
            print(f"  ⚠ {loc + '  ' if loc else ''}{issue.message}")

    if errors:
        print(f"\n❌ Validation failed — {len(errors)} error(s):\n")
        for issue in errors:
            loc = _location(issue)
            print(f"  ✗ {loc + '  ' if loc else ''}{issue.message}")
    else:
        print("\n✅ All checks passed. Brain structure is valid.")


# ── Runner ─────────────────────────────────────────────────────────────────────

def main() -> int:
    issues: list[Issue] = []

    # ── Repository-level checks ────────────────────────────────────────────────
    print("Checking repository structure...")
    issues.extend(check_deprecated_dirs(ROOT))
    issues.extend(check_required_files(ROOT))

    # ── Document checks (single-pass discovery) ────────────────────────────────
    print("Processing markdown files...")
    documents = discover_documents(ROOT)

    document_checks = (
        check_frontmatter,
        check_links,
        check_code_fences,
        check_mermaid,
    )
    for doc in documents:
        for check in document_checks:
            issues.extend(check(doc))

    # ── External tooling checks ────────────────────────────────────────────────
    print("Running Python quality checks...")
    issues.extend(run_ruff(ROOT))
    issues.extend(run_pyright(ROOT))

    report(issues)
    return 1 if any(i.severity == "error" for i in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
