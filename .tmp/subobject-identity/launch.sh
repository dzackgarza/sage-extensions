#!/bin/bash
# Run one probe in the pinned research image, under peakrss.py, logging to .scratch/588/$1.log.
set -uo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
TREE=${TREE:-$REPO}
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
NAME=${1:?give a log name}
SCRIPT=${2:?give a probe script}
PROG=${PROG:-/repos/sage-extensions}
LOG=$REPO/.scratch/588/$NAME.log
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo unversioned-worktree)"
  echo "# status: $(git -C "$TREE" status --porcelain 2>/dev/null | tr '\n' ' ')"
  echo "# port: $(git -C "$PORT" rev-parse HEAD 2>/dev/null)"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# program: $SCRIPT PROBE_PLANES=${PROBE_PLANES:-unset} PROBE_PHASE=${PROBE_PHASE:-unset} PYTHONHASHSEED=${PYTHONHASHSEED:-0}"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=$NAME PEAKRSS_LIMIT_MIB=${PEAKRSS_LIMIT_MIB:-0} timeout -s KILL "${WALL:-1200}" python3 -u peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" \
    ${GIT_BIND:+-b "$GIT_BIND"} \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work PROBE_PLANES=${PROBE_PLANES:-200} PROBE_PHASE=${PROBE_PHASE:-row} PROBE_SHAPE=${PROBE_SHAPE:-representatives} PROBE_CHECKPOINTS=${PROBE_CHECKPOINTS:-10,100,200} SPECIMEN=${SPECIMEN:-plane} PYTHONHASHSEED=${PYTHONHASHSEED:-0}; cd $PROG; exec /sage/.venv/bin/python -u $SCRIPT" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
