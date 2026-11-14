C30: `toric_variety()` demands a base ring the polytope already knows

`TypeError: ConvexPolytopes.Integral.ParentMethods.toric_variety() missing 1 required positional argument: 'base_ring'`: an integral polytope's toric variety is over `ZZ` when nothing else is said, and the operation is written so that `P.toric_variety()` -- the only call the mathematics needs -- is refused.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_standard_triangle.sage::test_the_toric_variety_of_the_triangle_is_the_projective_plane`
  `TypeError: ConvexPolytopes.Integral.ParentMethods.toric_variety() missing 1 required positional argument: 'base_ring'`

Defective call: `toric_variety` of an owned integral polytope.

Introduced by: not bisected to a commit: `git bisect` runs out of candidates it can evaluate (`We cannot bisect more!`). It fails at `14b9cc1` earlier, with the same `MRO` `TypeError`; `def toric_variety(self, base_ring, ...)` is in the initial import `c731175` (2026-10-26, Zack Garza), so the required argument has been on the operation all along.

Scope: the one operation.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C30).
