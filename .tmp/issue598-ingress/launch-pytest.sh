#!/bin/bash
# One pytest run in the pinned research image over a tree bound at /repos/sage-extensions.
# usage: launch-pytest.sh <log-name> <tree> <pytest arguments...>
set -uo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
NAME=${1:?give a log name}
TREE=${2:?give a tree}
shift 2
PORT=/workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo
LOG=$REPO/.tmp/issue598-ingress/$NAME.log
{
  echo "# tree: $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo unversioned)"
  echo "# status: $(git -C "$TREE" status --porcelain 2>/dev/null | tr '\n' ' ')"
  echo "# port: $(git -C "$PORT" rev-parse HEAD 2>/dev/null)"
  echo "# load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "# pytest: $*"
} > "$LOG"
cd "$HOME/sage-image"
PEAKRSS_LABEL=$NAME timeout -s KILL "${WALL:-900}" python3 -u peakrss.py -- ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$TREE:/repos/sage-extensions" \
    -- /bin/sh -c "export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src:/work/src:/work SAGE_BIN=/sage/.venv/bin/python PYTHONHASHSEED=0; cd /repos/sage-extensions; exec /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint $*" >> "$LOG" 2>&1
echo "# launcher exit: $?" >> "$LOG"
