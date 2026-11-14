definite_complement_extensions returns a bare tuple instead of an owned set

When this closes, `L.definite_complement_extensions(v, w)` returns the finite set of isometries
carrying `v` to `w`, so a user can ask it for its cardinality: the stabilizer of `e + f` in `U`
has two members, and the opposite coset two. Today the call returns a Python tuple, which has no
`cardinality`, so the count its own docstring describes is not reachable.

## Failing tests (red at `5f5fc25`, the current `main`)

```
tests/lattices/test_definite.sage::test_definite_complement_extensions_exhaust_the_u_vector_cosets
```

## Error

```
tests/lattices/test_definite.sage:403: in test_definite_complement_extensions_exhaust_the_u_vector_cosets
    assert stabilizer.cardinality() == 2
E   AttributeError: 'tuple' object has no attribute 'cardinality'
```

## Introducing commit

`_definite_complement_extensions` in `src/sage_extensions/categories/vector_orbits.py` returns a
tuple from the initial import `c731175` (Zack Garza, 2026-10-26); the assertion landed in the test
suite `14b9cc1` the same day. The failure is identical at `02d9657` (2026-10-28) and `441519c`
(2026-10-30), so the call has never returned an owned set on `main` and there is no pass-to-fail
commit to bisect to.

## Scope

`vector_orbits.py` and the public `Lattices.ElementMethods.definite_complement_extensions`; every
caller of the definite-complement torsor, including `binary_fixed_norm_representatives`.
