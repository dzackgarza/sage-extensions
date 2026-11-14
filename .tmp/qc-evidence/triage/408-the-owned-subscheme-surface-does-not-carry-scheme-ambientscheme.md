The owned subscheme surface does not carry `scheme`/`ambient_scheme`

A subscheme's `scheme()` and `ambient_scheme()` are absent from the owned subscheme parent (and its element class), so a user cannot ask a closed subscheme or a Cartier divisor which scheme it sits in.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_a_closed_subscheme_of_codimension_one`
  `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'ambient_scheme'`
- `tests/objects/test_divisors_on_three_points.sage::test_the_cartier_divisor_group_on_three_points`
  `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'scheme'`

Defective call: sage/cpython/getattr.pyx:357, sage/cpython/getattr.pyx:362.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: `test_a_coordinate_line_in_the_affine_plane.sage`, `test_divisors_on_three_points.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C06 of the triage in results/issue408-triage.md.
