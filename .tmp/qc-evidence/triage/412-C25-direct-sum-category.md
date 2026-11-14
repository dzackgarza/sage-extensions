C25: A direct sum is not an object of the decomposition category

`U + U` is not in `Category of objects of lattices with a chosen direct-sum decomposition`, although it was built as the direct sum of two hyperbolic planes. A user cannot treat a direct sum as a decomposed lattice, so the block-morphism machinery that reads the decomposition is unreachable from `+`.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_two_hyperbolic_planes.sage::test_the_categories_of_u_plus_u`
  `assert Integral lattice of rank 4 and signature (2, 2) in Category of objects of lattices with a chosen direct-sum decomposition`

Defective call: the direct-sum construction's category placement for lattices.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the direct-sum constructor, so it reaches every `L + M`.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C25).
