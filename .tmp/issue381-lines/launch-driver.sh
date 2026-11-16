#!/bin/bash
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
WORKTREE=$REPO/.scratch/wt381v
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
LOG=$WORKTREE/.tmp/issue381-lines/driver-u-u2-m2.log
mkdir -p "$(dirname "$LOG")"
{ echo "# tree: $(git -C "$WORKTREE" rev-parse HEAD)"; echo "# tree status: $(git -C "$WORKTREE" status --porcelain | tr "\n" " ")"; echo "# load: $(cut -d" " -f1-3 /proc/loadavg)"; } > "$LOG"
cd "$HOME/sage-image"
set +e
timeout -s KILL 420 ./run.sh -w /work -b "$PORT:/work" -b /workspace/nucleus/work/home/ai-review-ci:/ci -b "$REPO/.git:/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo/.git" -b "$WORKTREE:/repos/sage-extensions" -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u tests/coble_gamma_co_2_incidence_rows.py --rows Otilde,Otilde+ --lattice \"U+U(2)+<-2>\" --cap 120 --budget 300" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
