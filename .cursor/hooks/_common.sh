# Shared utilities for Cursor hooks. Source this from hook scripts only.
# shellcheck shell=bash

_hook_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$_hook_dir/../.." && pwd)"
export REPO_ROOT

# Hooks often inherit a minimal PATH (e.g. Cursor started from a desktop
# launcher). Prepend common toolchain dirs without introducing an empty entry.
prepend_path_segments() {
  local home="${HOME:-}" d
  local -a prefixes=(
    "${home}/.cargo/bin"
    "${home}/.local/bin"
    "${home}/miniconda3/condabin"
    "${home}/miniconda3/bin"
    "${home}/miniforge3/condabin"
    "${home}/miniforge3/bin"
    "${home}/mambaforge/bin"
    "${home}/anaconda3/bin"
    "${home}/micromamba/bin"
    "/opt/miniconda3/bin"
    "/usr/local/bin"
    "/usr/bin"
  )
  for d in "${prefixes[@]}"; do
    if [[ -n "$d" && -d "$d" ]]; then
      # Use ${PATH:+:${PATH}} so an empty inherited PATH never produces a
      # trailing colon (which would silently inject cwd into PATH).
      PATH="${d}${PATH:+:${PATH}}"
    fi
  done
  export PATH
}

# Best-effort cwd; do not abort the hook if it fails.
cd "$REPO_ROOT" 2>/dev/null || true
prepend_path_segments

# Pick the first conda env that has a working python. Returns env name on
# stdout, or 1 if none found.
infer_sandbox_conda_env() {
  command -v conda >/dev/null 2>&1 || return 1
  local env
  for env in nvidia nvidia311; do
    if conda run -n "$env" python -c "pass" >/dev/null 2>&1; then
      printf '%s' "$env"
      return 0
    fi
  done
  return 1
}

# Resolve the canonical "project python" runner and store it as an array in
# PROJECT_PYTHON_CMD. Callers do: "${PROJECT_PYTHON_CMD[@]}" -m <module> ...
# Resolution order:
#   1. repo .venv / venv
#   2. uv (with UV_PROJECT pinned to repo)
#   3. project conda env (nvidia / nvidia311)
#   4. system python3 / python
# Returns 1 if no interpreter was found.
PROJECT_PYTHON_CMD=()
pick_project_python() {
  PROJECT_PYTHON_CMD=()
  local conda_env py
  if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
    PROJECT_PYTHON_CMD=( "${REPO_ROOT}/.venv/bin/python" )
  elif [[ -x "${REPO_ROOT}/venv/bin/python" ]]; then
    PROJECT_PYTHON_CMD=( "${REPO_ROOT}/venv/bin/python" )
  elif command -v uv >/dev/null 2>&1; then
    PROJECT_PYTHON_CMD=( env "UV_PROJECT=${REPO_ROOT}" uv run python )
  elif conda_env="$(infer_sandbox_conda_env)"; then
    PROJECT_PYTHON_CMD=( conda run -n "$conda_env" python )
  else
    for py in python3 python; do
      if command -v "$py" >/dev/null 2>&1; then
        PROJECT_PYTHON_CMD=( "$py" )
        return 0
      fi
    done
    return 1
  fi
  return 0
}
