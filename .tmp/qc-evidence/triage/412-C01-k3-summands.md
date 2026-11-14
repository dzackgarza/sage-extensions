C01: The K3 lattice does not carry its summands

`Lattices(ZZ)("K3").summands()` raises `AttributeError` on the lattice's parent class, so a user cannot ask a K3 lattice for the three hyperbolic planes and two E8 summands it is presented as; every decomposition-dependent computation (`L.summands()` block morphisms, the invariants that read them) is unavailable on the library's own named K3 specimen.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_k3_lattice.sage::test_the_invariants_of_the_k3_lattice`
  `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'summands'`

Defective call: `src/sage_extensions/categories/` -- the sparse free-module parent the K3 lattice is realized by carries no `summands`.

Introduced by: `9f5831e` (2026-10-26, D. Zack Garza, "Merge remote-tracking branch 'origin/main'"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'domain'`.

Scope: one call on one catalogue specimen; the repair is the parent-class operation, so it reaches every lattice presented as a direct sum.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C01).
