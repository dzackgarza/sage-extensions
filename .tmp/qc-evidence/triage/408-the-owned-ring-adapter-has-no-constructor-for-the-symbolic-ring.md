The owned ring adapter has no constructor for the symbolic ring

Any construction whose coefficient ring is `SR` -- `PolynomialRing(SR)`, `LaurentPolynomialRing(SR)`, the character and translate families built over it -- raises `TypeError: cannot raise Symbolic Ring through an owned ring constructor` from `_owned_engine_ring`. A user cannot build the symbolic-coefficient rings the session namespace publishes names for.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_fourier_characters.sage::test_the_characters_are_indexed_by_the_integers`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_fourier_characters.sage::test_the_categories_of_the_characters`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_fourier_characters.sage::test_the_characters_are_countably_many_and_distinct`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_hermite_polynomials.sage::test_the_polynomials_are_indexed_by_the_naturals`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_hermite_polynomials.sage::test_the_categories_of_the_hermite_polynomials`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_hermite_polynomials.sage::test_the_hermite_polynomials`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`

The same defect also fails `tests/objects/test_laurent_monomials.sage::test_the_monomials_are_indexed_by_the_integers`, `tests/objects/test_laurent_monomials.sage::test_the_categories_of_the_laurent_monomials`, `tests/objects/test_laurent_monomials.sage::test_the_laurent_monomials_multiply_by_adding_exponents`, `tests/objects/test_sinc_translates.sage::test_the_translates_are_indexed_by_the_integers`, `tests/objects/test_sinc_translates.sage::test_the_categories_of_the_sinc_translates`, `tests/objects/test_sinc_translates.sage::test_the_translates_are_countably_many_and_distinct`, in files that #412 now owns.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/rings/ring_foundation.py:7534.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: `test_fourier_characters.sage`, `test_hermite_polynomials.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C02 of the triage in results/issue408-triage.md.
