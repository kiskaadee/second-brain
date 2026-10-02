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
    "journal", "discussion", "experiment", "practice", "reference",
    "agent", "debug",
})

REQUIRED_ROOT_FILES: tuple[str, ...] = ("README.md", "AGENTS.md", "LICENSE")

# Deprecated paths are exact repository-relative paths, NEVER substring greps
DEPRECATED_ROOT_DIRS: frozenset[str] = frozenset({
    "homelab", "journal", "learning", "docs", "practice",
    "projects", "records", "agents", "knowledge", "inbox",
})

DEPRECATED_NESTED_PATHS: frozenset[str] = frozenset({
    "knowledge/dsa", "knowledge/python", "knowledge/tools",
    "knowledge/devenv", "knowledge/skills", "projects/homelab/archive",
    "records/discussions",
})

# Paths (or path substrings) excluded entirely from validation.
EXEMPT_PATTERNS: tuple[str, ...] = (
    ".obsidian",
    ".trash",
    "00-inbox",
    "inbox",
    "04-learning/practice/LeetCode/Solutions",
    "practice/LeetCode/Solutions",
    "scripts",
    ".git",
    ".agents",  # graphify runtime files; not vault documents
)

# Navigational/meta files exempt from frontmatter and link validation.
# They are still validated for code fences and Mermaid diagrams.
FRONTMATTER_EXEMPT_FILES: frozenset[pathlib.Path] = frozenset({
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "00-inbox" / "README.md",
    ROOT / "inbox" / "README.md",
    ROOT / "05-agents" / "README.md",
    ROOT / "agents" / "README.md",
})

MERMAID_TYPES: frozenset[str] = frozenset({
    "flowchart", "graph", "sequencediagram", "erdiagram", "classdiagram",
    "statediagram", "gantt", "pie", "gitgraph", "mindmap", "timeline",
    "quadrantchart", "c4context", "zenuml", "sankey-beta", "kanban",
    "block-beta", "packet-beta", "architecture-beta",
})

# ── Types & Contracts ─────────────────────────────────────────────────────────

Severity = Literal["error", "warning"]


class DirectoryContract(NamedTuple):
    prefix: str
    expected_type: str | None
    max_depth: int | None = None
    require_filename: str | None = None
    filename_regex: re.Pattern[str] | None = None
    allow_unclassified: bool = False


DIRECTORY_CONTRACTS: tuple[DirectoryContract, ...] = (
    # 00-inbox: Staging zone, completely exempt from frontmatter validation
    DirectoryContract(prefix="00-inbox", expected_type=None, allow_unclassified=True),

    # 01-plans: Intent (allows max_depth=3 for project subsystems e.g. homelab/appctl/*.md)
    DirectoryContract(prefix="01-plans", expected_type="plan", max_depth=3),

    # 02-discussions: Prospective option explorations (max_depth=2: project/*.md)
    DirectoryContract(prefix="02-discussions", expected_type="discussion", max_depth=2),

    # 03-records: Historical Memory
    DirectoryContract(
        prefix="03-records/journal",
        expected_type="journal",
        max_depth=2,
        filename_regex=re.compile(r"^\d{4}-\d{2}-\d{2}\.md$"),
    ),
    DirectoryContract(prefix="03-records/debug", expected_type="debug", max_depth=2),
    DirectoryContract(prefix="03-records/decisions", expected_type="decision", max_depth=2),

    # 04-learning: Durable understanding & practice
    DirectoryContract(prefix="04-learning/knowledge", expected_type="knowledge"),
    DirectoryContract(prefix="04-learning/guides", expected_type="guide", max_depth=3),
    DirectoryContract(prefix="04-learning/practice", expected_type="practice"),

    # 05-agents: Agent persona profiles & reusable skills
    DirectoryContract(prefix="05-agents/profiles", expected_type="agent", max_depth=2),
    DirectoryContract(prefix="05-agents/skills", expected_type="agent", max_depth=4),

    # 06-projects: System topology hubs strictly at depth 2 named README.md
    DirectoryContract(
        prefix="06-projects",
        expected_type="project",
        max_depth=2,
        require_filename="README.md",
    ),
)


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


def _is_skill_package_internal(rel: pathlib.Path) -> bool:
    """Return True if rel is an internal artifact of a skill package (SKILL.md, references/, scripts/)."""
    rel_str = str(rel)
    if not rel_str.startswith(("05-agents/skills/", "agents/skills/")):
        return False
    if rel.name == "SKILL.md":
        return True
    return any(p in ("references", "scripts") for p in rel.parts)


# ── Repository checks ──────────────────────────────────────────────────────────

