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


## Addition (chat mkeo's report): three further lattices, and the Õ⁺(T_En) line row

Four further inputs hit the same frame on the pre-repair tip. Measured with the port at
`/work`, in one process per tree: the pre-repair tree is `6db8551` (the parent of the
repair), the post-repair tree is `main` with it.

| input | pre-repair `6db8551` | post-repair |
| --- | --- | --- |
| `U(2) ⊕ U(2)` (rank 4, signature (2,2)), `Aut().group_generators()` | `TypeError: membership … is undecided`, 3.13 s | 33 members, 4.34 s |
| `U(2) ⊕ U(2) ⊕ ⟨−6⟩` (rank 5, (2,3)), same call | `TypeError`, 6.49 s | 152 members, 11.71 s |
| `U(2) ⊕ U(2) ⊕ U(2)` (rank 6, (3,3)), same call | `TypeError`, 10.38 s | 105 members, 38.60 s |
| `Otilde^+(T_En)` line row = `TEn.stable_orthogonal_group().intersection(TEn.O_plus()).isotropic_orbit_representatives(1)` | `TypeError` at `eichler.py:901` → `groups.py:1594`, 139.47 s | no exception; stops inside `group_generators()` at 6.44 s (below) |

The three lattices are even, of signature (2,2), (2,3) and (3,3); each is a `2U` sum with
an extra summand, so each takes the port's envelope branch that reaches
`approximate_generators`.

**The member counts are not comparable across revisions and are not asserted.** Chat mkeo
recorded 9, 9 and 35 at `8d44136`; the repaired tree gives 33, 152 and 105. The count is
whatever the port's sampled search settles on (#289, moved to `sage-indefinite-port#72`),
and the tree's generator route has changed since `8d44136` as well, so the recorded three
are agent results and not a card value: they identify the input, and what the repair
restores is that the call returns. Nothing in the test tree asserts them.

**The `Otilde^+(T_En)` line row: the crash is gone, the count is not in yet.** After the
repair the row no longer raises. It builds `stable = {g : ρ_L(g) ∈ 1}` and
`O⁺ = {g : sn_RR(g) = 1}` in 6.4 s, and is then inside `group_generators()` on their
intersection:

```
[    0.07s] lattice built
[    6.34s] stable_orthogonal_group() built: {g in O(T_En) : rho_L(g) lies in ...}
[    6.43s] O_plus() built: {g in O(T_En) : sn_RR(g) = 1}
[    6.44s] intersection built: {g in O(T_En) : g lies in every selected subgroup}
[    6.44s] group_generators ...
```

A first post-repair run did not leave `group_generators()` inside an 1800 s cap; a second
runs under a 3300 s cap (background job `jmwc0f4px`) and had not left it when this file was
written. So what is established for this row is that the reported exception is gone and
where the remaining cost is; **no count is claimed for it here**.

The comparable number is a card value, not a run's: card `029J`'s `Otilde+` row states
`constant: 528` — 528 primitive isotropic lines, which its citation splits into two orbits
of lengths 1 and 527 — read by tag through `card_line_orbit_row("029J", "Otilde+")` and
`card_line_orbit_lengths("029J", "Otilde+")` on the digest pinned at
`d6a539339bac5ea0ee8d8bde5dc19564955eb152`. When the row returns, its count is compared
with that card value; nothing here asserts a value the run produced.

I also checked that the recorded numbers are not another call on the same lattices: on
`U(2) ⊕ U(2)` the number of plane orbits is 1, the discriminant image's order is 72, and
`O^+`'s generator family has 66 members — none of them 9.

**Which tree each measurement is on.** The repair is `src/sage_extensions/categories/sets/set_categories.py`
alone and is unchanged from `6d486c2` to the tip this file is pushed at; `groups.py`,
`lattice_morphisms.py` and `lattices.py` are byte-identical across those two commits as
well, so the acceptance runs below hold at the tip. The one exception is the row's count:
`isotropic_orbits.py` gained 394 lines between them (#312, #297), and the row's last step
is `isotropic_orbit_representatives`, so the row's post-repair stage — measured on the
`#339` commit itself — must be re-measured at the tip before any count is claimed for it.

## Acceptance items, as they stand on `main`

| item | state |
| --- | --- |
| `tests/lattices/test_the_orthogonal_group_of_ten_has_a_discriminant_image.sage` (#333) | established: 1 passed in 96.82 s |
| `Tco.Aut().group_generators()` returning | established: 1 passed in 164.09 s (the held #289 test, run untracked) |
| #287's `test_a_double_coset_section_returns_its_group_elements` | established: 41 passed in 14.76 s with seven neighbours |
| `U(2) ⊕ U(2)`, `U(2) ⊕ U(2) ⊕ ⟨−6⟩`, `U(2) ⊕ U(2) ⊕ U(2)` | established: the three calls return |
| the `Otilde^+(T_En)` line row | the exception is gone; its count is not established |

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
