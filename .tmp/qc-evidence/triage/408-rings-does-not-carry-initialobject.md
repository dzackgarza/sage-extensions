`Rings()` does not carry `initial_object`

`Rings().initial_object()` raises `AttributeError`; `initial_object` is written for `OwnedSemirings` (returning `NN`) and not for `OwnedRings`, so the initial ring `ZZ` cannot be named through the category that owns it.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_integers.sage::test_the_integers_are_the_initial_ring`
  `AttributeError: 'OwnedRings_with_category' object has no attribute '_structured_category'`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: `test_integers.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C05 of the triage in results/issue408-triage.md.
