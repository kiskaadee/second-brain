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

import re
import sys
import pathlib

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
        if not target or target.startswith('http') or target.startswith('file:') or target.startswith('mailto:'):
            continue
        resolved = (md.parent / target).resolve()
        if not resolved.exists():
            rel = md.relative_to(ROOT)
            errors.append(f"Broken link in {rel}: {target}")
            link_errors += 1
print(f"  {'✓' if link_errors == 0 else '✗'} Done ({link_errors} broken links).\n")


# ── Summary ───────────────────────────────────────────────────────────────────
if errors:
    print(f"❌ Validation failed — {len(errors)} error(s):\n")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print("✅ All checks passed. Brain structure is valid.")
