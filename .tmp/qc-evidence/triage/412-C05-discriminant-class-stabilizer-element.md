C05: The stabilizer of a discriminant class is built through an element with no ambient category

`form.O().stabilizer(form.module_generator(0))` raises `AttributeError: 'OwnedJoinCategory.element_class[_GeneralPresentedElement]' object has no attribute 'inclusion'`. A user cannot take the stabilizer of a point of a discriminant form, the operation the whole divided-class machinery of the isotropic-orbit work is built on.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_orthogonal_group_of_a2.sage::test_the_stabilizer_of_a_discriminant_class`
  `AttributeError: 'OwnedJoinCategory.element_class[_GeneralPresentedElement]' object has no attribute 'inclusion'`

Defective call: the discriminant quadratic form's `O()` action and the element it is called with.

Introduced by: not bisected to a commit: the stabilizer test does not finish inside the per-step cap at the older trees. It fails at `14b9cc1` earlier, with `'OwnedJoinCategory.parent_class' object has no attribute 'domain'`, so the current failure is a later unmasking of the discriminant-form element's missing `inclusion`; the test has never been green on main.

Scope: the discriminant form's setwise stabilizer, so it reaches every stabilizer of a point of a discriminant group.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C05).
