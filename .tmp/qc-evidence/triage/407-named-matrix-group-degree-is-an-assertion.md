`Groups.GL(n, R)` refuses a fractional rank with an `AssertionError`, not a `ValueError`

`Groups.GL(QQ(5)/2, ZZ)` --- and every named matrix family --- is documented and tested to
raise `ValueError("degree must be an integer")`. It raises
`AssertionError: GL_n(R) needs a rank n that is an integer n >= 0, but got (5)/(2)` instead: a
public constructor validating a caller's argument with `assert`, which disappears under
`python -O` and gives a caller nothing to catch.

When this closes, `Groups.GL`, `Groups.Sp` and `Groups.SO` raise `ValueError` naming the
degree, and the three-family test below passes.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/group/groups.py:2445: in _general_linear_group
        assert degree in ZZ and degree == ZZ(degree) and degree >= 0, (
    E   AssertionError: GL_n(R) needs a rank n that is an integer n >= 0, but got (5)/(2)

## Failing test

- `tests/groups/test_free_and_catalogued_groups.sage::test_named_matrix_group_families_require_integral_degree`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): `git log -S 'GL_n(R) needs a rank n'`
over `groups.py` returns that commit alone, and the test that expects `ValueError` arrived at
`14b9cc1` the same day.
