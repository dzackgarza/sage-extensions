C02: The owned ring adapter has no constructor for the symbolic ring

Any construction whose coefficient ring is `SR` -- `LaurentPolynomialRing(SR)`, the `SincTranslates` family, the character and translate families built over it -- raises `TypeError: cannot raise Symbolic Ring through an owned ring constructor`. A user cannot build the symbolic-coefficient rings the session namespace publishes names for.

Failing tests (6, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_laurent_monomials.sage::test_the_monomials_are_indexed_by_the_integers`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_laurent_monomials.sage::test_the_categories_of_the_laurent_monomials`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_laurent_monomials.sage::test_the_laurent_monomials_multiply_by_adding_exponents`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_sinc_translates.sage::test_the_translates_are_indexed_by_the_integers`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_sinc_translates.sage::test_the_categories_of_the_sinc_translates`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_sinc_translates.sage::test_the_translates_are_countably_many_and_distinct`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`

Defective call: `src/sage_extensions/categories/rings/ring_foundation.py:7534`, the owned ring constructor table, has no entry for `SR`.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the owned ring adapter, so it reaches every slice that builds a ring over `SR`: six tests here and #408's twelve. This is one defect with #408's cause C02 -- file one issue, not two.

Repair: filed; the same defect as #408's cause C02. Evidence: still red at `415c2b4` (`test/laurent_monomials` 3 failed, `test_sinc_translates` 3 failed).

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C02).
