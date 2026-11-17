#!/bin/bash
# Run pytest inside the pinned image on a tree, the way the memory probe's
# launcher runs its probe (same binds, same interpreter).
#   usage: launch-pytest.sh <tree> <log> <pytest args...>
set -uo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
WORKTREE=${1:?give the tree}
LOG=$(realpath -m "${2:?give the log}")
shift 2
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
mkdir -p "$(dirname "$LOG")"
{ echo "# tree: $(git -C "$WORKTREE" rev-parse HEAD)"; echo "# status: $(git -C "$WORKTREE" status --porcelain | tr '\n' ' ')"; echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"; echo "# argv: $*"; } > "$LOG"
cd "$HOME/sage-image"
timeout -s KILL 900 ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$REPO/.git:$REPO/.git" \
    -b "$WORKTREE:/repos/sage-extensions" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; cd /repos/sage-extensions; exec /sage/.venv/bin/python -u -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates --durations=0 $*" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