def check_deprecated_dirs(root: pathlib.Path) -> list[Issue]:
    issues: list[Issue] = []
    for d in sorted(DEPRECATED_ROOT_DIRS):
        target = root / d
        if target.is_dir() and not target.is_symlink():
            issues.append(Issue("error", target, None, f"Deprecated root directory still exists: {d}/"))
    for p in sorted(DEPRECATED_NESTED_PATHS):
        target = root / p
        if target.exists():
            issues.append(Issue("error", target, None, f"Deprecated nested path still exists: {p}"))
    return issues


def check_required_files(root: pathlib.Path) -> list[Issue]:
    return [
        Issue("error", root / f, None, f"Missing required root file: {f}")
        for f in REQUIRED_ROOT_FILES
        if not (root / f).exists()
    ]


# ── Document checks ────────────────────────────────────────────────────────────

def check_directory_contracts(doc: Document) -> list[Issue]:
    if not doc.validates_frontmatter:
        return []

    rel_str = str(doc.rel)
    matched_contract: DirectoryContract | None = None
    for contract in DIRECTORY_CONTRACTS:
        if rel_str.startswith(contract.prefix + "/") or rel_str == contract.prefix:
            matched_contract = contract
            break

    if matched_contract is None:
        return [Issue("error", doc.rel, 1, f"Document outside target taxonomy: {doc.rel}")]

    if matched_contract.allow_unclassified:
        return []

    issues: list[Issue] = []

    # Check filename requirement
    if matched_contract.require_filename and doc.path.name != matched_contract.require_filename:
        issues.append(Issue(
            "error", doc.rel, 1,
            f"Structural violation: {doc.rel} must be named '{matched_contract.require_filename}'",
        ))

    # Check filename regex
    if matched_contract.filename_regex and not matched_contract.filename_regex.match(doc.path.name):
        issues.append(Issue(
            "error", doc.rel, 1,
            f"Structural violation: {doc.rel} does not match required pattern '{matched_contract.filename_regex.pattern}'",
        ))

    # Check max depth relative to contract prefix
    if matched_contract.max_depth is not None:
        sub_path = rel_str[len(matched_contract.prefix):].strip("/")
        depth = len([p for p in sub_path.split("/") if p])
        if depth > matched_contract.max_depth:
            issues.append(Issue(
                "error", doc.rel, 1,
                f"Nesting violation: {doc.rel} exceeds max depth {matched_contract.max_depth} for {matched_contract.prefix}",
            ))

    # Check frontmatter type against expected_type
    content = doc.content
    doc_type = None
    type_line = 1
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm_block = content[3:end]
            type_match = re.search(r'^type:\s*(\S+)', fm_block, re.MULTILINE)
            if type_match:
                doc_type = type_match.group(1)
                type_line = _line_of(content, 3 + type_match.start())

    if (
        matched_contract.expected_type is not None
        and doc_type != matched_contract.expected_type
        and not _is_skill_package_internal(doc.rel)
    ):
        issues.append(Issue(
            "error", doc.rel, type_line,
            f"Directory/type contract violation: {doc.rel} has type '{doc_type}', expected '{matched_contract.expected_type}'",
        ))

    return issues

def check_frontmatter(doc: Document) -> list[Issue]:
    if not doc.validates_frontmatter:
        return []

    # Skill package internals:
    # SKILL.md is the agent runtime specification and must have name and description.
    # Subordinate directories (references/, scripts/) are exempt from vault frontmatter.
    if _is_skill_package_internal(doc.rel):
        if doc.path.name == "SKILL.md":
            content = doc.content
            if not content.startswith("---"):
                return [Issue("error", doc.rel, 1, "Missing frontmatter in SKILL.md")]
            end = content.find("\n---", 3)
            if end == -1:
                return [Issue("error", doc.rel, 1, "Malformed frontmatter in SKILL.md: no closing ---")]
            fm_block = content[3:end]
            if not re.search(r'^name:\s*\S+', fm_block, re.MULTILINE):
                return [Issue("error", doc.rel, 1, "Frontmatter missing 'name' field in SKILL.md")]
            if not re.search(r'^description:', fm_block, re.MULTILINE):
                return [Issue("error", doc.rel, 1, "Frontmatter missing 'description' field in SKILL.md")]
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
    blocks, _ = scan_code_blocks(doc.content)
    code_spans = [(b.start_line, b.end_line) for b in blocks]

    for m in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', doc.content):
        line_no = _line_of(doc.content, m.start())
        if any(start <= line_no <= end for start, end in code_spans):
            continue
        target = m.group(2).split('#')[0].strip()
        if not target or target.startswith(('http', 'file:', 'mailto:')):
            continue
        resolved = (doc.path.parent / target).resolve()
        if not resolved.exists():
            issues.append(Issue(
                "error", doc.rel, line_no,
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
    practice_dir = root / "04-learning" / "practice"
    if not practice_dir.exists():
        practice_dir = root / "practice"
    res = subprocess.run(
        ["pyright", str(root / "scripts"), str(practice_dir)],
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
        check_directory_contracts,
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
