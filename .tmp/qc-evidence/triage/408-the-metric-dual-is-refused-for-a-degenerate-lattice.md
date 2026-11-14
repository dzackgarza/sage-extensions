The metric dual is refused for a degenerate lattice

`L.dual_lattice()` raises on the degenerate plane although the test asks for the radical; the refusal message states the form is degenerate, which is the hypothesis the caller is testing.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_degenerate_plane.sage::test_the_radical_is_the_line_through_e0_minus_e1`
  `AssertionError: Integral lattice of rank 2 and signature (1, 0) has no metric dual: the dual lattice is defined for a nondegenerate form, and Integral lattice of rank 2 and signature (1, 0) is not known to be nondege`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/lattices.py:6838.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_degenerate_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C18 of the triage in results/issue408-triage.md.
