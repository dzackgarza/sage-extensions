`RingMorphism._engine_is_identity` asks a coercion map for `is_identity`

Composing two ring morphisms --- what every `candidate_closure * candidate_base` in the
absolute Galois group does --- raises instead of composing:

    AttributeError: 'sage.structure.coerce_maps.DefaultConvertMap_unique' object has no attribute 'is_identity'

When this closes, `f * g` for ring maps whose private engine realization is a coercion map
composes, and the normalizer, extension-coset and quotient computations of `profinite/`
return.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/rings/ring_foundation.py:173: in __mul__
        other._engine_morphism is not None and other._engine_is_identity()
    src/sage_extensions/categories/rings/ring_foundation.py:241: in _engine_is_identity
        return bool(self._engine_morphism.is_identity())

`is_identity` is a method of some Sage maps and not of others: `Map` does not define it, and
the value here is a `DefaultConvertMap_unique`.

## Failing tests

- `tests/groups/test_absolute_galois.sage::test_the_core_of_the_subgroup_fixing_the_real_cube_root_of_two_has_index_six`
- `tests/groups/test_galois_extension_coset_archive.sage::test_complex_conjugation_of_q_i_extends_to_sigma_7_and_sigma_11`
- `tests/groups/test_galois_normalizer_archive.sage::test_the_real_cube_root_of_two_has_no_nontrivial_automorphisms`
- `tests/groups/test_galois_quotient_archive.sage::test_the_automorphisms_of_q_zeta_12_act_on_i_and_root_three_by_their_exponent`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, *Initial import of the mathematical library from
dzack-research's preamble*): `git log -S 'bool(self._engine_morphism.is_identity())'` over
`ring_foundation.py` returns that commit alone. The tests arrived at `14b9cc1` the same day,
and at that commit the same `AttributeError` is the first failure of
`test_galois_normalizer_archive.sage`
(`.tmp/qc-evidence/issue407-legacy-14b9cc1-summary.log`), so no commit on `main` carries
these tests green.
