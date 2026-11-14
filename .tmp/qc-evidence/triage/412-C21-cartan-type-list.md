C21: `CartanType` is called with a list

`Lattices(ZZ)(CartanType(["A", 2]))` raises `ValueError: ['A', 2] is not a valid Cartan type`: the test writes the Dynkin symbol the way the library's own docstrings do, and the constructor accepts only another spelling, so the named root lattices cannot be reached from their Cartan type.

Failing tests (2, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_root_lattice_a2.sage::test_the_root_system_construction_agrees`
  `ValueError: ['A', 2] is not a valid Cartan type`
- `tests/objects/test_root_lattice_e8.sage::test_the_root_system_construction_agrees`
  `ValueError: ['E', 8] is not a valid Cartan type`

Defective call: the `CartanType` argument handling reached from the lattice catalogue.

Introduced by: `39d3db4` (2026-11-08, D. Zack Garza, "feat: Stabilize and transport non-isotropic and nonprimitive sublattices"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `TypeError: category() needs an argument`.

Scope: the Cartan-type constructor, so it reaches every root lattice built from its diagram.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C21).
