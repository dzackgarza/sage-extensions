#!/bin/bash
# #570: run the named test files inside the pinned image against this worktree.
set -uo pipefail
WORKTREE=${TREE:?give TREE=<worktree>}
HOST=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
LOG=${LOG:?give LOG=<path>}
shift_args=${*:?give test paths}
INNER=${INNER:-480}
mkdir -p "$(dirname "$LOG")"
{
  echo "tree SHA: $(git -C "$WORKTREE" rev-parse HEAD) (modified paths: $(git -C "$WORKTREE" status --porcelain | wc -l))"
  echo "port SHA: $(git -C "$PORT" rev-parse HEAD)"
  echo "load: $(cat /proc/loadavg)"
  echo "tests: $shift_args"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=probe570 PEAKRSS_LIMIT_MIB=6144 timeout -s KILL "$((INNER + 80))" python3 -u peakrss.py -- \
  timeout -s KILL "$INNER" ./run.sh -w /work \
    -b "$PORT:/work" \
    -b "$WORKTREE:/repos/sage-extensions" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$HOST:$HOST" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work; cd /repos/sage-extensions; exec /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates --durations=0 $shift_args" >> "$LOG" 2>&1
echo "tests exit: $?" >> "$LOG"
