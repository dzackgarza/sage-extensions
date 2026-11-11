# #341: a stabilizer's generator family generates a subgroup, and where the membership question was coming from

## The cause, measured

`GeneratedSubgroups._engine_subgroup` opened with

```python
selected = finite_ordered_set(tuple(group(generator) for generator in generators))
```

`group(generator)` is `_Group._element_constructor_`, which asks `generator not in group` for
a proper subgroup, and `__contains__` puts that to `membership_decision` — an unevaluated
proposition for a general infinite generated group.  So the construction refused a family
that this library's own constructions had produced, and reported it as
`TypeError: membership of Morphism … is undecided; supply a word witness to
membership_decision` (`groups.py:1559 → :1571 → :1594`, from `:2035`).

What the family actually is, per specimen, printed element by element:

| specimen | `group` | stabilizer generators | each generator's parent |
| --- | --- | --- | --- |
| `U + U` over `QQ`, `G = <τ₁, τ₂, swap>`, `S` = lattice stabilizer of `2ZZ e₁ + ZZ f₁ + ZZ e₂ + ZZ f₂` | the **generated subgroup** `G` | 12 | `O(U + U)` — the **ambient**, not `G` |
| `T_En`, `G = O(T_En)`, `S` = setwise stabilizer of `ZZ e` | the **ambient** `O(T_En)` | 6260 | `O(T_En)` — i.e. `G` itself |

So the two rows fail differently, and only the first one fails:

- **Ambient case (`T_En`).** `_element_constructor_` of the ambient takes the parent-identity
  branch (`__contains__`: `value.parent() is self`), so no membership question is asked and
  the construction already succeeded: `group.subgroup(tuple(S.group_generators()))` returned
  a `Subgroup of Orthogonal group O(T_En)` in 2208.3 s on the **pre-repair** tree
  (`.scratch/issue292/run341ten.log`; the run's process loaded the library before the repair
  was written to disk — file mtimes 10:12:48 against a process start at ~10:12:00, and the
  generator count 6260 with `parent is group: True` on every one of the first four).
  `T_En` therefore does *not* reproduce the issue as reported; the test keeps it as a
  regression guard, and it is not red before the repair.
- **Generated-subgroup case (`U + U`).** The generators are parented by `O(U + U)` while
  `group` is a proper subgroup of it, so parent identity does not decide, and the
  membership question is asked — that is the `TypeError` #287's results file recorded, and
  `#341`'s acceptance is about. This is the red.

## The repair

At `GeneratedSubgroups._engine_subgroup`, through one helper
(`src/sage_extensions/categories/group/groups.py`): `_supplied_generator(group, element)`
reads one supplied generator as an element of `group` without deciding membership.

- An element whose parent **is** `group` is that element.
- An element whose parent is `group`'s **ambient group** is a member of `group` by the
  caller's supplied premise (`OWN-05`, `OWN-22`), and it is recorded through the same
  element-side admission a free cover's word values get
  (`_retain_admitted_member`, `0c6ea4e7df`), so no later question about it is put to
  `group` either.
- An element whose parent is **neither** is coerced through `group` exactly as before, so a
  foreign element is still refused and nothing is admitted that was not supplied.

The admission is written only for a **generated** subgroup (`group in
GeneratedSubgroups(ambient)`): that record is the family the subgroup was handed. A
predicate subgroup's membership is its predicate, and recording a supplied element there
would answer a question its predicate has not decided, so that branch is left to the
predicate.

The stabilizer's datum is the first two bullets: its generator family is built through its
own selected free cover into the ambient group, and this library does not reparent subgroup
elements, so "element of `L.Aut()`" is written in the element's parent rather than decided.

## Runs, on the tree this file ships with

```
tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage   (the U + U half, pre-repair)   1 failed in 2.62 s
tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage   (the U + U half, post-repair)  1 passed in 2.13 s
eleven group/lattice files at the narrowed repair, the #341 U + U half and #287's file
  among them                                                                                        55 passed in 19.88 s
```

The full run at the tip this file ships with: the #341 file's two halves, #287's file,
seven neighbours and `tests/lattices/test_the_orthogonal_group_of_ten_has_a_discriminant_image.sage`

```
44 passed in 4577.49s (1:16:17)
```

with the two `sha256` values of the edited library file and the new test pinned before the
run and re-checked after it (`.scratch/issue292/issue341-pre-run.sha`), so the run is of the
bytes that were committed.

## What is not claimed

No order, index or finiteness of the constructed subgroup is asserted: an infinite generated
subgroup has no decided order here, and asking would be the question this construction
declines to ask. The premise is the caller's — a family that does not lie in `group` but is
parented by its ambient is admitted on that statement, not verified.
