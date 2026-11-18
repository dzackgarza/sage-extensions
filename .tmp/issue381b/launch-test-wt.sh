#!/bin/bash
# One test file in the pinned research image, from this worktree, logged in it.
# usage: launch-test-wt.sh <log-name> <test path relative to the worktree>
set -uo pipefail
TREE=${TREE:?give the tree to bind at /repos/sage-extensions}
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
GITDIR=$(cd "$TREE" && git rev-parse --path-format=absolute --git-common-dir)
NAME=${1:?give a log name}; FILE=${2:?give a test file}
LOG=$TREE/.tmp/issue381b/$NAME.log
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo unversioned-worktree)"
  echo "# status: $(git -C "$TREE" status --porcelain 2>/dev/null | tr '\n' ' ')"
  echo "# free: $(free -m | awk '/Mem:/{print $7" MiB available"}')"
  echo "# started: $(date -u +%FT%TZ)"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=$NAME PEAKRSS_LIMIT_MIB=${PEAKRSS_LIMIT_MIB:-6144} timeout -s KILL "${WALL:-1800}" python3 -u peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" -b "$GITDIR:$GITDIR" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work SAGE_BIN=/sage/.venv/bin/python PYTHONHASHSEED=0 GIT_CEILING_DIRECTORIES=/ ; cd /repos/sage-extensions; exec /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates --durations=0 -q $FILE" >> "$LOG" 2>&1
echo "# launcher exit: $?  ended: $(date -u +%FT%TZ)" >> "$LOG"
