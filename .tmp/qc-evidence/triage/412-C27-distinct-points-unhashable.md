C27: A finite set of lattice points cannot be formed

`finite set of distinct points` raises `ValueError: cannot form a finite set of distinct points: equality of supplied unhashable elements is undecided` on the three vertices of the standard triangle, whose `__hash__` is refused by Python (`cannot use ... as a dict key`). A user cannot form the vertex set -- or any point set -- of a polytope.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_standard_triangle.sage::test_the_invariants_of_the_triangle`
  `ValueError: cannot form a finite set of distinct points: equality of supplied unhashable elements is undecided`

Defective call: the finite-set constructor over owned unhashable elements; the polytope's point class.

Introduced by: not bisected to a commit: `git bisect` runs out of candidates it can evaluate (`We cannot bisect more!`). It fails at `14b9cc1` earlier, with the same `MRO` `TypeError`; the message this cause reports is in the tree from the initial import `c731175` (2026-10-26, Zack Garza), and the test has never been green on main.

Scope: the finite-set constructor, so it reaches every set of owned elements that are not hashable.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C27).
