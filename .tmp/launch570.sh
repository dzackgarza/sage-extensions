#!/bin/bash
# #570: run one probe inside the pinned image against this worktree.
#   TREE=<worktree> PROBE=<path inside the tree> LOG=<log> [INNER=..] [OUTER=..]
set -uo pipefail
WORKTREE=${TREE:?give TREE=<worktree>}
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
HOST=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
PROBE=${PROBE:?give PROBE=<path inside the tree>}
LOG=${LOG:?give LOG=<path>}
INNER=${INNER:-600}
OUTER=${OUTER:-700}
mkdir -p "$(dirname "$LOG")"
{
  echo "tree SHA: $(git -C "$WORKTREE" rev-parse HEAD) (modified paths: $(git -C "$WORKTREE" status --porcelain | wc -l))"
  echo "port SHA: $(git -C "$PORT" rev-parse HEAD)"
  echo "load: $(cat /proc/loadavg)"
  echo "probe: $PROBE; inner ${INNER} s"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=probe570 PEAKRSS_LIMIT_MIB=6144 timeout -s KILL "$OUTER" python3 -u peakrss.py -- \
  timeout -s KILL "$INNER" ./run.sh -w /work \
    -b "$PORT:/work" \
    -b "$WORKTREE:/repos/sage-extensions" \
    -b "$HOST:$HOST" \
    -- /bin/sh -c "export PYTHONPATH=/repos/sage-extensions/src:/work/src:/work; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u -s $PROBE" >> "$LOG" 2>&1
echo "probe exit: $?" >> "$LOG"
