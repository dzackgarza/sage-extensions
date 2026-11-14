C06: The kernel of the de Rham differential is refused

`kernel(...)` on the map `Omega^0_{A^1} -> Omega^1_{A^1}` raises `cannot compute the kernel of Free module on {[0]} over Free module on Coproduct of the family over NN ...`: the module morphism refuses its own kernel. A user cannot compute de Rham cohomology of the affine line, the smallest case of the cohomology the function-module catalogue is for.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_polynomial_ring_qq_x.sage::test_the_de_rham_cohomology_of_the_affine_line`
  `AssertionError: cannot compute the kernel of Free module on {[0]} over Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring restricted to Fraction Field of Integer Ring along Generic morphism:`

Defective call: `src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1481`, the kernel of a module morphism.

Introduced by: `c546077` (2026-11-01, D. Zack Garza, "Publish completed issue 614 repairs, retained torsion-form hashes, and subgroup-action tests"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `TypeError: AdditiveMorphism.__init__() got an unexpected keyword argument 'evaluator'`.

Scope: the kernel of a module morphism, so it reaches every cohomology computation built on it.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C06).
