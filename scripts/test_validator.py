#!/usr/bin/env python3
"""
Unit tests for validate-brain.py DirectoryContract and invariants.
Run: python3 scripts/test_validator.py
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).parent.parent.resolve()

from typing import Any

spec = importlib.util.spec_from_file_location("validate_brain", ROOT / "scripts" / "validate-brain.py")
if spec is None or spec.loader is None:
    raise ImportError("Could not load validate-brain.py")
vb = importlib.util.module_from_spec(spec)
sys.modules["validate_brain"] = vb
spec.loader.exec_module(vb)


class TestDirectoryContracts(unittest.TestCase):
    def make_doc(self, rel_path: str, content: str, validates_frontmatter: bool = True) -> Any:
        p = ROOT / rel_path
        return vb.Document(
            path=p,
            rel=pathlib.Path(rel_path),
            content=content,
            validates_frontmatter=validates_frontmatter,
        )

    def test_plans_valid(self) -> None:
        doc = self.make_doc(
            "01-plans/homelab/appctl/smart-deploy.md",
            "---\ntype: plan\nstatus: active\n---\n# Plan",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertEqual(len(issues), 0)

    def test_plans_type_mismatch(self) -> None:
        doc = self.make_doc(
            "01-plans/homelab/knowledge-note.md",
            "---\ntype: knowledge\nstatus: stable\n---\n# Note",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertTrue(any("Directory/type contract violation" in i.message for i in issues))

    def test_plans_max_depth_exceeded(self) -> None:
        doc = self.make_doc(
            "01-plans/homelab/subsystem/deep/too-deep.md",
            "---\ntype: plan\nstatus: active\n---\n# Plan",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertTrue(any("Nesting violation" in i.message for i in issues))

    def test_discussions_valid(self) -> None:
        doc = self.make_doc(
            "02-discussions/homelab/auth.md",
            "---\ntype: discussion\nstatus: open\n---\n# Disc",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertEqual(len(issues), 0)

    def test_journal_valid(self) -> None:
        doc = self.make_doc(
            "03-records/journal/2026-09-28.md",
            "---\ntype: journal\n---\n# Log",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertEqual(len(issues), 0)

    def test_journal_invalid_filename(self) -> None:
        doc = self.make_doc(
            "03-records/journal/my-notes.md",
            "---\ntype: journal\n---\n# Log",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertTrue(any("does not match required pattern" in i.message for i in issues))

    def test_projects_valid_readme(self) -> None:
        doc = self.make_doc(
            "06-projects/homelab/README.md",
            "---\ntype: project\nstatus: active\n---\n# Hub",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertEqual(len(issues), 0)

    def test_projects_invalid_arbitrary_file(self) -> None:
        doc = self.make_doc(
            "06-projects/homelab/guide.md",
            "---\ntype: project\nstatus: active\n---\n# Hub",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertTrue(any("must be named 'README.md'" in i.message for i in issues))

    def test_projects_invalid_depth(self) -> None:
        doc = self.make_doc(
            "06-projects/homelab/sub/README.md",
            "---\ntype: project\nstatus: active\n---\n# Hub",
        )
        issues = vb.check_directory_contracts(doc)
        self.assertTrue(any("exceeds max depth" in i.message for i in issues))

    def test_inbox_exempt(self) -> None:
        doc = self.make_doc(
            "00-inbox/scratch.md",
            "No frontmatter at all! Just raw unclassified capture.",
            validates_frontmatter=False,
        )
        issues = vb.check_directory_contracts(doc)
        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
