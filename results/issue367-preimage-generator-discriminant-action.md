# #367: `discriminant_morphism()` of a preimage generator is `rho_L` of it

Card `0125`, `L = U(2) + E8(-2)` (rank 10, signature (1,9), `A_L = (Z/2)^10`,
`|A_L| = 1024`).  The family is `L.Aut().discriminant_point_stabilizer(point)`'s
generating family, `point = A_{U(2)}` inside `A_L`, as #354 built it
(`results/issue354-the-preimage-and-the-kernel.md`).  All numbers below are
measured on the fetched `main` `27be129`, the port bound at `991b88b0`.

## What the two spellings are, at the owner

| object | owner |
| --- | --- |
| `rho_L` | `lattices.py:4196-4214`, `discriminant_representation`: `image(element)` is `isometry.discriminant_morphism()`, after coercing the element into `Aut(L)` |
| `g.discriminant_morphism()` | `lattice_morphisms.py:2195-2202`: `orthogonal_group().from_morphism(self.discriminant_isometry())` |
| the induced map | `lattice_morphisms.py:2178-2193` from `(forward(self), forward(self^-1))`, and `:2140-2176` computes `forward` by `b_M(f e^s, m_r) = b_L(e^s, f^-1 m_r)` |
| the member's type | `groups.py`, `_evaluate_reduced_word`: the letters are images in the codomain, so a family value is an element of `O(L)`, not of the subgroup façade |

So `rho_L(g)` **is** `g.discriminant_morphism()`: the representation's `image`
calls exactly the accessor, and `from_morphism` returns its argument unchanged
when its parent is the group (`torsion_form_modules.py:2117-2142`).  There is no
second computation of the induced action on that path, hence no place for the two
to differ.

Measured (`.tmp/p367-diag.log`):

```
preimage_morphism() is lattice.discriminant_representation():  True
member.parent() is O(L):                                      True
preimage(member) is member:                                    True
accessor is preimage_morphism()(member):                       True     (same object)
accessor is again member.discriminant_morphism():              True
```

## The reproduction attempt: no member disagrees

1. **Stride scan over the whole family** (`.tmp/p367-scan.log`): labels
   `0, 250, 500, ...` up to `944384`, 3778 samples, each compared as
   `member.discriminant_morphism() != preimage_morphism()(member)`.  **No
   disagreement**, including the last member (label `944384`, agreement
   `False`-for-difference).  466.5 s.
2. **Single-label scan of the first 1500 labels** (`.tmp/p367-repro.log`): all
   agree; stopped there because the stride scan covers the family.
3. **The selected subfamily** of `discriminant_point_stabilizer_image_generators`
   (9 members, `.tmp/p367-diag.log`): all agree; the 15 letters of `O(L)` agree.

There is therefore **no first disagreeing index**: the comparison cannot fail on
this tree, and the reported observation is not reproducible on `main`.

## The accessor is not merely equal to itself: it is the induced map

Because the first comparison is an identity, it decides nothing about whether the
accessor is *right*.  It was checked against the definition, from the member's own
integral matrix: for `g` with matrix `M` in the basis of `L`, the induced map on
`L^#/L` is `[v] |-> [(M^-1)^T v]`, and two dual vectors are one class exactly
when `G^-1` of their difference is integral (`G` the Gram matrix, `L ⊆ L^#` on
the rows of `G`).  Arithmetic in `fractions.Fraction`; no discriminant-form code
on the independent side (`.tmp/p367-definition2.log`):

```
labels 0, 1, 2, 3, 100, 1000, 10000, 100000, 500000, 944384
  each: the accessor is the definition on all 10 classes of A_L
labels with any difference: []
```

## The laws the contract rests on

On 15 labels including the last (`.tmp/p367-consistency.log`), every one true:

* `member * ~member == 1` and `~member * member == 1` in `O(L)`;
* `Disc(member) * Disc(~member) == 1` in `O(A_L)`, and `Disc(~member) == ~Disc(member)`;
* `Disc(member * other) == Disc(member) * Disc(other)`;
* `Disc(member)` carries the decomposition point to itself.

These are what a wrong retained inverse, a transposed basis or a mis-composed
word would break; none does.

## What the earlier observation can be

#354's record says the accessor "disagrees with `rho_L(generator)` on some deeper
family members".  On this tree:

* the two are one object whenever the member is an element of `O(L)`, which the
  family's values are;
* `rho_L` on a member rebuilt in another group refuses rather than rebuilding it
  silently: `_normalize_admitted_element` walks a subgroup façade to its ambient,
  and `LatticeIsometryMor._morphism_from_images` then refuses a foreign arrow
  (`_refuse_foreign_arrow`, `CON-17`) or raises the domain mismatch when the
  lattice object differs;
* a second, equal lattice built from the same Gram rows shares the discriminant
  group parent (`Lattices(ZZ)(rows)` is content-cached), so even that route
  returns the same element (`.tmp/p367-spellings2.log`).

So the reported disagreement is not a disagreement of these two maps on the
current owner.  The record that produced it was written while the orbit action of
`_DiscriminantF2Model` was mis-keyed by object identity — #354's own note says
that version's orbit collapsed to 4608 points and its family had 64 513 members
instead of 944 385, which is exactly the kind of state in which a member is not
the word it is labelled by.  Nothing in the present tree reproduces it.

## What changed

Nothing in `src/`.  There is no site at which the accessor and `rho_L` differ, so
a "repair" would be a change with no defect behind it, and a comparison that
corrects one side after the fact is excluded by the issue itself.  What is added
is the contract as a test: `tests/lattices/test_the_preimage_generator_discriminant_action.sage`
takes the public call's family and asserts, on the labels `0, 1, 2`,
`letters - 1`, `letters * 100`, `letters * 10_000` and `count - 1`, that
`member.discriminant_morphism()` equals
`preimage_morphism()(member)`, that it preserves the decomposition point, that
`Disc(g) * Disc(~g)` is the identity, that `Disc(~g) == ~Disc(g)`, and that
`Disc(first * last) == Disc(first) * Disc(last)`.  The last four are the content
that can fail; the first is the issue's statement.

## Evidence

| log | what it is |
| --- | --- |
| `.tmp/p367-scan.log` | the stride-250 scan of the whole family: 3778 samples, no disagreement, last member included |
| `.tmp/p367-repro.log` | the first 1500 labels, one by one: all agree |
| `.tmp/p367-diag.log` | the object identities, the selected subfamily, the 15 letters |
| `.tmp/p367-consistency.log` | inverse, product and point laws on 15 labels including the last |
| `.tmp/p367-definition2.log` | the accessor against `[(M^-1)^T v]` on all 10 classes, 10 labels |

Test: `tests/lattices/test_the_preimage_generator_discriminant_action.sage`,
`1 passed in 53.11 s` through `.scratch/sage-python-port` with
`--no-time-gates --timeout=0` (`.tmp/p367-test2.log`); `just test-lint` on it:
`1 files, 0 findings`.
