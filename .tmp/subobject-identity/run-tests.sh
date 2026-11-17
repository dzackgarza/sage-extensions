#!/bin/bash
# Run pytest inside the pinned research image on the given files, logging to .scratch/588/$1.log.
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
TREE=${TREE:-$REPO}
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
NAME=${1:?give a log name}
shift
LOG=$REPO/.scratch/588/$NAME.log
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD)"
  echo "# status: $(git -C "$REPO" status --porcelain | tr '\n' ' ')"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# pytest: $*"
} > "$LOG"
cd "$HOME/sage-image"
set +e
timeout -s KILL "${WALL:-560}" ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" \
    ${GIT_BIND:+-b "$GIT_BIND"} \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; cd /repos/sage-extensions; exec /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --durations=0 $*" >> "$LOG" 2>&1
echo "# runner exit: $?" >> "$LOG"
