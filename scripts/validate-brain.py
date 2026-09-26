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
    line: int | None  # reserved for Phase 2 — always None in Phase 1
    message: str


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
        return [Issue("error", doc.rel, None, f"Missing frontmatter: {doc.rel}")]

    end = content.find("\n---", 3)
    if end == -1:
        return [Issue("error", doc.rel, None, f"Malformed frontmatter (no closing ---): {doc.rel}")]

    fm_block = content[3:end]
    type_match = re.search(r'^type:\s*(\S+)', fm_block, re.MULTILINE)
    if not type_match:
        return [Issue("error", doc.rel, None, f"Frontmatter missing 'type' field: {doc.rel}")]

    doc_type = type_match.group(1)
    if doc_type not in VALID_TYPES:
        return [Issue("error", doc.rel, None, f"Invalid type '{doc_type}': {doc.rel}")]

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
            issues.append(Issue("error", doc.rel, None, f"Broken link in {doc.rel}: {target}"))
    return issues


def check_code_fences(doc: Document) -> list[Issue]:
    fences = [line for line in doc.content.splitlines() if line.strip().startswith("```")]
    if len(fences) % 2 != 0:
        return [Issue(
            "error", doc.rel, None,
            f"Unclosed code fence in {doc.rel} (found {len(fences)} fence delimiters)",
        )]
    return []


def check_mermaid(doc: Document) -> list[Issue]:
    issues: list[Issue] = []
    for m in re.finditer(r'```mermaid\s*\n(.*?)\n```', doc.content, re.DOTALL):
        block = m.group(1).strip()
        if not block:
            issues.append(Issue("error", doc.rel, None, f"Empty Mermaid diagram block in {doc.rel}"))
            continue

        lines = [
            line.strip() for line in block.splitlines()
            if line.strip() and not line.strip().startswith("%%")
        ]
        if not lines:
            continue

        header = lines[0].split()[0].lower()
        if header not in MERMAID_TYPES:
            issues.append(Issue(
                "error", doc.rel, None,
                f"Invalid Mermaid diagram type '{header}' in {doc.rel}",
            ))
            continue

        if header in ("flowchart", "graph"):
            subgraphs = sum(1 for line in lines if line.startswith("subgraph"))
            ends = sum(1 for line in lines if line == "end" or line.startswith("end "))
            if subgraphs != ends:
                issues.append(Issue(
                    "error", doc.rel, None,
                    f"Unbalanced subgraph in Mermaid diagram in {doc.rel} "
                    f"({subgraphs} subgraph vs {ends} end)",
                ))
        elif header == "sequencediagram":
            block_openers = sum(
                1 for line in lines
                if re.match(r'^(alt|opt|loop|par|critical|break|rect)\b', line)
            )
            ends = sum(1 for line in lines if re.match(r'^end\b', line))
            if block_openers != ends:
                issues.append(Issue(
                    "error", doc.rel, None,
                    f"Unbalanced control blocks in Mermaid sequenceDiagram in {doc.rel} "
                    f"({block_openers} block openers vs {ends} end)",
                ))

        for line in lines:
            for label_match in re.finditer(r'[-.=~<>]*\|([^|]+)\|', line):
                label = label_match.group(1).strip()
                if (
                    any(ch in label for ch in ('*', '/', '(', ')', '[', ']', '{', '}'))
                    and not (label.startswith('"') and label.endswith('"'))
                ):
                    issues.append(Issue(
                        "error", doc.rel, None,
                        f"Unquoted special character in Mermaid edge label "
                        f"'|{label}|' in {doc.rel} (wrap in \"...\")",
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

def report(issues: list[Issue]) -> None:
    """Render collected issues to stdout.

    The renderer is deliberately separated from the checks so that the output
    format can evolve (e.g. --format json) without touching validation logic.
    """
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):\n")
        for issue in warnings:
            print(f"  ⚠ {issue.message}")

    if errors:
        print(f"\n❌ Validation failed — {len(errors)} error(s):\n")
        for issue in errors:
            print(f"  ✗ {issue.message}")
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
