#!/bin/bash
# Each consumer file its own process, so one costly file cannot hide another's result.
set -uo pipefail
cd /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
for file in \
  tests/lattices/test_the_coble_incidence_of_line_and_plane_orbits.sage \
  tests/lattices/test_the_incidence_decided_by_divided_classes.sage \
  tests/lattices/test_a_row_computes_one_plane_covering.sage \
  tests/lattices/test_the_row_retains_no_transport_for_a_carried_line.sage \
  tests/lattices/test_the_incidence_line_vertex_is_named_by_the_finite_image.sage \
  tests/engineering/test_the_incidence_row_reports_a_broken_contract_apart_from_an_undecided_row.py \
  tests/lattices/test_special_orthogonal_split_building.sage \
  tests/lattices/test_orbit_milestones.sage \
  tests/lattices/test_the_kernel_incidence_rows.sage ; do
  name=$(basename "$file" .sage)
  WALL=1500 .tmp/issue598-ingress/launch-pytest.sh "consumer-$name" "$PWD" "$file" --durations=0 -q
done
echo "consumers finished"
