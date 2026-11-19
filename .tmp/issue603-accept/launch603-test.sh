#!/bin/bash
# #603: run the touched test files inside the pinned image against this worktree.
#   FILES=<space separated, inside the tree> LOG=<log> [INNER=..] [OUTER=..] [EXTRA=..]
set -uo pipefail
WORKTREE=$(cd "$(dirname "$0")/.." && pwd)
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
PLUGINS=$HOME/ai-review-ci/tool-artifacts/pytest_plugins
HOST=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
FILES=${FILES:?give FILES=<test files>}
LOG=${LOG:?give LOG=<path>}
EXTRA=${EXTRA:-}
INNER=${INNER:-900}
OUTER=${OUTER:-1000}
case "$LOG" in /*) ;; *) LOG="$WORKTREE/$LOG" ;; esac
mkdir -p "$(dirname "$LOG")"
{
  echo "tree SHA: $(git -C "$WORKTREE" rev-parse HEAD) (modified paths: $(git -C "$WORKTREE" status --porcelain | wc -l))"
  echo "port SHA: $(git -C "$PORT" rev-parse HEAD)"
  echo "load: $(cat /proc/loadavg)"
  echo "files: $FILES; inner ${INNER} s"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=test603 PEAKRSS_LIMIT_MIB=6144 timeout -s KILL "$OUTER" python3 -u peakrss.py -- \
  timeout -s KILL "$INNER" ./run.sh -w /work \
    -b "$PORT:/work" \
    -b "$WORKTREE:/repos/sage-extensions" \
    -b "$HOST:$HOST" \
    -b "$PLUGINS:/ci/tool-artifacts/pytest_plugins" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --durations=0 $EXTRA $FILES" >> "$LOG" 2>&1
echo "test exit: $?" >> "$LOG"
