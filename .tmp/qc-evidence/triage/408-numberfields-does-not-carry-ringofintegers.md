`NumberFields()` does not carry `ring_of_integers`

`NumberFields().ring_of_integers()(QQ)` raises `AttributeError`; the functor that sends a number field to its ring of integers is not published on the category.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_integers.sage::test_the_integers_are_the_ring_of_integers_of_the_rationals`
  `AttributeError: 'NumberFields_with_category' object has no attribute 'ring_of_integers'`

Defective call: /repos/sage-extensions/tests/objects/test_integers.sage:13.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: `test_integers.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C11 of the triage in results/issue408-triage.md.
