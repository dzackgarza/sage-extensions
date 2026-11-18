#!/bin/bash
# The two kernel incidence rows of T_Co, one process a row: each row's cusp row is
# retained for its subgroup (the two subgroups are distinct objects), so two rows in
# one process is their two rows at once against the 6144 MiB guard.
set -uo pipefail
cd /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
for row in Otilde Otilde+; do
  WALL=14400 PEAKRSS_LIMIT_MIB=6144 .tmp/issue381-rows/launch.sh "$row" \
      --rows "$row" --lattice Tco --route divided-class
  echo "$row: launcher done, exit $?" >> .tmp/issue381-rows/order.log
done
echo "both rows finished" >> .tmp/issue381-rows/order.log
