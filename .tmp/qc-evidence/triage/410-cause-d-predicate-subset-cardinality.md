A predicate subset of a finite group has no cardinality decision

When this closes, `S.condition_set(predicate).cardinality()` counts the members of a finite set
that satisfy a predicate, so `A2.Aut().condition_set(det == 1).cardinality()` is 6 — the rotations
of the hexagon — instead of an assertion that the construction supplies no value. Users of
`condition_set`, `Subset` and the other predicate slices of a finite set get a count rather than a
refusal.

## Failing tests (red at `c8a3cedb`, the current `main`)

```
tests/lattices/test_definite.sage::test_a2_discriminant_representation_is_onto_order_two_and_so_a2_has_order_6
```

## Error

```
src/sage_extensions/categories/sets/set_categories.py:2503: in cardinality
    assert construction_cardinality is not None, (
E   AssertionError: cannot compute the cardinality of Subset of Orthogonal group O(Integral lattice of
    rank 2 and signature (0, 2)) cut out by <lambda>: its construction supplies no exact value or decided
    finite enumeration (it is in Join of Category of finite sets and Category of facade sets and Category
    of finite countable sets)
```

`Sets().condition_set` takes the filtered finite-enumeration route only when the universe is both
provably finite and in `EnumeratedSets()`; a finite *group* is neither enumerated nor given a
cardinality decision by the fallback `_condition_set`, although its category says it is finite.

## Introducing commit

`d26db5d7` (Zack Garza, 2026-10-27), which added the `Sets().is_provably_finite(universe) and
universe in EnumeratedSets()` guard to `Sets().condition_set`; before it the call went straight to
`_filtered_ordered_set`. There is no observable pass-to-fail flip on `main` for this defect: at
`d26db5d7^` and at `d26db5d7` the test is red for an earlier cause
(`TypeError: CategoricalIsomorphism.__init__() missing 1 required positional argument:
'inverse_computation'` at `lattice_morphisms.py:914`, checked in the image at both commits), and the
cardinality refusal only becomes the visible failure once that is repaired. The guard's commit is
named from the code history, and the failure it produces is verified at `c8a3cedb`.

## Scope

The `Sets`/`SetSubobjectCategory` owner: a predicate slice with a finite ambient set, for every
caller and not only this test. The repair reaches beyond the definite-lattice slice.
