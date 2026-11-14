The augmented simplex category's parent class does not carry `codomain`

A functor out of the augmented simplex category raises `AttributeError: 'AugmentedSimplexCategory.parent_class' object has no attribute 'codomain'`.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_free_module_of_rank_three.sage::test_the_module_category_applied_to_a_basis_set_agrees`
  `AttributeError: 'AugmentedSimplexCategory.parent_class' object has no attribute 'codomain'`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_free_module_of_rank_three.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C08 of the triage in results/issue408-triage.md.
