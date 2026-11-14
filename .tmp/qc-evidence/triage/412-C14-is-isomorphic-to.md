C14: Owned objects do not carry `is_isomorphic_to`

`X.is_isomorphic_to(Y)` raises `AttributeError: '...parent_class' object has no attribute 'is_isomorphic_to'. Did you mean: 'is_isomorphic'?` on schemes, free modules, group modules and isomorphism categories. The test surface and the library disagree on the name of one decision, so a user writing the session-standard spelling gets an `AttributeError` where an isomorphism proposition is expected.

Failing tests (6, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_projective_plane_over_qq.sage::test_the_projective_plane_is_glued_from_its_charts`
  `AttributeError: 'Schemes.parent_class' object has no attribute 'is_isomorphic_to'. Did you mean: 'is_isomorphic'?`
- `tests/objects/test_projective_plane_over_qq.sage::test_the_standard_affine_charts`
  `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'is_isomorphic_to'. Did you mean: 'is_isomorphic'?`
- `tests/objects/test_projective_plane_over_qq.sage::test_the_picard_group_and_the_canonical_bundle`
  `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'is_isomorphic_to'`
- `tests/objects/test_regular_module_of_c2.sage::test_the_permutation_module_is_the_regular_module`
  `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'is_isomorphic_to'`
- `tests/objects/test_regular_module_of_c2.sage::test_the_coinduced_module_is_the_regular_module`
  `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'is_isomorphic_to'`
- `tests/objects/test_symmetric_group_s3.sage::test_the_automorphisms_of_a_three_element_set`
  `AttributeError: 'FixedIsoCategory_with_category' object has no attribute 'is_isomorphic_to'`

Defective call: the owned parent and element classes (`is_isomorphic` exists on some owners and the tests call `is_isomorphic_to` throughout).

Introduced by: `6c381ad` (2026-11-01, agent, "fix: export the group owner, and compare the Sterk archive table in one representation"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: type object 'Groups' has no attribute 'C'`.

Scope: the name of the isomorphism decision across the library, so the scope is every parent and element class that decides isomorphism; this slice's six tests are schemes (3), group modules (2) and an isomorphism category (1).

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C14).
