# #339: the admitted member is coerced before the record that answers the coercion

**Result: repaired at the owner that coerces.** `NamedLattices.TEn.O().discriminant_image()`
and `NamedLattices.Tco.Aut().group_generators()` return again, #333's test passes, #287's
test passes and so do its neighbours.

Measured on `6db8551ae90d45bcc9f11881fee4432fbc323987` (`main`, the parent of this
commit), on the adopted runtime: Sage 11.0.beta5, Python 3.14.10, GAP 4.16.1, with the
indefinite port project bound at `/work`.

## The cause, measured

`158c170385` gave `IndexedFreeGroupMorphism._evaluate_reduced_word` a call
`codomain._retain_admitted_member(value)`: a word's value in a generated subgroup is a
member by that map's range law, and the record is what a membership question reads instead
of searching an infinite subgroup. `_ConditionSetEngine._retain_admitted_member` then
opened with `point = self.universe()(element)`.

Instrumenting both owners in one process on `T_Co` (`Tco.Aut().group_generators()`, which
reaches the port's envelope branch at `eichler.py:901`) shows which objects are involved:

```
retain 1: self 0x716394258650 universe 0x716394e57650 same False element 0x71636fdfd4f0 records 0 universe records 222
retain 2: self 0x716394258650 universe 0x716394e57650 same False element 0x71636fdfe150 records 1 universe records 226
...
  retain 14 FAILED TypeError: membership of Morphism from Lattice of rank 11 and signature (2, 9) to
  element 0x71636fa6f490 in universe records: False
```

The retaining set and its universe are **different objects**, the record is written on the
retaining set, and the coercion asks the *universe*: a generated subgroup, whose general
membership question is an unevaluated proposition. The element itself is not at fault — it
is already the ambient representative that the universe's subgroup holds, because this
library does not reparent subgroup elements.

`main` has moved since the report: the generated subgroup's record is now a mark on the
*element* (`GeneratedSubgroups._mark_admitted` / `_admits_member`, keyed by identity, read
inside `membership_decision`). That closes the subgroup half of the gap — but not this
one, because the coercion happens in the *condition set's* retention, before any mark is
written, and it asks the universe rather than reading a record.

## The repair

One hunk, at `SetMethods._retain_admitted_member`
(`src/sage_extensions/categories/sets/set_categories.py`): record the supplied element
first, and do not coerce it when it already holds the representation the universe uses.

```python
        retained = self._admitted_members
        retained.setdefault(id(element), element)
        universe = self.universe()
        ambient = getattr(universe, "supergroup", None)
        owner = universe if ambient is None or ambient() is universe else ambient()
        point = element if element.parent() is owner else universe(element)
        retained.setdefault(id(point), point)
        return point
```

Nothing is reparented, no predicate that was undecided is decided, and the record still
holds exactly the point a construction supplied, keyed by identity. An element whose
parent is not the universe's ambient group is still coerced through the universe, so the
admission is not widened.

## Runs, at the pushed parent `6db8551`

| run | before | after |
| --- | --- | --- |
| `tests/lattices/test_the_orthogonal_group_of_ten_has_a_discriminant_image.sage` (#333, on main) | 1 failed in 111.82s | **1 passed in 96.82s** |
| `Tco.Aut().group_generators()` with its discriminant image (the #289 test, run untracked) | 1 failed in 98.02s (at `6c4f7a4`) | **1 passed in 164.09s** |
| #287's `test_a_double_coset_section_returns_its_group_elements` and seven neighbours | — | **41 passed in 14.76s** |

The neighbours are `test_generated_subgroup_membership`,
`test_double_cosets_from_a_finite_orbit`, `test_finite_actions_from_permutation_morphisms`,
`test_finite_index_cosets_of_gamma_zero_two`, `test_generated_model_character_quotient`,
`tests/lattices/test_integral_stabilizers` and
`tests/lattices/test_finiteness_premise_under_a_containing_bound`.

The #289 test file is not committed: #289 is closed and its subject moved to
`sage-indefinite-port#72`, so it was run untracked as the `Tco.Aut().group_generators()`
acceptance call.

## Issue closure text

> Repaired at `SetMethods._retain_admitted_member`. Instrumented on `T_Co`, the retaining
> condition set and its universe are different objects and the universe is a generated
> subgroup, so `point = self.universe()(element)` asked that subgroup for a membership
> whose record was written one line later on the other object. The retention now records
> the supplied element first and coerces only when the element does not already hold the
> universe's ambient representative — a subgroup's elements are not reparented here, so a
> point parented by the ambient group is the point.
>
> Measured at `6db8551`: `TEn.O().discriminant_image()` 1 passed in 96.82 s (1 failed in
> 111.82 s before), a `Tco.Aut().group_generators()` run with its discriminant image
> 1 passed in 164.09 s, #287's `test_a_double_coset_section_returns_its_group_elements`
> with seven neighbours 41 passed in 14.76 s.
