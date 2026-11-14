The owned algebraic closure of a prime field is never built: `AlgebraicClosureFiniteField` is called without its base field

A session that asks for the algebraic closure of a prime field --- through
`GF(p).absolute_galois_group()`, a cyclotomic or Kummer character of a finite field, or any
Galois quotient stage --- raises before it computes anything:

    TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'

The closure is what carries every finite-field computation in the absolute Galois group, so
the whole finite-field side of `profinite/` is unusable. When this closes,
`_owned_algebraic_closure_finite_field(p)` returns the one owned closure of `F_p`, and the
tests below reach the mathematics they state.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/rings/ring_foundation.py:7608: TypeError
    engine = AlgebraicClosureFiniteField(int(characteristic))

`AlgebraicClosureFiniteField(base_ring, name, category=None, implementation=None)` takes both
the field it closes and the name of its primitive elements; it has no one-argument form
(`sage/rings/algebraic_closure_finite_field.py`, whose docstring recommends
`GF(p).algebraic_closure()`).

## Failing tests

- `tests/groups/test_absolute_galois.sage::test_cyclotomic_and_kummer_characters_of_finite_fields_take_their_frobenius_values`
- `tests/groups/test_absolute_galois.sage::test_open_subgroups_of_the_absolute_galois_group_of_f5_follow_the_degrees`
- `tests/groups/test_absolute_galois.sage::test_the_frobenius_of_f625_restricts_to_that_of_f25_with_two_extensions`
- `tests/groups/test_absolute_galois.sage::test_the_frobenius_of_f9_raises_to_the_ninth_power_and_fixes_f9`
- `tests/groups/test_absolute_galois_category_archive.sage::test_every_finite_quotient_of_the_galois_group_of_f5_is_cyclic_generated_by_frobenius`
- `tests/groups/test_absolute_galois_category_archive.sage::test_the_frobenius_of_f25_is_the_25th_power_not_the_fifth`
- `tests/groups/test_absolute_galois_element_archive.sage::test_frobenius_restricts_to_the_generator_of_gal_f25_over_f5`
- `tests/groups/test_absolute_galois_subgroups_elements_archive.sage::test_the_subgroup_fixing_f25_is_normal_of_index_two`
- `tests/groups/test_absolute_galois_subgroups_elements_archive.sage::test_the_subgroups_fixing_f25_and_f125_meet_in_index_six`
- `tests/groups/test_field_absolute_galois_archive.sage::test_the_frobenius_of_f7_generates_every_finite_quotient`
- `tests/groups/test_galois_characters_archive.sage::test_the_mod_three_cyclotomic_character_of_f5_factors_through_f25`
- `tests/groups/test_galois_characters_archive.sage::test_the_quadratic_character_of_two_over_f5_has_kernel_of_index_two`
- `tests/groups/test_galois_quotient_archive.sage::test_restriction_to_f625_has_kernel_of_index_four_containing_frobenius_to_the_fourth`
- `tests/groups/test_galois_quotient_archive.sage::test_the_frobenius_of_f25_has_exactly_two_extensions_to_f625`

## Cause and introducing commit

The two-argument call is absent from every commit. The one-argument form first appears in
`544d940` (Zack Garza, 2026-10-26, *Sync library edits from research origin/main
1b35ddc83c*), inside `_owned_engine_ring`:

    case AlgebraicClosureFiniteField_generic():
        characteristic = int(engine.characteristic())
        closure = AlgebraicClosureFiniteField(characteristic)

`6a42c22` (D. Zack Garza, 2026-10-26, *Intern algebraic closures by characteristic
construction*) moved that same call into its own cached function, where it now sits. `git log
-S` on the offending call returns those two commits and no other.

No commit on `main` carries these tests green. At `14b9cc1` (2026-10-26), the commit that
brought `tests/groups` into this repository, the same `KeyError` cascade out of the closure is
already the first failure of `test_galois_quotient_archive.sage`
(`.tmp/qc-evidence/issue407-legacy-14b9cc1-summary.log`).

## Repaired by

`main`'s `23ae718` (#408, *State why the closure is raised through the field, not the
constructor*): the closure is `SageGF(p).algebraic_closure()`, the field's own operation,
which is also what this workstream's `4706e99` and its replacement `525dd1b` reached; the
merge of `8755b95` keeps main's wording of the reason and this branch's other repair.  The
raw constructor is no longer called at all, so the one-argument call this cause names is
gone from the tree.

No test in this list flips on that repair alone, and that is not hidden: with the closure
constructible the same calls reach the next defect on the same path,
`RingMorphism._engine_is_identity` asking a coercion map for `is_identity`
(`.tmp/qc-evidence/triage/407-engine-identity-asks-a-coercion-map.md`, repaired by
`fa7553e`/`c17910a` in this workstream), and that is where they now stop.  The run that
shows both: `issue407-repair6.log`.
