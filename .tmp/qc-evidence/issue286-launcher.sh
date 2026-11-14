#!/bin/bash
# Launch one probe in the adopted runtime with the pinned port clone at /work.
#   PROBE=<file in .scratch>  LOG=<path under .tmp>  [INNER] [OUTER]
set -uo pipefail
HERE=/workspace/nucleus/work/home/sage-image
PROVIDER=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
PORT="$PROVIDER/.scratch/port-991b88b0"
PROBE=${PROBE:?set PROBE}
LOG=${LOG:?set LOG}
INNER=${INNER:-1800}
OUTER=${OUTER:-1900}
cd "$HERE" || exit 1
PEAKRSS_LABEL=issue286 PEAKRSS_LIMIT_MIB=6144 \
  timeout -s KILL "$OUTER" python3 -u peakrss.py -- \
  timeout -s KILL "$INNER" ./run.sh -w /work \
    -b "$PORT:/work" \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b "$PROVIDER:/repos/sage-extensions" \
    -b "$PROVIDER/.scratch/$PROBE:/probe.py" \
    -- /bin/sh -c 'export PATH=/sage/.venv/bin:$PATH; export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; exec /sage/.venv/bin/python -u -s /probe.py' \
  > "$PROVIDER/$LOG" 2>&1
echo "launcher exit: $?" >> "$PROVIDER/$LOG"
