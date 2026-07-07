#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

if [[ ! -f AGENTS.md ]]; then
  echo "ERROR: AGENTS.md is required." >&2
  exit 1
fi

if [[ ! -x scripts/workflow.sh ]]; then
  echo "ERROR: scripts/workflow.sh must exist and be executable." >&2
  exit 1
fi

bash -n scripts/workflow.sh

./scripts/workflow.sh validate

# CLAUDE.md is optional. If present, require it to point to AGENTS.md.
if [[ -f CLAUDE.md ]] && ! grep -Eq 'AGENTS\.md' CLAUDE.md; then
  echo "ERROR: CLAUDE.md exists but does not reference AGENTS.md." >&2
  exit 1
fi

legacy_hits=$(grep -RInE 'Junior Data Engineer|Let.s configure your AI context|interactively configure your project context' \
  README.md AGENTS.md docs standards 2>/dev/null || true)

if [[ -n "$legacy_hits" ]]; then
  echo "ERROR: Found legacy onboarding language:" >&2
  echo "$legacy_hits" >&2
  exit 1
fi

echo "Template checks: OK"
