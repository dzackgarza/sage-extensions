`O(L)` of an indefinite lattice is refused

`AssertionError: cannot compute O(Integral lattice of rank 2 and signature (1, 1)) as a finite group: that computation is supplied for a definite lattice`, so `O(U)` has no arithmetic.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_orthogonal_group_of_u`
  `AssertionError: cannot compute O(Integral lattice of rank 2 and signature (1, 1)) as a finite group: that computation is supplied for a definite lattice of finite rank over ZZ, and Integral lattice of rank 2 and sign`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/lattice_morphisms.py:4531.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_hyperbolic_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C25 of the triage in results/issue408-triage.md.
