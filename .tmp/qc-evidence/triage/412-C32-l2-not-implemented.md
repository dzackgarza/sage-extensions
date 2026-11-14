C32: `L2` and its categories are not implemented

`L2(R)` raises a bare `NotImplementedError`: the square-integrable functions on the line -- `L^2` as a Hilbert space, its inner product, and its Holder conjugation `L^2^* = L^2` -- are not implemented, so the analytic half of the function-module catalogue has no `L^2`.

Failing tests (4, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_square_integrable_functions.sage::test_l2_is_its_own_holder_conjugate`
  `NotImplementedError`
- `tests/objects/test_square_integrable_functions.sage::test_the_categories_of_l2`
  `NotImplementedError`
- `tests/objects/test_square_integrable_functions.sage::test_the_form_on_a_gaussian`
  `NotImplementedError`
- `tests/objects/test_square_integrable_functions.sage::test_l2_has_one_endomorphism_category`
  `NotImplementedError`

Defective call: the `L2` construction.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the `L2` family, four tests in this slice.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C32).
