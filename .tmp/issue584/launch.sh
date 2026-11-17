#!/bin/bash
# Run one #584 probe in the pinned research image, logging to .scratch/584/<name>.log.
#   usage: WALL=300 ./launch.sh <logname> <probe.py> [PROBE_PLANES=...]
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
TREE=${TREE:-$REPO/.scratch/w584}
NAME=${1:?give a log name}
SCRIPT=${2:?give a probe script}
LOG=$REPO/.scratch/584/$NAME.log
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD)"
  echo "# status: $(git -C "$TREE" status --porcelain | tr '\n' ' ')"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# program: $SCRIPT  PROBE_PLANES=${PROBE_PLANES:-unset} PROBE_MODE=${PROBE_MODE:-baseline} PROBE_METER_EVERY=${PROBE_METER_EVERY:-0}"
} > "$LOG"
cd "$HOME/sage-image"
set +e
PEAKRSS_LABEL=$NAME PEAKRSS_LIMIT_MIB=0 timeout -s KILL "${WALL:-560}" python3 peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" \
    -b "$REPO/.git:$REPO/.git" \
    -b "$REPO/.scratch/584:/probe" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src PROBE_PLANES=${PROBE_PLANES:-10} PROBE_MODE=${PROBE_MODE:-baseline} PROBE_MAXDEPTH=${PROBE_MAXDEPTH:-14} PROBE_METER_EVERY=${PROBE_METER_EVERY:-0}; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u /probe/$SCRIPT" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
