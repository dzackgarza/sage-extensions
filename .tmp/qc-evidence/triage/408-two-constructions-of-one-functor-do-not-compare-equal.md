Two constructions of one functor do not compare equal

`cone.apex_and_leg(...)` and the functor rebuilt from its data do not compare equal.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_apex_and_the_leg`
  `assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets`
- `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_apex_and_the_leg`
  `assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets`

Defective call: /repos/sage-extensions/tests/objects/test_cocone_under_a_one_object_diagram.sage:26, /repos/sage-extensions/tests/objects/test_cone_over_a_one_object_diagram.sage:26.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: `test_cocone_under_a_one_object_diagram.sage`, `test_cone_over_a_one_object_diagram.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C31 of the triage in results/issue408-triage.md.
