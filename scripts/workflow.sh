#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLAN_PATH="$REPO_ROOT/docs/workflow/PLAN.md"
DECISIONS_PATH="$REPO_ROOT/docs/workflow/DECISIONS.md"
GATES_PATH="$REPO_ROOT/docs/workflow/GATES.md"

usage() {
  cat <<USAGE
Usage:
  ./scripts/workflow.sh status
  ./scripts/workflow.sh prompt
  ./scripts/workflow.sh validate
USAGE
}

read_current_phase() {
  local lines count value
  lines="$({ grep -E '^\*\*Current Phase:\*\*[[:space:]]*[0-9]+' "$PLAN_PATH" || true; })"
  if [[ -n "$lines" ]]; then
    count=$(printf '%s\n' "$lines" | wc -l | tr -d ' ')
    if [[ "$count" -gt 1 ]]; then
      echo "ERROR: PLAN.md has $count '**Current Phase:**' markers; expected exactly one." >&2
      return 1
    fi
  fi
  value="$(printf '%s\n' "$lines" | head -n 1 | sed -E 's/^\*\*Current Phase:\*\*[[:space:]]*([0-9]+).*$/\1/')"
  printf '%s' "$value"
}

list_phase_rows() {
  grep -E '^## Phase [0-9]+:' "$PLAN_PATH" | sed -E 's/^## Phase ([0-9]+):[[:space:]]*(.+)$/\1|\2/'
}

render_phase_block() {
  local key="$1"
  awk -v key="$key" '
    $0 ~ "^## Phase " key ":" {in_block=1}
    in_block && $0 ~ "^## Phase [0-9]+:" && $0 !~ "^## Phase " key ":" {exit}
    in_block {print}
  ' "$PLAN_PATH"
}

phase_body() {
  local key="$1"
  awk -v key="$key" '
    $0 ~ "^## Phase " key ":" {in_block=1; next}
    in_block && $0 ~ "^## Phase [0-9]+:" {exit}
    in_block {print}
  ' "$PLAN_PATH"
}

checklist_totals() {
  local key="$1"
  local block total done
  block="$(phase_body "$key")"

  total=$(printf '%s\n' "$block" | { grep -E '^[[:space:]]*- \[[ xX]\] .+' || true; } | wc -l | tr -d ' ')
  done=$(printf '%s\n' "$block" | { grep -E '^[[:space:]]*- \[[xX]\] .+' || true; } | wc -l | tr -d ' ')
  printf '%s %s\n' "$done" "$total"
}

is_unchecked_in_phase() {
  local key="$1"
  local block
  block="$(phase_body "$key")"
  if printf '%s\n' "$block" | grep -Eq '^[[:space:]]*- \[ \] .+'; then
    return 0
  fi
  return 1
}

phase_has_checklist() {
  local key="$1"
  local block
  block="$(phase_body "$key")"
  if printf '%s\n' "$block" | grep -Eq '^[[:space:]]*- \[[ xX]\] .+'; then
    return 0
  fi
  return 1
}

gates_phase_body() {
  local key="$1"
  awk -v key="$key" '
    $0 ~ "^## Phase " key ":" {in_block=1; next}
    in_block && $0 ~ "^## Phase [0-9]+:" {exit}
    in_block {print}
  ' "$GATES_PATH"
}

gate_has_unchecked() {
  local key="$1"
  gates_phase_body "$key" | grep -Eq '^[[:space:]]*- \[ \] .+'
}

