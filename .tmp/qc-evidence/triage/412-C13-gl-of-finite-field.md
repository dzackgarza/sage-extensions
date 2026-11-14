C13: `GL` of a finite field is refused as a matrix group

`GL(ZZ/3)` raises `GL(Integer Ring / Ideal (3) of Integer Ring) is realized as a matrix group only for a free module with a finite selected basis`: a finite field is a one-dimensional free module over itself, so the refusal is wrong and `GL(F_3) = F_3^x` cannot be constructed.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_prime_field_f3.sage::test_the_automorphisms_of_f3`
  `AssertionError: GL(Integer Ring / Ideal (3) of Integer Ring) is realized as a matrix group only for a free module with a finite selected basis, but Integer Ring / Ideal (3) of Integer Ring is in Join of Category of finite fields and Category of quotient rings and Category of prime fields and Category of commutative algebras and Category of modules over Integer Ring / Ideal (3) of Integer Ring`

Defective call: `GL` of an owned module over an owned field.

Introduced by: `365abfb` (2026-11-08, D. Zack Garza, "fix: Retain finite module automorphism decisions at the group owner"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AssertionError: cannot compute the cardinality of the group Aut_Category of modules over Integer Ring(Integer Ring / Ideal (3) of Integer Ring): it is not known to be finite, it has no c`.

Scope: the matrix-group realization test, so it reaches `GL`/`SL`/`PGL` of every non-free or quotient carrier.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C13).
