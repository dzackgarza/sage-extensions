C17: The base-category class of `Modules.FinitelyGenerated` mismatches its own class

Taking the underlying integral module of a group-algebra module raises `base category class for Modules.FinitelyGenerated mismatch; expected Modules, got ModulesOverGroupAlgebra`. The axiom class of a joined module category does not agree with the class of its base category, so the object cannot be re-placed in its own parent.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_regular_module_of_c2.sage::test_the_underlying_integral_module`
  `AssertionError: base category class for <class 'sage_extensions.categories.modules.pure.modules.Modules.FinitelyGenerated'> mismatch; expected <class 'sage_extensions.categories.modules.pure.modules.Modules'>, got <class 'sage_extensions.categories.modules.group_modules.group_modules.ModulesOverGroupAlgebra'>`

Defective call: the base-category class resolution in `src/sage_extensions/categories/modules/pure/modules.py`.

Introduced by: `6c381ad` (2026-11-01, agent, "fix: export the group owner, and compare the Sterk archive table in one representation"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: type object 'Groups' has no attribute 'C'`.

Scope: the category-class resolution, so it reaches every joined module category.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C17).
