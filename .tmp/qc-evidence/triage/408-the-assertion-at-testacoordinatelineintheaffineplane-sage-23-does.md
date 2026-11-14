The assertion at `test_a_coordinate_line_in_the_affine_plane.sage:23` does not hold: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction 

The proposition asserted at `/repos/sage-extensions/tests/objects/test_a_coordinate_line_in_the_affine_plane.sage:23` is false on main: `Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction `. The test states the contract; the construction it names does not meet it.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_categories_of_the_axis`
  `assert: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring defined by x in Category of smooth schemes over Fraction Field of In`

Defective call: /repos/sage-extensions/tests/objects/test_a_coordinate_line_in_the_affine_plane.sage:23.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_a_coordinate_line_in_the_affine_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C32 of the triage in results/issue408-triage.md.
