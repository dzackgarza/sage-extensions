C34: `module_rank` refuses a module over a non-field base

`the centre of the tensor algebra`: `the rank of Fraction Field of Integer Ring over Integer Ring is computed over a finite field for a finite module, or from a chosen basis or presentation, and Fraction Field of Integer Ring supplies none of these`. `QQ` is a field and the free module of rank one over `ZZ` has rank one; a user cannot ask for the rank over `ZZ`.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_tensor_algebra_of_qq2.sage::test_the_centre_of_the_tensor_algebra`
  `AssertionError: the rank of Fraction Field of Integer Ring over Integer Ring is computed over a finite field for a finite module, or from a chosen basis or presentation, and Fraction Field of Integer Ring supplies none of these`

Defective call: `module_rank` of an owned module over an owned ring.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the rank operation, so it reaches every rank over a non-field base ring.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C34).
