#!/bin/bash
# The slice comparison, then the curve at three row lengths, one process a run.
set -uo pipefail
cd /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
PROBE_PLANES=100 WALL=1200 .tmp/issue598-ingress/launch.sh slice .tmp/issue598-ingress/probe-slice.py
for planes in 1000 10000 100000; do
  PROBE_PLANES=$planes PROBE_BAND=$((planes / 10)) WALL=2400 PEAKRSS_LIMIT_MIB=6144 \
    .tmp/issue598-ingress/launch.sh growth-$planes .tmp/issue598-ingress/probe-ingress-growth.py
done
echo "all runs finished"
