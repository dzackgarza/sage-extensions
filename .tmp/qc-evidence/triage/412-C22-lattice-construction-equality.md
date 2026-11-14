C22: Two constructions of one lattice do not compare equal

`Lattices(ZZ)("A2") == Lattices(ZZ)([[-2, 1], [1, -2]])` is `False`, and so is the K3/`E8` catalogue entry against its Gram matrix and `U + U` against the block Gram. A user cannot compare the named specimen with the lattice they built, which is the only way to check that a catalogue entry is the lattice it claims.

Failing tests (3, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_root_lattice_a2.sage::test_the_named_and_the_gram_constructions_agree`
  `assert Integral latt...gnature (0, 2) == Integral latt...gnature (0, 2)`
- `tests/objects/test_root_lattice_e8.sage::test_the_catalogue_entry_agrees`
  `assert Integral latt...gnature (0, 8) == Integral latt...gnature (0, 8)`
- `tests/objects/test_two_hyperbolic_planes.sage::test_the_sum_and_the_block_gram_agree`
  `assert Integral latt...gnature (2, 2) == Integral latt...gnature (2, 2)`

Defective call: the lattice equality of the owned integral lattice parent.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: integral lattice equality, so it reaches every catalogue row and every isometry test written as an equality.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C22).
