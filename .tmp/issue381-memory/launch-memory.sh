#!/bin/bash
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
WORKTREE=$REPO/.scratch/w381mem
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
LOG=$WORKTREE/.tmp/issue381-memory/${1:?give a log name}
mkdir -p "$(dirname "$LOG")"
{ echo "# tree: $(git -C "$WORKTREE" rev-parse HEAD)"; echo "# status: $(git -C "$WORKTREE" status --porcelain | tr '\n' ' ')"; echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"; } > "$LOG"
cd "$HOME/sage-image"
set +e
timeout -s KILL 620 ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$REPO/.git:/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo/.git" \
    -b "$WORKTREE:/repos/sage-extensions" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src PROBE_PLANES=${PROBE_PLANES:-1200} PROBE_EDGE_PLANES=${PROBE_EDGE_PLANES:-400}; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u /repos/sage-extensions/.tmp/issue381-memory/probe-incidence-memory.py" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
