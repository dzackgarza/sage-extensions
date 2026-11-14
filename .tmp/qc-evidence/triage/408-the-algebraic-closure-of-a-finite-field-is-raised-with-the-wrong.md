The algebraic closure of a finite field is raised with the wrong constructor arity

`GF(p).algebraic_closure()` raises `TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'`, because the owned adapter calls Sage's `AlgebraicClosureFiniteField(base_ring, name)` with a characteristic. A user cannot take the algebraic closure of a finite field at all.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_field_construction_agrees`
  `TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/rings/ring_foundation.py:7608.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: `test_absolute_galois_group_of_f5.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: repaired in `?`, docstring in `23ae718`. In the image, `GF(5).absolute_galois_group()` raises `TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'` at ring_foundation.py:7608 on main `c8a3ced`, and returns an `AbsoluteGaloisGroupsOfFiniteFields` object with the repair. No failing test of the slice changes colour: its only test, `test_absolute_galois_group_of_f5.sage::test_the_field_construction_agrees`, reaches the call through the file's `galois()` helper, which names `AbsoluteGaloisGroup` -- C01 -- so it stays red until C01 is repaired.

Cause C03 of the triage in results/issue408-triage.md.
