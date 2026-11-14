The assertion at `test_integers.sage:28` does not hold: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring

The proposition asserted at `/repos/sage-extensions/tests/objects/test_integers.sage:28` is false on main: `Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring`. The test states the contract; the construction it names does not meet it.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_integers.sage::test_the_integers_as_an_algebra_over_themselves`
  `assert: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring`

Defective call: /repos/sage-extensions/tests/objects/test_integers.sage:28.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: `test_integers.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C35 of the triage in results/issue408-triage.md.
