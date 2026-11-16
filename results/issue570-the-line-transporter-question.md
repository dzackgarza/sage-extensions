# #570: where the Otilde(T_Co) transporter question at a line cusp spends its time

**The mechanism the issue names is not the one that costs the minutes.**  At the
named cusp the stabilizer image's closure walk is never entered -- `|lower|` equals
`|upper|` -- and `exact_isotropic_stabilizer_generators` answers in 13.8-18.6 s.
The minutes are in `OrthogonalCharacterQuotient.adjust_witness_into_subgroup`, and
inside it in one engine call: GAP's membership in the double coset
`DoubleCoset(S, 1, W)`, where the subgroup's condition `S` is trivial and
`|W| = 89181388800`.  A double coset with a trivial left factor *is* the subgroup
`W`, but the generic engine question does not reduce to the subgroup's own
membership test, and it did not return in 528 s.  That case is now asked as the
subgroup question it is: the adjuster answers in 5.43 s and the question returns.

tree eead610 (main), port 991b88b0, adopted runtime; load 0.45-2.4 during the runs
below except where noted.

## The specimen (construction)

| stage | time |
| --- | ---: |
| `T_Co` | 0.8 s |
| `Otilde(T_Co) = stable_orthogonal_group()` | 1.2-2.7 s |
| `finite_character_quotient()` | 0.00 s |
| `quotient.index()` (= `|rho(O(T_Co))|` here) | 60.64 s, 62.56 s (two runs) |
| the plane, its line, its divided class | 0.03 s |
| the Otilde line row, `isotropic_orbit_representatives(1)`, 527 representatives | 179.73 s (once; 300 s cap expired under load 6.9) |
| the row entry carrying the plane line's divided class | position 492 of 527 |

`|rho(O(T_Co))| = 46998591897600`.  The cusp is the row representative whose divided
class is the plane's own line's (`2[h] + [a3] - [a4] + 2[a8]`); the #381 evidence
recorded position 215 at its own tree, this run's walk order gives 492.  Every probe
after the first replays its coordinates from `.tmp/p570-row.log`.

## The named question, `cusp.transporter_witness(line)`

Before (`.tmp/p570-question.log`), killed at the 575 s probe cap:

| stage | time |
| --- | ---: |
| `invariant_separates_isotropic_orbits` | 55.52 s |
| `isotropic_lift_of` twice | 0.00 s |
| ambient `isotropic_equivalence_witness` (the port) | 20.55 s |
| `separates_witness_orbits` | 0.01 s |
| `exact_isotropic_stabilizer_generators` | 13.78 s |
| `adjust_witness_into_subgroup` | **did not return; 480 s spent, killed** |

Inside the adjuster (`.tmp/p570-adjust2.log`), with `S` the subgroup's condition:

| stage | time |
| --- | ---: |
| `|S|` | 1 (trivial) |
| `IsomorphismPermGroup(product)` | 0.01 s |
| `Subgroup(product, family images)` | 0.01 s |
| `DoubleCoset(S, 1, W)` construction | 0.00 s |
| **its membership test, `coset_point in ...`** | **> 528 s, no walk step taken** |

After the repair (`.tmp/p570-question-fixed.log`):

| stage | time |
| --- | ---: |
| `invariant_separates_isotropic_orbits` | 53.69 s |
| the port's witness search | 20.98 s |
| `separates_witness_orbits` | 0.01 s |
| `exact_isotropic_stabilizer_generators` | 18.59 s (parabolic family 10.00 s of it) |
| `adjust_witness_into_subgroup` | **5.43 s** |
| the question | **98.80 s, answered, witness in the subgroup** |

## `exact_isotropic_stabilizer_generators` at that cusp (`.tmp/p570_stages5.log`)

| stage | time | value |
| --- | ---: | --- |
| parabolic family | 10.50 s | 88 generators (92, 93, 96 in other runs of the same line) |
| `_image_section()` | 52.11 s (60.24 s) | cached per quotient |
| divided data `D(W)` | 0.01 s | orbit 527, walked in 0.02 s |
| `Stabilizer(discriminant_image, data)` | 0.22 s | |
| `PreImages` | 0.00 s | |
| `Size(upper)` | 0.00 s | 89181388800 |
| `Subgroup(product, images of the family)` | 7.69 s | |
| `Size(lower)` | 0.02 s | 89181388800 |
| `IsSubset(upper, lower)` | 0.01 s | true |
| the closure walk | -- | **not entered**: `|lower| = |upper|` |
| total | 91.9 s | |

So the issue's premise -- that the stabilizer image closes by a transversal walk over
minutes -- is not what happens: `|lower| = |upper|` at this cusp and the walk is
never entered.  The cost it named is in the adjuster, and the walk-free certificate
is already what the function performs.

## What remains, and whose it is

The question answers in 98.80 s cold and 44.22 s asked again, where before it never
returned.  The parts left, measured apart on the repaired tree
(`.tmp/p570-question-fixed.log`, `.tmp/p570-repeat.log`):

| stage | time | owner |
| --- | ---: | --- |
| `invariant_separates_isotropic_orbits` | 53.69 s (first call) | here; the `O(A_L)` chain, cached per quotient |
| the ambient witness search | 20.98 s | **the port** (`sage_indefinite_port...marked_lattices.isometry`), paused: not repaired here |
| `exact_isotropic_stabilizer_generators` | 18.59 s (family 10.00 s) | here |
| `adjust_witness_into_subgroup` | 5.43 s | here, repaired by this round |

Of the 527 cusps of the row, 526 are separated by the finite image and their
question costs 0.01 s each (measured at two of them, `.tmp/p570-repeat.log`); the
one question per plane that is not separated is the one above.

## Repaired

`_double_coset_adjustment` (`src/sage_extensions/categories/orthogonal_quotients.py`)
now asks the double-coset membership as the subgroup membership it is when the
subgroup's condition is trivial: `S` trivial makes `S * 1 * W` the subgroup `W`, and
the element asked for is the coset point itself when it lies in `W`.  Neither
kernel group is affected otherwise -- `Otilde` and `Otilde+` both have `S` trivial,
which is why both kernel rows hit this -- and a nontrivial `S` keeps the generic
engine question, which is measured instant at the sizes the other rows use.
