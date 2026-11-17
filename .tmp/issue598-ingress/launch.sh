#!/bin/bash
# One probe in the pinned research image, under peakrss.py.
# usage: launch.sh <log-name> <probe script>;  env: PROBE_* WALL PEAKRSS_LIMIT_MIB TREE
set -uo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
TREE=${TREE:-$REPO}
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
NAME=${1:?give a log name}
SCRIPT=${2:?give a probe script}
PROG=/repos/sage-extensions
LOG=$REPO/.tmp/issue598-ingress/$NAME.log
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo unversioned-worktree)"
  echo "# status: $(git -C "$TREE" status --porcelain 2>/dev/null | tr '\n' ' ')"
  echo "# port: $(git -C "$PORT" rev-parse HEAD 2>/dev/null)"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# program: $SCRIPT PROBE_PLANES=${PROBE_PLANES:-unset} PROBE_BAND=${PROBE_BAND:-unset} PYTHONHASHSEED=${PYTHONHASHSEED:-0}"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=$NAME PEAKRSS_LIMIT_MIB=${PEAKRSS_LIMIT_MIB:-0} timeout -s KILL "${WALL:-600}" python3 -u peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work PROBE_PLANES=${PROBE_PLANES:-1000} PROBE_BAND=${PROBE_BAND:-100} PYTHONHASHSEED=${PYTHONHASHSEED:-0}; cd $PROG; exec /sage/.venv/bin/python -u $SCRIPT" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
