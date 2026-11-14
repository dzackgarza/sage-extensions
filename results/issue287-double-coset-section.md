# #287: the double-coset section rejected its own representative, and where that is now decided

## The defect, reproduced at main `74a4647` (provider), port `991b88b0`

`_DoubleCosetSet.double_coset_section` (`categories/group/g_sets.py`) is a set morphism
into the acting group. On a **finite action of an infinite generated group** its value is

```
representative_map()(orbit.representative()) = augmentation(word_section(...))
```

— a word in the group's *selected generators*, evaluated in the group. So the value is an
element of the group by that evaluation. The section's codomain coercion did not know it:

```
sets/set_categories.py:810   return self.codomain()(function(point, ...))
groups.py:1559               return self._element_constructor_(value)
groups.py:1571               if element not in self:
groups.py:1594               raise TypeError(f"membership of {value} in {self} is undecided; ...")
```

`membership_decision` answers a *general* infinite-subgroup membership question with an
unevaluated proposition, so the coercion raised. Scalar counts: the section must return
words of length two and more on the specimen below; one-letter words and the identity
were already admitted by `membership_decision`'s existing rules, which is why a
two-point coset space does not show the defect and a four-point one does.

## The specimen, without the port

Full file: `tests/groups/test_a_double_coset_section_returns_its_group_elements.sage`.

- `U + U` over `QQ`, read in its `ZZ` restriction; `G = <tau_1, tau_2, swap>` where
  `x |-> x + b(x, v) w - b(x, w) v` at the isotropic `v = e_1`, `w = e_2` (and
  symmetrically) are two Eichler transvections and `swap` exchanges `e_1, f_1`.
  `G` is infinite; all three generators preserve `L = ZZ e_1 + ZZ f_1 + ZZ e_2 + ZZ f_2`.
- `IntegralStructureAction(G, L'.inclusion()).with_stable_containing_bound(L.inclusion())`
  for the index-two sublattice `L' = 2ZZ e_1 + ZZ f_1 + ZZ e_2 + ZZ f_2`; `right_cosets()`
  is `G/G_{L'}` on the finite orbit of `L'` (**4** points).
- `cosets.double_cosets(Q)` for `Q = <tau_1>` (**3** orbits) and `Q = G` (**4**), then
  `double_coset_section()`.

Before the fix: `2 failed, 1 passed in 7.67 s`, both failures that `TypeError`. After:
`3 passed in 2.84 s`; with the mark on the element, this file and its seven neighbours:
`41 passed in 17.94 s`.

## The repair, at the owner

`categories/group/groups.py`, `GeneratedSubgroups.ParentMethods`:

- `_evaluate_reduced_word` retains its value and the value's inverse through
  `_retain_admitted_member` when the codomain is a proper generated subgroup. The letters
  are that subgroup's selected generators, so the value's membership is *supplied by this
  map*; inverting a word reverses it, so the inverse is supplied too.
- `membership_decision` reads the record before the general question, so a consumer that
  coerces the value back — a coset or double-coset section — gets a certificate.
- The mark lives on **the element**, as a tuple of the groups whose construction supplied
  it, compared by identity (`element._admitted_subgroups`). Not a value key and not a hash
  key: this library's group elements are not reliably equatable — on this specimen an
  owned lattice isometry satisfies `value == ~value` and `hash` is the parent's, measured
  in `.scratch/issue292/run287hash.log`:

  ```
  type: OwnedLatticeIsometryMor_with_category_with_category.ArrowType
  hash: 4843919552574235634
  inverse hash: 4843919552574235634
  value == inverse: True
  ```

  Not a record on the subgroup either: `fd60fe9` first kept an id-keyed dict on the
  subgroup, one entry per value of the cover's word evaluation. That is one entry per
  word, so the subgroup would grow without bound on exactly the long walks this admission
  serves — the shape sage-extensions#292 is about one call away. `c694cb9` moves the mark
  onto the element, where it lives exactly as long as the element does.

- Nothing is reparented. An element parented by the subgroup breaks the *ambient's*
  ingress (`_to_engine` asserts membership in the supergroup), which is why group
  morphisms into a subgroup keep their ambient representatives
  (`_GroupMorRealizationMixin._normalize_admitted_element`); the admission travels beside
  the representative instead.

## What is not fixed, and is the next owner's

`GeneratedSubgroups._engine_subgroup` calls `group(generator)` for each *supplied*
generator, so

```
group.subgroup(tuple(lattice_stabilizer.group_generators()))
```

raises the same `TypeError` (`_engine_subgroup`, groups.py:2035; reproduced in
`.scratch/issue292/run287g.log` on the same lattice). That family is a stabilizer's
generator family, not a value of this group's cover, so no range law of this construction
supplies it: deciding it needs the construction datum of that family (its own cover, or a
stated finite generating set of the subgroup it is taken in). It is not #287's call and is
not patched here.

## The port

The port's `flags_through` (`indefinite/isotropic_induction.py:228-230` at `991b88b0`) is
the same construction and now returns: on the issue's lattice
`Lattices(ZZ)([[0,1,0,0],[1,0,0,0],[0,0,0,2],[0,0,2,0]])` it gives one flag per line class,
2 line classes, in 12 s (`.scratch/issue292/run287f.log`). The issue's own reproducer
(`IsotropicInduction(...).basis_marking_classes`) is a later port method that this paused
checkout does not contain, so that exact call was not run; the private construction it
fails in was, at both the before and after states of this fix.
