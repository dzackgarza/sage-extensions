A direct sum is not an object of `DirectSumObjects(Lattices(ZZ))`

`L in DirectSumObjects(Lattices(ZZ))` answers false for a lattice built as a sum, so a user cannot test the decomposition it was constructed with.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_a1_plus_a2.sage::test_the_categories_of_a1_plus_a2`
  `assert: Integral lattice of rank 3 and signature (0, 3) in Category of objects of lattices with a chosen direct-sum decomposition`

The same defect also fails `tests/objects/test_two_hyperbolic_planes.sage::test_the_categories_of_u_plus_u`, in files that #412 now owns.

Defective call: /repos/sage-extensions/tests/objects/test_a1_plus_a2.sage:16.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: `test_a1_plus_a2.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C29 of the triage in results/issue408-triage.md.
