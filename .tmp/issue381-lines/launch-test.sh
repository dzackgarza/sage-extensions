#!/bin/bash
# usage: launch-test.sh <worktree> <log-path> [pytest args...]
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
WORKTREE=$1; shift
LOG=$1; shift
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
mkdir -p "$(dirname "$LOG")"
{
  echo "# tree: $(git -C "$WORKTREE" rev-parse HEAD)"
  echo "# tree status: $(git -C "$WORKTREE" status --porcelain | tr '\n' ' ')"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# command: pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint -q $*"
} > "$LOG"
TARGETS=""
for t in "$@"; do TARGETS="$TARGETS /repos/sage-extensions/$t"; done
cd "$HOME/sage-image"
set +e
timeout -s KILL 900 ./run.sh -w /work \
  -b "$PORT:/work" \
  -b /workspace/nucleus/work/home/ai-review-ci:/ci \
  -b "$REPO/.git:/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo/.git" \
  -b "$WORKTREE:/repos/sage-extensions" \
  -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; cd /repos/sage-extensions; exec /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint -q $TARGETS" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
