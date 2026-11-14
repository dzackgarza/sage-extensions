The whole-algebra map of an infinite-rank free algebra is refused

`ValueError: the whole-algebra map for Free module on Coproduct ... over Fraction Field ...`, raised when the endomorphism category of a coordinate-ring algebra is formed.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_has_one_endomorphism_category`
  `ValueError: the whole-algebra map for Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring/(x) -> Free module on Coproduct of the family over NN = {0, 1, 2, ...} ove`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/algebras/algebras.py:4631.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_a_coordinate_line_in_the_affine_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C19 of the triage in results/issue408-triage.md.
