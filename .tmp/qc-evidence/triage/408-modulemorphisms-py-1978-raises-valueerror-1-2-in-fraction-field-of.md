`module_morphisms.py:1978` raises ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:

The call at `/repos/sage-extensions/src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1978` raises `ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:`. A user reaching that operation through the public API gets the exception instead of the documented object.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_discriminant_quadratic_form_of_a1.sage::test_the_brown_invariant_of_q_a1`
  `ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1978.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_discriminant_quadratic_form_of_a1.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C34 of the triage in results/issue408-triage.md.
