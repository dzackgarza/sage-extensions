# The selected subfamily of a discriminant-point preimage is read, not realized

`L.Aut().discriminant_point_stabilizer_image_generators(point)` selects a
subfamily of the Schreier family of the point's orbit whose images in `O(A_L)`
generate the point's stabilizer.  The selection stops as soon as the subgroup the
images have generated reaches `|O(A_L)| / |orbit|`, so it visits a prefix of the
family; until now it read that family whole first, through
`preimage.group_generators()`, and `_orbit_schreier_morphism` with
`drop_trivial=True` evaluates **every** member to decide which ones are trivial.

## The mechanism

`discriminant_preimage(..., orbit_point=point)` replaces the preimage's
generating morphism by the orbit's Schreier family
(`_discriminant_point_stabilizer_morphism` -> `schreier_generating_morphism(drop_trivial=True)`).
That family has `|letters| * |orbit|` members -- `26 * 1024 = 26 624` on
`T_En`, `346 * 67 456 = 2.3e7` on `T_Co`, `15 * 67 456 = 1 010 640` on card
`0125` -- and realizing it costs one group element per member, plus the
`drop_trivial` pass over all of them.  The selection needs a few members.

## The repair

| site | what it is |
| --- | --- |
| `src/sage_extensions/categories/group/g_sets.py`, `LeftCosetGSets.schreier_family_members` | **the repair**: yields the same words in the same order from the retained section and free cover, one at a time |
| `src/sage_extensions/categories/lattice_morphisms.py`, `_discriminant_point_stabilizer_members` | the selection's reader: the coset space the preimage's morphism would have built, read lazily |
| `.../lattice_morphisms.py`, `discriminant_point_stabilizer_image_generators` | iterates that reader, skips a member whose value is the identity (the `drop_trivial` rule, applied per member), keeps its own stop -- no cutoff |

The answer is unchanged: the identity members skipped on the fly are exactly the
ones `drop_trivial` removes, the order is the family's (orbit position outer,
letters inner), and the loop's stop is still the stabilizer's order, with the same
`ArithmeticError` when the whole family's images do not reach it.

## Measured

Card `0125`, `L = U(2) + E8(-2)`, `|A_L| = 1024`, `point = A_{U(2)}` (4 classes),
orbit `67 456`:

| | selection |
| --- | --- |
| parent (`92188cb`) | **killed at 600 s**; the orbit took 13.1 s, nothing followed |
| repair | **9 members in 68.7 s**, peak RSS 1 546 MiB, image order `696 729 600` = `|O(A_L)| / |orbit|` |

The announced family itself -- `discriminant_point_stabilizer(point).group_generators()` --
was still running at 500 s and 1.5 GiB in the same session, which is the datum
the selection no longer builds.

`T_Co` (the consumer's specimen, `|A_L| = 2048`, same 67 456-point orbit): the
orbit takes 155 s, and the call was killed at 900 s in **both** trees -- on the
parent 734 s past the orbit, with the repair 740 s past it.  So on `T_Co` the
family is no longer what the call waits in, and the call still does not return in
15 minutes: what remains there is GAP's `stabilizer_of_classes` over 2048
classes, the `F_2` class action over the ~346 ambient letters, and the
group-layer search of the same 67 456-point orbit.  That is the next unit, not
this one; the `T_Co` rows stay image items.

## Tests

`tests/lattices/test_the_selected_subfamily_is_a_subfamily_of_the_announced_family.sage`
(specimen `U + U(2)`, `|A_L| = 16`) pins the contract the repair must keep: the
selection's members lie in the preimage, each carries the point onto itself, each
one's discriminant image occurs among the announced family's images, the
selection is smaller than that family, and the images of the selection generate
`|O(A_L)| / |orbit|`.  Both assertions hold before and after the repair, which is
what makes it a contract and not a red test.

Run with the time gates on, the tree bound at `/repos/sage-extensions` and the
port at `/work`:

```
8 passed in 24.23s
11.61s call  ...test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup
 7.17s call  ...test_the_selection_is_a_subfamily_of_the_announced_family
 2.36s call  ...test_the_selections_images_generate_the_points_stabilizer
 0.99s, 0.53s, 0.43s  the factor-law file's three tests
 0.21s, 0.02s         the stabilizer acceptance file's other two
pytest exit 0
```

`tests/lattices/test_the_decomposition_preimage_returns_generators.sage` was not
run: it builds the announced family (944 385 members at `0125`) and that build
alone did not finish in 500 s here, so the file is over the ten-minute limit on
this host independently of this change.

## The `T_Co` walk: one orbit search, no transition table

On `T_Co` (`|A_L| = 2048`, the same 67 456-point orbit, `O(L)`'s ambient family
342 letters) the call was killed at 900 s twice after the family was no longer
built, and the selection's own search was the stage it sat in.  Two walks of the
same orbit were being made, and each one built a table with one entry per
(point, letter) pair -- `342 * 67 456 = 2.3e7` entries:

- `discriminant_point_orbit(point)`, for the orbit's cardinality alone, realized
  the orbit as a `G`-set from a complete transition table;
- `pointed_orbit(...)`, for the section, searched the orbit again.

The staged probe, on the pushed head before this change:

```
point built, |A_L| = 2048                      3.2 s
O(A_L) engine / |O(A_L)| = 46998591897600      2.5 s
stabilizer_of_classes                        106.9 s
P generators 3                                 0.2 s
O(L) ambient family 342                       42.8 s
class action                                  54.0 s
discriminant_point_orbit           did not finish in the 600 s cap (155 s in a quiet window)
```

Repair: `_discriminant_point_orbit_and_section` walks the orbit **once** with
`FiniteGSets._orbit_words(..., retain_transitions=False)`, which returns the
points and one transversal word per point and no table, and
`_discriminant_point_stabilizer_members` composes each family member from those
words, evaluating one action per member (`s.p`) instead of every letter at every
point.  The selection no longer builds the orbit `G`-set at all: it needs the
orbit's cardinality and its section, not the action of every letter.

After the repair, same specimen, the same call:

```
orbit and section 67 456 points in 148.0 s
selection returned 10 in 335.7 s
image order of the selection 696 729 600 = |O(A_L)| / 67 456
done at 485.0 s (the probe walks the orbit once for itself as well)
```

So the call returns on `T_Co` in **335.7 s** where it was killed at 900 s (two
runs) and at 2 662 s in the consumer's record, and it returns the index-stabilizer
order exactly.  The suite cannot hold this: 335.7 s is far over the 20 s call
ceiling, so the deciding evidence is the probe and the `0125` measurement above.

Regression, the same three files, time gates on: `8 passed in 23.93s`, the
subfamily contract `6.47 s` -- which is what says the section the selection reads
is still the announced family's.
