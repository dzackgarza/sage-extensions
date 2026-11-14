C28: The lattice points of a polytope are a bare list

`polyhedron.lattice_points()` returns a Python `list`, so `...parent()` raises `AttributeError: 'list' object has no attribute 'parent'`. A list is not a mathematical object: the points of a polytope are a set of lattice points, and the session's rule is that they come from the category that owns them.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_standard_triangle.sage::test_the_lattice_points_of_the_triangle`
  `AttributeError: 'list' object has no attribute 'parent'`

Defective call: the lattice-points operation of the owned convex polytope.

Introduced by: not bisected to a commit: `git bisect` runs out of candidates it can evaluate (`We cannot bisect more!`). It fails at `14b9cc1` earlier, with `TypeError: Cannot create a consistent method resolution order (MRO) for the category graph`; the bare-list return is present at `c8a3ced`, and the test has never been green on main.

Scope: the one operation.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C28).
