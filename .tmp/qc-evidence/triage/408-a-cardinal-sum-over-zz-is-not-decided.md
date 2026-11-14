A cardinal sum over `ZZ` is not decided

`AssertionError: cannot decide whether the cardinal sum_{i in Integer Ring} kappa_i is finite`, raised while the centre of an exterior algebra is formed.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_centre_of_the_exterior_algebra`
  `AssertionError: cannot decide whether the cardinal sum_{i in Integer Ring} kappa_i is finite: it is not a finite sum, product, or supremum of known cardinals`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/sets/cardinals.py:732.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_exterior_algebra_of_qq2.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C21 of the triage in results/issue408-triage.md.
