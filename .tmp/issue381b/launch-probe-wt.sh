#!/bin/bash
# One probe in the pinned research image, from this worktree, logged in it.
# usage: launch-probe-wt.sh <log-name> <script relative to the worktree>; env: TREE WALL PEAKRSS_LIMIT_MIB PROBE_*
set -uo pipefail
TREE=${TREE:?give the tree to bind at /repos/sage-extensions}
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
# A worktree's .git is a file naming the main checkout's git directory by
# absolute path, so that directory is bound where the file says it is.
GITDIR=$(cd "$TREE" && git rev-parse --path-format=absolute --git-common-dir)
NAME=${1:?give a log name}; SCRIPT=${2:?give a probe script}
LOG=$TREE/.tmp/issue381b/$NAME.log
mkdir -p "$TREE/.tmp/issue381b"
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo unversioned-worktree)"
  echo "# status: $(git -C "$TREE" status --porcelain 2>/dev/null | tr '\n' ' ')"
  echo "# port: $(git -C "$PORT" rev-parse HEAD 2>/dev/null)"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# free: $(free -m | awk '/Mem:/{print $7" MiB available"}')"
  echo "# started: $(date -u +%FT%TZ)"
  echo "# program: $SCRIPT  PROBE_LATTICE=${PROBE_LATTICE:-unset} PROBE_ROW=${PROBE_ROW:-unset}"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=$NAME PEAKRSS_LIMIT_MIB=${PEAKRSS_LIMIT_MIB:-6144} timeout -s KILL "${WALL:-1800}" python3 -u peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" \
    -b "$GITDIR:$GITDIR" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work SAGE_BIN=/sage/.venv/bin/python PYTHONHASHSEED=0 GIT_CEILING_DIRECTORIES=/ PROBE_LATTICE='${PROBE_LATTICE:-unset}' PROBE_ROW='${PROBE_ROW:-Otilde}' PROBE_PHASE='${PROBE_PHASE:-split}' PROBE_MARK='${PROBE_MARK:-1000}' PROBE_CHECKPOINT='${PROBE_CHECKPOINT:-}' PROBE_REPEATS='${PROBE_REPEATS:-50}' ; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u $SCRIPT" >> "$LOG" 2>&1
echo "# launcher exit: $?  ended: $(date -u +%FT%TZ)" >> "$LOG"
