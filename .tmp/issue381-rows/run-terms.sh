#!/bin/bash
# Three arms, one process each: the split gathered as the row does, the split
# dropped as the cusp row needs it, and the contract step over a thousand cusps.
set -uo pipefail
cd /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
for mode in gather drop contract; do
  PROBE_MODE=$mode WALL=1800 PEAKRSS_LIMIT_MIB=6144 \
    .tmp/issue381-rows/launch-probe.sh "term-$mode" .tmp/issue381-rows/probe-terms.py \
    >> .tmp/issue381-rows/terms-order.log 2>&1
  echo "$mode: launcher exit $?" >> .tmp/issue381-rows/terms-order.log
done
echo "the three arms finished" >> .tmp/issue381-rows/terms-order.log
