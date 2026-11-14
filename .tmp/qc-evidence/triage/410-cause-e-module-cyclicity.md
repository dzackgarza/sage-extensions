A module states no cyclicity, so discriminant_group().is_cyclic() does not exist

When this closes, a module answers `is_cyclic()`: the discriminant group of `A1 + A2` is cyclic of
order 6, the discriminant group of `A2` is cyclic of order 3, and a user reading a finite abelian
group off a lattice gets its structure instead of an `AttributeError`. The operation is asked for
by this test and by `tests/rings/test_unit_group_functor.sage`; today the name occurs nowhere in
`src/`.

## Failing tests (red at `c8a3cedb`, the current `main`)

```
tests/lattices/test_definite.sage::test_discriminant_group_of_a1_plus_a2_is_cyclic_of_order_6
```

## Error

```
sage/cpython/getattr.pyx:362: in __getattr__
    ???
E   AttributeError: 'OwnedJoinCategory.parent_class[_PresentedModule].ObjectType' object has no attribute 'is_cyclic'
```

## Introducing commit

No commit introduced it: `git log -S'is_cyclic' -- src/` is empty over the whole history, so the
library has never had the operation, while the assertion landed with the test suite in `14b9cc1`
(Zack Garza, 2026-10-26). The same `AttributeError` is the failure at `441519c` (2026-10-30) and
`a0d9ad37` (2026-11-11), so there is no pass-to-fail commit. The cause is a missing public
operation, not a regression.

## Scope

The module catalogue owner — `is_cyclic` for a module over a ring — which reaches every module and
not only the discriminant groups of lattices. The repair reaches beyond this slice.
