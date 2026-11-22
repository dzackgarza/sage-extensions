# The gamma-h plane row's cost: the stabilizer family that seeds the closure

The plane-orbit row of `tests/enriques_polarization_rows_by_card.py` did not
return inside its 1800 s cap on most `gamma-h` cards while the flag-orbit row on
the same cards returned the card's value (#620).  This note names the stage that
costs the row, gives the repair and its owner, and records the run.

## What the row is

The row is `PredicateSubgroups.isotropic_orbit_representatives(2)`, which takes
the ambient `O(N)`-orbits of primitive isotropic planes and splits each under the
card's group.  With `Gamma` a character kernel, the `Gamma`-orbits inside one
`O(N)`-orbit `G.P` are the double cosets `rho(Gamma) \ rho(G) / rho(Stab(P))`
(D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces --
computational aspects*, arXiv:2302.01679v2, Lemma 3.6), so the row needs the
exact finite image of the plane's stabilizer.  It certifies that image in
`OrthogonalCharacterQuotient.exact_isotropic_stabilizer_generators`: an upper
bound `U` is computed from the plane's divided class set, and the image is closed
to `U` by exhibiting elements of the stabilizer.

## The split, and the stage that costs it

Card `gamma-h-25` (85 plane orbits, 213 flags) at `b0801b6`, in the pinned image
(Sage 11.0.beta5) with the paused port at `991b88b0`:

| stage | seconds |
| --- | --- |
| construction: `Enriques()` | 1.1 |
| construction: `polarization_group` (the card's `Gamma_h`) | 2.9 |
| computation: ambient `O(N)` plane row, 2 planes | 12.2 |
| computation: ambient `O(N)` flag row, 3 flags | 157.8 |
| plane 0: `is_parabolic_complete()` -> `False`, with 173 parabolic generators | 3.3 |
| plane 0: `exact_isotropic_stabilizer_generators` | not returned at 480 s |

Construction is 4 s of the row's thousands: the whole cost is the computation.
The parabolic route declines after a 3.3 s decision, so the row falls through to
the exact stabilizer image, and that is where the minutes are.

The stack the watchdog recorded is inside the first statement of that method:

```
exact_isotropic_stabilizer_generators:1944  generators = list(ambient.isotropic_stabilizer_generators(...))
  -> _isotropic_stabilizer_generators -> automorphism_group_generators(Ar(Lattices), plane)
  -> isotropic_induction.plane_automorphism_generators -> _stabilizer_generators
  -> tuple(lattice.integral_isometry(g) for g in action.stabilizer().group_generators())
  -> _record_generators_in_supergroup: each generator is a word
  -> _evaluate_reduced_word -> _signed_generator_image -> isometry compose
  -> _morphism_from_engine_matrix -> nrows -> _owned_engine_element -> _own_ring
  -> if ring in OwnedRings()
```

The seed family is built from the port's marked-lattice construction, which
spells each generator of the ambient action's stabilizer as a word in the ambient
generating family and multiplies it out; every product re-derives the matrix
shape and re-owns the base ring.  Memory climbs linearly with it: 1.77 GB at
320 s and 2.29 GB at 538 s, still climbing when the probe ended.

The flag row's counterpart is the same kind of construction one rank up
(`flag_automorphism_generators`), and the plane call does **not** repeat it: the
plane row builds the plane stabilizer's family, the flag row builds the flag
stabilizer's family and never reaches the plane stabilizer at all.  The plane's
construction is the more expensive of the two, which is the factor the issue
records between the plane and flag rows.

## The repair, at its owner

`exact_isotropic_stabilizer_generators` needs elements of `H = Stab_{O(N)}(P)`
from that line, not a family that generates `H`: the closure below certifies the
image against `U`, and raises when the index cannot be closed.  The stabilizer in
`O(N)` of a primitive isotropic plane **is** the parabolic subgroup at that
plane, and that subgroup's own construction exhibits its elements from the
plane's block equations (Dutour Sikirić and Hulek, arXiv:2302.01679v2,
Theorem 4.9, the block form of an isometry preserving an isotropic plane).  In
the same row that family is already built, and it holds 173 elements of the
stabilizer for a 3.3 s decision.

So the seed of the closure is the plane's parabolic family, and the pass over the
right transversal ends the moment the image reaches `U` instead of asking the
ambient group a transporter question for every coset the pass started with.  The
returned contract is unchanged, and the count is the card's.

## The run

    python3 tests/enriques_polarization_rows_by_card.py --one gamma-h-25:planes --cap 1800

    @@ROW@@ {"id": "gamma-h-25:planes", "expected": 85, "computed": 85,
             "elapsed": 61.1, "state": "PASS"}

The library's own stage record of that run (`.timings/stages-*.jsonl`):

```
isotropic orbit representatives            57.12 s
  discriminant image                        0.00 s
  ambient O(L) row                         12.97 s   (the 2 ambient planes)
  coset splitting and transport            44.12 s
    parabolic completeness decision          3.51 s
    parabolic completeness decision          3.41 s
```

Peak resident memory of the run: 755 MiB, against 2.29 GB and climbing while the
parent's closure had not returned.  Inside the closure, plane 0 closes in 47.0 s
with 118 exhibited generators and plane 1 in 6.8 s with 131; their splitting
yields 17 and 68 lifts, and `17 + 68 = 85` is the card's `#I_2` for case 25
(Dutour Sikirić and Hulek, arXiv:2302.01679v2, Table 1).

## What is not repaired here

The flag row builds its stabilizer family by the same word-evaluation route
(`flag_automorphism_generators`), and this repair does not touch it: on
`gamma-h-25` that construction alone had not returned at 300 s.  The issue's
plane row is decided; the flag row's cost is the same defect one rank up and is
named here rather than folded into this change.

## No red test

No library answer in this path is wrong at the parent: the row returns the card's
value wherever it returns, and every family
`exact_isotropic_stabilizer_generators` returns is a family whose image is the
upper bound.  The defect is a slow run, so there is no failing assertion to write,
and none is manufactured to stand in for one.  The record above is the evidence.

## The seed's premise, and what it costs

The closure certifies `chi(H)` for `H = Stab_{Gamma_0}(x)`, where `Gamma_0` is the
quotient's ambient group.  A seed element outside `Gamma_0` is not an element of
`H`, and the closure would not notice: `upper` is computed inside `Gamma_0`'s
character image, so the image is capped there and a foreign generator is returned
as if it were a stabilizer element.  The parabolic family is taken in `O(N)`, so
the seed keeps only the generators the ambient group's own membership predicate
admits, and falls back to `isotropic_stabilizer_generators` when it admits none.

Measured on `gamma-h-25`: 173 parabolic generators tested in 0.0 s, all 173
admitted, closure 27.6 s, 17 splitting lifts.  The predicate is the character
test that defines the group, so the filter is free.

Measured on `U + U(2) + <-2>` (rank 5, `|A_L| = 8`), about whether a quotient
with a proper ambient group exists here at all:

| subgroup | its `supergroup()` | quotient's ambient group | index |
| --- | --- | --- | --- |
| `O^+` | `O(L)` | `O(L)` | 2 |
| `Otilde` | `O(L)` | `O(L)` | 2 |
| `Otilde^+` | `O(L)` | `O(L)` | 4 |

So no construction in this tree produces a quotient whose ambient group is a
proper subgroup, and the case the restriction protects against has no specimen
here: the plane's parabolic family on that lattice has 27 generators, 2 of them
outside `O^+`, and those two are inside the ambient group the quotient is
actually built over.  The restriction is what keeps the premise true for a
subgroup-of-a-subgroup construction, which this tree does not have yet.
