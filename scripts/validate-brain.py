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
"""

import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent.parent.resolve()

VALID_TYPES = {
    "knowledge", "project", "plan", "guide", "decision",
    "journal", "discussion", "experiment", "practice", "inbox", "reference",
}

DEPRECATED_DIRS = [
    "homelab", "journal", "learning", "docs",
    "knowledge/dsa", "knowledge/python", "knowledge/tools",
    "knowledge/devenv", "knowledge/skills",
]

REQUIRED_ROOT_FILES = ["README.md", "AGENTS.md", "LICENSE"]

EXEMPT_PATTERNS = [
    ".obsidian",
    "inbox",
    "practice/LeetCode/Solutions",
    "scripts",
    ".git",
]

# Root-level files that are navigational/meta and intentionally have no frontmatter
FRONTMATTER_EXEMPT_FILES = {
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "inbox" / "README.md",
}

errors: list[str] = []
warnings: list[str] = []


def is_exempt(path: pathlib.Path) -> bool:
    rel = str(path.relative_to(ROOT))
    return any(ex in rel for ex in EXEMPT_PATTERNS)


# ── Check 1: No deprecated directories ────────────────────────────────────────
print("Checking deprecated directories...")
for d in DEPRECATED_DIRS:
    target = ROOT / d
    if target.exists():
        errors.append(f"Deprecated directory still exists: {d}/")
print(f"  {'✓' if not any('Deprecated' in e for e in errors) else '✗'} Done.\n")


# ── Check 2: Required root files ──────────────────────────────────────────────
print("Checking required root files...")
for f in REQUIRED_ROOT_FILES:
    if not (ROOT / f).exists():
        errors.append(f"Missing required root file: {f}")
print(f"  {'✓' if not any('Missing required' in e for e in errors) else '✗'} Done.\n")


# ── Check 3 & 4: Frontmatter presence and valid type ─────────────────────────
print("Checking frontmatter...")
fm_errors = 0
for md in ROOT.rglob("*.md"):
    if is_exempt(md):
        continue
    if md in FRONTMATTER_EXEMPT_FILES:
        continue
    content = md.read_text(errors="replace")
    rel = md.relative_to(ROOT)
    if not content.startswith("---"):
        errors.append(f"Missing frontmatter: {rel}")
        fm_errors += 1
        continue
    # Extract frontmatter block
    end = content.find("\n---", 3)
    if end == -1:
        errors.append(f"Malformed frontmatter (no closing ---): {rel}")
        fm_errors += 1
        continue
    fm_block = content[3:end]
    type_match = re.search(r'^type:\s*(\S+)', fm_block, re.MULTILINE)
    if not type_match:
        errors.append(f"Frontmatter missing 'type' field: {rel}")
        fm_errors += 1
    elif type_match.group(1) not in VALID_TYPES:
        errors.append(f"Invalid type '{type_match.group(1)}': {rel}")
        fm_errors += 1
print(f"  {'✓' if fm_errors == 0 else '✗'} Done ({fm_errors} issues).\n")


# ── Check 5: Relative link resolution ─────────────────────────────────────────
print("Checking relative links...")
link_errors = 0
for md in ROOT.rglob("*.md"):
    if is_exempt(md):
        continue
    if md in FRONTMATTER_EXEMPT_FILES:
        continue
    content = md.read_text(errors="replace")
    for m in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', content):
        target = m.group(2).split('#')[0].strip()
        if not target or target.startswith(('http', 'file:', 'mailto:')):
            continue
        resolved = (md.parent / target).resolve()
        if not resolved.exists():
            rel = md.relative_to(ROOT)
            errors.append(f"Broken link in {rel}: {target}")
            link_errors += 1
print(f"  {'✓' if link_errors == 0 else '✗'} Done ({link_errors} broken links).\n")


# ── Check 6: Code fence balance ───────────────────────────────────────────────
print("Checking markdown code fences...")
fence_errors = 0
for md in ROOT.rglob("*.md"):
    if is_exempt(md):
        continue
    content = md.read_text(errors="replace")
    rel = md.relative_to(ROOT)
    fences = [line for line in content.splitlines() if line.strip().startswith("```")]
    if len(fences) % 2 != 0:
        errors.append(f"Unclosed code fence in {rel} (found {len(fences)} fence delimiters)")
        fence_errors += 1
print(f"  {'✓' if fence_errors == 0 else '✗'} Done ({fence_errors} issues).\n")


# ── Check 7: Mermaid diagram validation ───────────────────────────────────────
print("Checking Mermaid diagrams...")
mermaid_errors = 0
MERMAID_TYPES = {
    "flowchart", "graph", "sequencediagram", "erdiagram", "classdiagram",
    "statediagram", "gantt", "pie", "gitgraph", "mindmap", "timeline",
    "quadrantchart", "c4context", "zenuml", "sankey-beta", "kanban",
    "block-beta", "packet-beta", "architecture-beta"
}

for md in ROOT.rglob("*.md"):
    if is_exempt(md):
        continue
    content = md.read_text(errors="replace")
    rel = md.relative_to(ROOT)

    # Find all ```mermaid ... ``` blocks
    for m in re.finditer(r'```mermaid\s*\n(.*?)\n```', content, re.DOTALL):
        block = m.group(1).strip()
        if not block:
            errors.append(f"Empty Mermaid diagram block in {rel}")
            mermaid_errors += 1
            continue

        lines = [line.strip() for line in block.splitlines() if line.strip() and not line.strip().startswith("%%")]
        if not lines:
            continue

        # Check valid diagram header
        header = lines[0].split()[0].lower()
        if header not in MERMAID_TYPES:
            errors.append(f"Invalid Mermaid diagram type '{header}' in {rel}")
            mermaid_errors += 1
            continue

        # Check subgraph / block balance depending on diagram type
        if header in ["flowchart", "graph"]:
            subgraphs = sum(1 for line in lines if line.startswith("subgraph"))
            ends = sum(1 for line in lines if line == "end" or line.startswith("end "))
            if subgraphs != ends:
                errors.append(f"Unbalanced subgraph in Mermaid diagram in {rel} ({subgraphs} subgraph vs {ends} end)")
                mermaid_errors += 1
        elif header == "sequencediagram":
            block_openers = sum(1 for line in lines if re.match(r'^(alt|opt|loop|par|critical|break|rect)\b', line))
            ends = sum(1 for line in lines if re.match(r'^end\b', line))
            if block_openers != ends:
                errors.append(f"Unbalanced control blocks in Mermaid sequenceDiagram in {rel} ({block_openers} block openers vs {ends} end)")
                mermaid_errors += 1

        # Check for unquoted special characters in transition labels: e.g. -->|label|
        for line in lines:
            for label_match in re.finditer(r'-->\|([^|]+)\|', line):
                label = label_match.group(1).strip()
                # If label contains special characters like *, /, or unescaped parens but isn't quoted
                if any(ch in label for ch in ['*', '/']) and not (label.startswith('"') and label.endswith('"')):
                    errors.append(f"Unquoted special character in Mermaid edge label '|{label}|' in {rel} (wrap in \"...\")")
                    mermaid_errors += 1

print(f"  {'✓' if mermaid_errors == 0 else '✗'} Done ({mermaid_errors} issues).\n")


# ── Check 8: Python Linting (Ruff) ────────────────────────────────────────────
print("Checking Python code quality (Ruff)...")
if shutil.which("ruff"):
    res = subprocess.run(["ruff", "check", str(ROOT)], capture_output=True, text=True, check=False)
    if res.returncode != 0:
        errors.append(f"Ruff linting failed:\n{res.stdout.strip()}")
        print("  ✗ Done (Ruff errors found).\n")
    else:
        print("  ✓ Done (0 lint issues).\n")
else:
    print("  ℹ Skipped (ruff not in PATH).\n")


# ── Check 9: Python Type Checking (Pyright) ───────────────────────────────────
print("Checking Python type consistency (Pyright)...")
if shutil.which("pyright"):
    res = subprocess.run(["pyright", str(ROOT / "scripts"), str(ROOT / "practice")], capture_output=True, text=True, check=False)
    if res.returncode != 0:
        errors.append(f"Pyright type checks failed:\n{res.stdout.strip()}")
        print("  ✗ Done (Pyright errors found).\n")
    else:
        print("  ✓ Done (0 type errors).\n")
else:
    print("  ℹ Skipped (pyright not in PATH).\n")


# ── Summary ───────────────────────────────────────────────────────────────────
if errors:
    print(f"❌ Validation failed — {len(errors)} error(s):\n")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print("✅ All checks passed. Brain structure is valid.")


