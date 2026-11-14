Module elements do not carry `is_isometric`

`L.is_isometric(M)` on the elements of an indefinite lattice's module raises `AttributeError` (the library writes `is_isometric` with no `_to`).

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_invariants_of_u`
  `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'is_isometric'. Did you mean: 'is_symmetric'?`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_hyperbolic_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C09 of the triage in results/issue408-triage.md.
