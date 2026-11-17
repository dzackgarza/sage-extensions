#!/bin/bash
# Run one probe in the pinned research image, under peakrss.py, logging to .scratch/381/$1.
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
NAME=${1:?give a log name}
SCRIPT=${2:?give a probe script}
LOG=$REPO/.scratch/381/$NAME.log
{
  echo "# tree: $(git -C "$REPO" rev-parse HEAD)"
  echo "# status: $(git -C "$REPO" status --porcelain | tr '\n' ' ')"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# program: $SCRIPT  PROBE_PLANES=${PROBE_PLANES:-unset} PROBE_PHASE=${PROBE_PHASE:-row}"
} > "$LOG"
cd "$HOME/sage-image"
set +e
PEAKRSS_LABEL=$NAME PEAKRS_LIMIT_MIB=0 timeout -s KILL "${WALL:-560}" python3 peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$REPO:/repos/sage-extensions" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src PROBE_PLANES=${PROBE_PLANES:-10} PROBE_PHASE=${PROBE_PHASE:-row}; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u /repos/sage-extensions/.scratch/381/$SCRIPT" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