contains_line() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    if [[ "$item" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

validate_required_contract_fields() {
  local fields missing line value field errors
  fields=("Objective" "Success criteria" "Constraints" "Non-goals" "Risks")
  errors=0

  for field in "${fields[@]}"; do
    line=$(grep -E "^- \\*\\*$field:\\*\\*" "$PLAN_PATH" | head -n 1 || true)

    if [[ -z "$line" ]]; then
      echo "ERROR: Project Contract missing required field '$field' in PLAN.md." >&2
      errors=$((errors + 1))
      continue
    fi

    value=$(printf '%s' "$line" | sed -E "s/^- \\*\\*$field:\\*\\*[[:space:]]*//")

    if [[ -z "${value// }" ]]; then
      echo "ERROR: Project Contract field '$field' is empty in PLAN.md." >&2
      errors=$((errors + 1))
      continue
    fi

    if printf '%s' "$value" | grep -Eqi 'TBD|TODO'; then
      echo "ERROR: Project Contract field '$field' still has placeholder text (TBD/TODO)." >&2
      errors=$((errors + 1))
    fi
  done

  printf '%s\n' "$errors"
}

cmd_status() {
  local current_phase rows row key title done total marker blockers

  current_phase="$(read_current_phase)"
  if [[ -z "$current_phase" ]]; then
    echo "Error: PLAN.md missing '**Current Phase:** N' marker." >&2
    return 1
  fi

  rows=()
  while IFS= read -r row; do
    rows+=("$row")
  done < <(list_phase_rows)
  if [[ ${#rows[@]} -eq 0 ]]; then
    echo "Error: No phase headers found in PLAN.md." >&2
    return 1
  fi

  echo "Project Workflow Status"
  echo "========================================"

  for row in "${rows[@]}"; do
    key="${row%%|*}"
    title="${row#*|}"
    read -r done total < <(checklist_totals "$key")
    marker="   "
    if [[ "$key" == "$current_phase" ]]; then
      marker=">>>"
      echo "Current Phase: Phase $key: $title"
      echo
    fi
    echo "  $marker Phase $key: $done/$total complete"
  done

  blockers="$({
    awk '
      $0 == "## Blockers" {in_blockers=1; next}
      in_blockers && ($0 ~ /^## / || $0 ~ /^---$/) {exit}
      in_blockers && $0 ~ /^- / {
        line=$0
        sub(/^- /, "", line)
        lower=tolower(line)
        if (lower != "none") print line
      }
    ' "$PLAN_PATH"
  } || true)"

  if [[ -n "$blockers" ]]; then
    echo
    echo "Blockers:"
    while IFS= read -r blocker; do
      echo "  - $blocker"
    done <<<"$blockers"
  fi

  echo
  echo "Current Phase Checklist:"
  phase_body "$current_phase" | { grep -E '^[[:space:]]*- \[[ xX]\] .+' || true; }
}

cmd_prompt() {
  local current_phase
  current_phase="$(read_current_phase)"
  if [[ -z "$current_phase" ]]; then
    echo "Error: PLAN.md missing '**Current Phase:** N' marker." >&2
    return 1
  fi

  render_phase_block "$current_phase"
}

cmd_validate() {
  local errors warnings current_phase
  local rows gate_rows decision_count contract_errors
  local row key title

  errors=0
  warnings=0

  if [[ ! -f "$PLAN_PATH" ]]; then
    echo "ERROR: Missing docs/workflow/PLAN.md" >&2
    errors=$((errors + 1))
  fi
  if [[ ! -f "$DECISIONS_PATH" ]]; then
    echo "ERROR: Missing docs/workflow/DECISIONS.md" >&2
    errors=$((errors + 1))
  fi
  if [[ ! -f "$GATES_PATH" ]]; then
    echo "ERROR: Missing docs/workflow/GATES.md" >&2
    errors=$((errors + 1))
  fi

  if ((errors > 0)); then
    echo
    echo "Validation failed: $errors error(s), $warnings warning(s)."
    return 1
  fi

  current_phase="$(read_current_phase)"
  if [[ -z "$current_phase" ]]; then
    echo "ERROR: PLAN.md missing '**Current Phase:** N' marker." >&2
    errors=$((errors + 1))
  fi

  rows=()
  while IFS= read -r row; do
    rows+=("$row")
  done < <(list_phase_rows)
  if [[ ${#rows[@]} -eq 0 ]]; then
    echo "ERROR: PLAN.md must include at least one '## Phase N: Title' section." >&2
    errors=$((errors + 1))
  fi

  if ((errors == 0)); then
    contract_errors=$(validate_required_contract_fields)
    errors=$((errors + contract_errors))

    gate_rows=()
    while IFS= read -r row; do
      gate_rows+=("$row")
    done < <(grep -E '^## Phase [0-9]+:' "$GATES_PATH" | sed -E 's/^## Phase ([0-9]+):.*$/\1/' || true)

    local phase_keys=()
    local gate_keys=()

    for row in "${rows[@]}"; do
      key="${row%%|*}"
      title="${row#*|}"
      phase_keys+=("$key")

      if ! phase_has_checklist "$key"; then
        echo "ERROR: Phase $key ('$title') has no checklist items." >&2
        errors=$((errors + 1))
      fi

      if [[ "$key" -lt "$current_phase" ]] && is_unchecked_in_phase "$key"; then
        echo "ERROR: Prior phase $key has unchecked checklist items, but current phase is $current_phase." >&2
        errors=$((errors + 1))
      fi

      if [[ "$key" -lt "$current_phase" ]] && gate_has_unchecked "$key"; then
        echo "ERROR: Prior phase $key has unchecked gate criteria in GATES.md, but current phase is $current_phase." >&2
        errors=$((errors + 1))
      fi
    done

    for key in ${gate_rows[@]+"${gate_rows[@]}"}; do
      gate_keys+=("$key")
    done

    for key in "${phase_keys[@]}"; do
      if ! contains_line "$key" ${gate_keys[@]+"${gate_keys[@]}"}; then
        echo "WARNING: GATES.md has no section for Phase $key." >&2
        warnings=$((warnings + 1))
      fi
    done

    if ! contains_line "$current_phase" "${phase_keys[@]}"; then
      echo "ERROR: Current phase '$current_phase' is not defined in PLAN.md." >&2
      errors=$((errors + 1))
    fi
  fi

  decision_count=$(grep -Ec '^## ADR-[0-9]+:' "$DECISIONS_PATH" || true)
  if [[ "$decision_count" -lt 1 ]]; then
    echo "WARNING: DECISIONS.md contains no ADR entries." >&2
    warnings=$((warnings + 1))
  fi

  if ((errors > 0)); then
    echo
    echo "Validation failed: $errors error(s), $warnings warning(s)."
    return 1
  fi

  if ((warnings > 0)); then
    echo "Validation passed with $warnings warning(s)."
    return 0
  fi

  echo "Workflow docs: OK"
}

main() {
  if [[ $# -ne 1 ]]; then
    usage
    return 1
  fi

  case "$1" in
    status)
      cmd_status
      ;;
    prompt)
      cmd_prompt
      ;;
    validate)
      cmd_validate
      ;;
    *)
      usage
      return 1
      ;;
  esac
}

main "$@"
