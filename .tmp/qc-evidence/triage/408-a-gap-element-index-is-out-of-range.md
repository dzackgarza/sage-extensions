A GAP element index is out of range

`IndexError: index out of range` from GAP while the isotropic lines of `U` are enumerated.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_isotropic_lines_of_u`
  `IndexError: index out of range.`

Defective call: sage/libs/gap/element.pyx:3170.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_hyperbolic_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C24 of the triage in results/issue408-triage.md.
