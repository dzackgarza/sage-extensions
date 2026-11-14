`Sets(G)` is not a category of `G`-sets, and the group-adjunction tests call it

`Sets(group)` --- how both adjunction tests of `test_group_adjunctions.sage` build the
`C_2`-set they act on --- dies while the category is being made:

    TypeError: Category.__init__() takes 1 positional argument but 2 were given

The owned `Sets` is not a parameterized category: it has `_call_(self, source)` and no
`__classcall__`, so a call with an argument is read as a category-with-parameters and falls
into Sage's `Category.__init__`. When this closes, the `G`-set of a group is named by the
category that owns it (`FiniteGSets(G)`) --- or `Sets(G)` becomes that parameterized category
--- and the two adjunctions' unit and counit are checked.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    tests/groups/test_group_adjunctions.sage:10: in _swap_two_of_three
        acted = Sets(group)(Sets()((ZZ(0), ZZ(1), ZZ(2))), lambda g, p: ...)
    sage/categories/category.py:465: in __classcall__
    TypeError: Category.__init__() takes 1 positional argument but 2 were given

## Failing tests

- `tests/groups/test_group_adjunctions.sage::test_orbits_and_fixed_points_are_adjoint_to_the_trivial_action`
- `tests/groups/test_group_adjunctions.sage::test_the_free_and_cofree_g_sets_are_adjoint_to_the_underlying_set`

## Cause and introducing commit

The test arrived at `14b9cc1` (Zack Garza, 2026-10-26), and `Sets` has no `__classcall__` in
any commit (`git log -S 'def __classcall__'` over
`src/sage_extensions/categories/sets/set_categories.py` is empty), so this pair has never been
green on `main`.

The defect is the test's: the library's category of `G`-sets is `FiniteGSets(G)`, and the
repair is the test's call.
