C21: The owned quadratic field has no `gen`

`QuadraticField(-1, 'i').gen()` raises `AttributeError: 'Owned_OwnedAlgebraParent_with_category' object has no attribute 'gen'`, so the generator of a number field cannot be named -- and no Galois action can be written on it.

Failing tests on main `c8a3ced` (2026-11-14), one file per run in the published image:

- `tests/groups/test_profinite_collection_ownership.sage::test_galois_group_of_gaussian_rationals_is_generated_by_complex_conjugation`
  `AttributeError: 'Owned_OwnedAlgebraParent_with_category' object has no attribute 'gen'`
  at `tests/groups/test_profinite_collection_ownership.sage:18: in test_galois_group_of_gaussian_rationals_is_generated_by_complex_conjugation`

Defective call: the owned number-field parent (the object `QuadraticField(-1, 'i')` answers).

Introduced by: not bisected: the failure is reached through the field construction at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.

Scope: the generator of an owned number field; one test.

Triage record: `results/issue411-triage.md` (C21), slice of #411.
