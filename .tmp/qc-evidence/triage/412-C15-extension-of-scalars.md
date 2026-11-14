C15: `Modules()` does not carry `extension_of_scalars`

`Modules().extension_of_scalars(...)` raises `AttributeError: 'Modules_with_category' object has no attribute 'extension_of_scalars'. Did you mean: 'coextension_of_scalars'?`. Extension of scalars is the adjoint the induction/coinduction tests are written against; with it missing, `Ind_ZZ^G` cannot be formed from the category that owns it.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_regular_module_of_c2.sage::test_the_induced_module_is_the_regular_module`
  `AttributeError: 'Modules_with_category' object has no attribute 'extension_of_scalars'. Did you mean: 'coextension_of_scalars'?`

Defective call: `Modules()` (`src/sage_extensions/categories/modules/pure/modules.py`): the operation is declared only in its co form.

Introduced by: `6c381ad` (2026-11-01, agent, "fix: export the group owner, and compare the Sterk archive table in one representation"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: type object 'Groups' has no attribute 'C'`.

Scope: the module category, so it reaches induced and extended modules throughout the suite.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C15).
