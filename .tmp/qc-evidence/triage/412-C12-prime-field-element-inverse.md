C12: An element of `ZZ/3` carries no `inverse`

`(ZZ/3)(2).inverse()` raises `AttributeError: 'OwnedJoinCategory.element_class' object has no attribute 'inverse'`. In a field every nonzero element is invertible, and the library's prime-field element does not offer the operation, so no linear algebra over its own `F_3` can divide.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_prime_field_f3.sage::test_the_arithmetic_of_f3`
  `AttributeError: 'OwnedJoinCategory.element_class' object has no attribute 'inverse'`

Defective call: the owned element class of a prime field.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the field element's inverse, so it reaches every computation over an owned finite field.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C12).
