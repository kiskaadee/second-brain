#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

chmod +x .githooks/pre-commit .githooks/post-commit
git config core.hooksPath .githooks

echo "✅ Git hooks configured successfully:"
echo "   • core.hooksPath set to .githooks"
echo "   • pre-commit: structural validation via validate-brain.py"
echo "   • post-commit: auto-push to origin"
