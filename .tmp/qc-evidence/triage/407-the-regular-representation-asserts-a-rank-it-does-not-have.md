The group-algebra test asserts rank 6 of a module that is free of rank 1

`QQ[G].regular_representation()` is `QQ[G]` as a left module over itself: free of rank 1, of
`QQ`-dimension 6. The test asserts `regular.module_rank() == 6` and gets 1, so the invariant
it means to state --- that the regular representation has `QQ`-dimension `|G|` --- is not the
one it states. When this closes the test states the `QQ`-dimension it means; `module_rank` is
right as it stands, and the library needs no change.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    assert regular.module_rank() == 6
    E   assert 1 == 6
    E    +  where 1 = Free module on {[1]} over Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring.module_rank

## Failing test

- `tests/groups/test_actual_group_algebra_modules.sage::test_the_invariants_of_the_regular_representation_of_s3_are_one_dimensional`

## Cause and introducing commit

The test arrived at `14b9cc1` (Zack Garza, 2026-10-26) with that assertion, and
`regular_representation` in the initial import `c731175` already answered the rank-1 free
module. The defect is the test's, and its repair is the assertion.
