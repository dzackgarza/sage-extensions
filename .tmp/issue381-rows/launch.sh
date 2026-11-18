#!/bin/bash
# One row of the kernel incidence driver in the pinned research image, under peakrss.py.
# usage: launch.sh <log-name> <driver arguments...>;  env: TREE WALL PEAKRSS_LIMIT_MIB
set -uo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
TREE=${TREE:-$REPO}
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
NAME=${1:?give a log name}; shift
DRIVER="tests/coble_gamma_co_2_incidence_rows.py"
for argument in "$@"; do DRIVER="$DRIVER $(printf '%q' "$argument")"; done
LOG=$REPO/.tmp/issue381-rows/$NAME.log
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo unversioned-worktree)"
  echo "# status: $(git -C "$TREE" status --porcelain 2>/dev/null | tr '\n' ' ')"
  echo "# port: $(git -C "$PORT" rev-parse HEAD 2>/dev/null)"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# free: $(free -m | awk '/Mem:/{print $7" MiB available"}')"
  echo "# started: $(date -u +%FT%TZ)"
  echo "# program: $DRIVER  PYTHONHASHSEED=0"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=$NAME PEAKRSS_LIMIT_MIB=${PEAKRSS_LIMIT_MIB:-6144} timeout -s KILL "${WALL:-1800}" python3 -u peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work SAGE_BIN=/sage/.venv/bin/python PYTHONHASHSEED=0; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u $DRIVER" >> "$LOG" 2>&1
echo "# launcher exit: $?  ended: $(date -u +%FT%TZ)" >> "$LOG"
