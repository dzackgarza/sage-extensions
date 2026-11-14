C26: Four tests evaluate an undecided-capable `Predicate` as a Python truth value

`assert is_finite(O(U + U))` raises `TypeError: the proposition is_finite(...) has no Python truth value, because it may be undecided; call ask(...)`. The library refuses the coercion by design, and the two questions the four tests state are not decided by their owners: whether `O` of an indefinite rank-four lattice and of its isotropic stabilizers is finite, and whether one lattice polygon is a subset of another. A user gets a `TypeError` where the mathematics has an answer.

Failing tests (4, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_two_hyperbolic_planes.sage::test_the_orthogonal_group_is_infinite`
  `TypeError: the proposition is_finite(Orthogonal group O(Integral lattice of rank 4 and signature (2, 2))) has no Python truth value, because it may be undecided; call ask(...) on it to get True, False or Unknown`
- `tests/objects/test_two_hyperbolic_planes.sage::test_an_isotropic_plane_and_its_stabilizer`
  `TypeError: the proposition is_finite({g in Orthogonal group O(Integral lattice of rank 4 and signature (2, 2)) : g(im(Generic morphism:`
- `tests/objects/test_two_hyperbolic_planes.sage::test_an_isotropic_flag_and_its_stabilizer`
  `TypeError: the proposition is_finite({g in Orthogonal group O(Integral lattice of rank 4 and signature (2, 2)) : g lies in every selected subgroup}) has no Python truth value, because it may be undecided; call ask(...) on it to get True, False or Unknown`
- `tests/objects/test_standard_triangle.sage::test_the_order_of_the_vertices_does_not_matter`
  `TypeError: the proposition is_subset(Lattice Polygon of dimension 2 with 3 vertices, Lattice Polygon of dimension 2 with 3 vertices) and is_subset(Lattice Polygon of dimension 2 with 3 vertices, Lattice Polygon of dimension 2 with 3 vertices) has no Python truth value, because it may be undecided; call ask(...) on it to get True, False or Unknown`

Defective call: `is_finite` of an owned orthogonal group, its stabilizers, and `is_subset` of two lattice polygons; the tests also spell the accessor as a Python truth value.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the two decision owners plus the four call sites; the repair is a decision in the library and `ask(...)` in the tests.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C26).
