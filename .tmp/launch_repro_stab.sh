#!/bin/bash
set -uo pipefail
cd /workspace/nucleus/work/home/sage-image
export PEAKRSS_LABEL=repro-marked-stab
export PEAKRSS_LIMIT_MIB=6144
exec timeout -s KILL 2700 python3 peakrss.py -- \
  timeout -s KILL 2400 ./run.sh \
    -w /work \
    -b /workspace/nucleus/work/projects/p-165a6922b36b40789ddc90db34bb23c7/repo:/work \
    -b /workspace/nucleus/work/home/ai-review-ci:/ci \
    -b /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo:/repos/sage-extensions \
    -b /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo/.tmp/repro_marked_stabilizer.py:/probe.py \
    -- /bin/sh -c 'export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; exec python -u -s /probe.py' \
  > /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo/.tmp/repro_marked_stabilizer.log 2>&1
