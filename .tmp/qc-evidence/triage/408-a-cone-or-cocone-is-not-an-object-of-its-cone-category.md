A cone or cocone is not an object of its cone category

`cone in Cones(F)` and `cocone in Cocones(F)` answer false for the cone built by the category's own constructor.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_cocone_is_an_object_of_the_cocone_category`
  `assert: Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cocone category`
- `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_cone_is_an_object_of_the_cone_category`
  `assert: Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cone category`

Defective call: /repos/sage-extensions/tests/objects/test_cocone_under_a_one_object_diagram.sage:19, /repos/sage-extensions/tests/objects/test_cone_over_a_one_object_diagram.sage:19.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: `test_cocone_under_a_one_object_diagram.sage`, `test_cone_over_a_one_object_diagram.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C30 of the triage in results/issue408-triage.md.
