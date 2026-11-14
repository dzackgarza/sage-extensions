The embedding set Emb(L, M) has no cardinality decision

When this closes, `L.Emb(M).cardinality()` counts the lattice embeddings a user asks for, so
`A1.Emb(A2).cardinality()` is 6 — one per primitive image of the generator, the six roots of A2
— instead of an assertion that the construction supplies no value. The sibling `Isom(L, M)` set
already supplies its count through `_cardinality_decision`; `Emb` has no such decision.

## Failing tests (red at `c8a3cedb`, the current `main`)

```
tests/lattices/test_definite.sage::test_definite_target_embedding_mor_enumerates_all_a1_into_a2_roots
```

## Error

```
src/sage_extensions/categories/sets/set_categories.py:2503: in cardinality
    assert construction_cardinality is not None, (
E   AssertionError: cannot compute the cardinality of Emb(Integral lattice of rank 1 and signature (0, 1),
    Integral lattice of rank 2 and signature (0, 2)): its construction supplies no exact value or decided
    finite enumeration (it is in Join of Category of homsets of sets and Category of sets)
```

## Introducing commit

The assertion landed with the test suite in `14b9cc1` (Zack Garza, 2026-10-26, "Move the session
namespace and the mathematics test suite from research"). No commit on `main` ever gave `Emb` a
cardinality decision: the same assertion with the same text is the failure at `02d9657`
(2026-10-28), `441519c` (2026-10-30), `a0d9ad37` (2026-11-11) and `c8a3cedb`. `Isom`'s decision
sits at `lattice_morphisms.py:3660`; the `Emb` class defines none. This is a decision that was
never written, not a regression, and there is no pass-to-fail commit to bisect to.

## Scope

`src/sage_extensions/categories/lattice_morphisms.py` (the `Emb` realization) with the `Sets`
cardinality hook. Beyond this slice: every `Emb(L, M)` cardinality, not only the definite ones.
