An isomorphism category does not carry `order`

`Isomorphisms(X, Y).order()` raises `AttributeError`, so the cardinality of the isomorphism set cannot be read as a group order.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_isomorphisms_of_a_two_element_set.sage::test_the_isomorphisms_are_the_automorphism_group`
  `AttributeError: 'FixedIsoCategory_with_category' object has no attribute 'order'`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_isomorphisms_of_a_two_element_set.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C10 of the triage in results/issue408-triage.md.
