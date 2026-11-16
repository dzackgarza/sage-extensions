#!/bin/bash
# usage: launch.sh <log-name> <program-absolute-path> [inner-seconds]
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
WORKTREE=$REPO/.scratch/wt381v
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
NAME=$1; shift
PROGRAM=$1; shift
INNER=${1:-480}
LOG=$WORKTREE/.tmp/issue381-lines/$NAME.log
mkdir -p "$WORKTREE/.tmp/issue381-lines"
{
  echo "# tree: $(git -C "$WORKTREE" rev-parse HEAD)"
  echo "# tree status: $(git -C "$WORKTREE" status --porcelain | tr '\n' ' ')"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# program: $PROGRAM"
} > "$LOG"
cd "$HOME/sage-image"
set +e
PEAKRSS_LABEL=$NAME PEAKRSS_LIMIT_MIB=${LIMIT:-6144} timeout -s KILL $((INNER+90)) \
  python3 "$HOME/sage-image/peakrss.py" -- \
  timeout -s KILL "$INNER" ./run.sh -w /work \
  -b "$PORT:/work" \
  -b /workspace/nucleus/work/home/ai-review-ci:/ci \
  -b "$REPO/.git:/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo/.git" \
  -b "$WORKTREE:/repos/sage-extensions" \
  -b "$PROGRAM:/probe.py" \
  -- /bin/sh -c "export PROBE_CAP=${PROBE_CAP:-420}; export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u -s /probe.py" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
