C31: `C^k(X, Y)` refuses `RR` as a real vector space

`C^inf(R, R)` raises `C^k(X, Y) is a real vector space of maps, so Y must be a real vector space, but Real Field is not`. `RR` is the real line; the smooth functions on the line are the library's own catalogue entry and cannot be constructed.

Failing tests (5, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_smooth_functions_on_the_line.sage::test_the_constructions_of_smooth_functions_agree`
  `AssertionError: C^k(X, Y) is a real vector space of maps, so Y must be a real vector space, but Real Field is not`
- `tests/objects/test_smooth_functions_on_the_line.sage::test_the_categories_of_smooth_functions`
  `AssertionError: C^k(X, Y) is a real vector space of maps, so Y must be a real vector space, but Real Field is not`
- `tests/objects/test_smooth_functions_on_the_line.sage::test_there_are_continuum_many_smooth_functions`
  `AssertionError: C^k(X, Y) is a real vector space of maps, so Y must be a real vector space, but Real Field is not`
- `tests/objects/test_smooth_functions_on_the_line.sage::test_evaluating_a_gaussian`
  `AssertionError: C^k(X, Y) is a real vector space of maps, so Y must be a real vector space, but Real Field is not`
- `tests/objects/test_smooth_functions_on_the_line.sage::test_smooth_functions_have_one_endomorphism_category`
  `AssertionError: C^k(X, Y) is a real vector space of maps, so Y must be a real vector space, but Real Field is not`

Defective call: the codomain check of `C^k(X, Y)` in `src/sage_extensions/categories/functions/`.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the check, so it reaches every `C^k` and the function-module tests built on it.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C31).
