`Modules(R)(X)` for a set dies on `scalar_action.codomain()`

`Modules(R)(n)` builds the free module of rank `n`, so a caller reading the same constructor
passes a finite set and gets an `AttributeError` from inside the constructor instead of the
free module on that set:

    AttributeError: 'FiniteOrderedSets.parent_class' object has no attribute 'codomain'

When this closes, `Modules(R)(X)` for an object of `Sets` is the free module on `X` --- the
one-point module the group-algebra tests use for the trivial and sign lines --- and the
group-algebra and `G`-object tests below run.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/modules/pure/modules.py:497: in _call_
        module = scalar_action.codomain().domain()

The branch handles an integer rank (`Modules(R)(n)`) and a scalar action `rho: R -> End(X)`; a
set is neither and is taken for `rho`.

## Failing tests

- `tests/groups/test_actual_group_algebra_modules.sage::test_q_splits_c2_but_the_splitting_field_of_c3_is_quadratic`
- `tests/groups/test_actual_group_algebra_modules.sage::test_sign_and_trivial_actions_coincide_after_base_change_to_characteristic_two`
- `tests/groups/test_actual_group_algebra_modules.sage::test_the_integral_sign_representation_has_no_invariants_and_coinvariants_z_mod_2`
- `tests/groups/test_g_objects.sage::test_the_averaging_operator_of_s3_squares_to_six_times_itself_and_kills_augmentation`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): `module =
scalar_action.codomain().domain()` is that commit's line, per `git log -S`. No commit on
`main` has these tests green.
