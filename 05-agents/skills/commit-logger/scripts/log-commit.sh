#!/usr/bin/env bash
# log-commit.sh - Deterministic Git commit event capture for Brain
# Appends verified commit metadata into 00-inbox/commit-log.csv

set -euo pipefail

BRAIN_ROOT="${BRAIN_ROOT:-/home/kiskaadee/Brain}"
LEDGER_FILE="${BRAIN_ROOT}/00-inbox/commit-log.csv"

TARGET_REF="HEAD"
FORCE_ALLOW_BRAIN=false

for arg in "$@"; do
    if [[ "$arg" == "--force" ]] || [[ "$arg" == "--allow-brain" ]]; then
        FORCE_ALLOW_BRAIN=true
    elif [[ "$arg" != -* ]]; then
        TARGET_REF="$arg"
    fi
done

# 1. Verify Git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "commit-logger: not inside a git repository. Exiting." >&2
    exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "${REPO_ROOT}")"

# 2. Anti-Recursion Invariant: Brain is non-loggable unless explicitly forced
if [[ "${REPO_ROOT}" == "${BRAIN_ROOT}" ]] || [[ "${REPO_NAME}" == "Brain" ]]; then
    if [[ "${FORCE_ALLOW_BRAIN}" != "true" ]]; then
        # Silent exit as a no-op to prevent recursion
        exit 0
    fi
fi

# 3. Extract Immutable Git Metadata
COMMIT_SHA="$(git rev-parse "${TARGET_REF}")"
PARENT_SHA="$(git rev-parse "${COMMIT_SHA}^" 2>/dev/null || echo "")"
COMMITTED_AT="$(git show -s --format=%cI "${COMMIT_SHA}")"
SUBJECT="$(git show -s --format=%s "${COMMIT_SHA}")"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")"

# 4. Authoritative Project Mapping
PROJECT=""
if [[ "${REPO_ROOT}" == "${BRAIN_ROOT}" ]] || [[ "${REPO_NAME}" == "Brain" ]]; then
    PROJECT="brain"
elif [[ -d "${BRAIN_ROOT}/06-projects/${REPO_NAME}" ]]; then
    PROJECT="${REPO_NAME}"
elif [[ -d "${BRAIN_ROOT}/06-projects" ]]; then
    # Look for matching project directory containing repository reference in README.md
    for proj_dir in "${BRAIN_ROOT}/06-projects"/*; do
        if [[ -f "${proj_dir}/README.md" ]]; then
            if grep -qi "${REPO_NAME}" "${proj_dir}/README.md"; then
                PROJECT="$(basename "${proj_dir}")"
                break
            fi
        fi
    done
fi

# 5. CSV Formatting (RFC 4180 Escaping)
escape_csv() {
    local val="$1"
    # Double existing double quotes
    val="${val//\"/\"\"}"
    # Quote if string contains comma, quote, or newline
    if [[ "${val}" =~ [,\"\n\r] ]]; then
        echo "\"${val}\""
    else
        echo "${val}"
    fi
}

ESCAPED_SUBJECT="$(escape_csv "${SUBJECT}")"

# 6. Ensure Ledger File and Header Exist
mkdir -p "$(dirname "${LEDGER_FILE}")"
if [[ ! -f "${LEDGER_FILE}" ]]; then
    echo "committed_at,repository,project,branch,commit_sha,parent_sha,subject" > "${LEDGER_FILE}"
fi

# 7. Idempotency Barrier: Full 40-char SHA deduplication
if grep -q ",${COMMIT_SHA}," "${LEDGER_FILE}" 2>/dev/null; then
    # Commit already recorded
    exit 0
fi

# 8. Atomic Append
echo "${COMMITTED_AT},${REPO_NAME},${PROJECT},${BRANCH},${COMMIT_SHA},${PARENT_SHA},${ESCAPED_SUBJECT}" >> "${LEDGER_FILE}"
