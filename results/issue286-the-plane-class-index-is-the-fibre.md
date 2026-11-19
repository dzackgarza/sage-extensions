# The plane class index: which quotient it is, and the fibre it counts

A correction, with the measurement that forced it.

## What the issue asks

`#286` asks for "the index `[Stab_{O(q)}(v̄) : ρ(Stab_{O(T_Co)}(v))]` per finite
class" -- the **ambient** stabilizer's image.  For planes that is

$$
\bigl[\mathrm{Stab}_{O(q)}(J) : \rho(\mathrm{Stab}_{O(T_{Co})}(P))\bigr],
\qquad J = [P/2],
$$

and it is the number of the row's plane cusps lying over one class `J`.

## The error in the two earlier notes

`OrthogonalCharacterQuotient.plane_class_index` computes
`[Stab(J) : ρ(Stab_Γ(P))]` -- the *subgroup's* image -- and the two notes
(`results/issue286-the-plane-class-index-is-one-value-per-row.md`,
`results/issue286-the-four-items-reargued.md`) called that the issue's index and
"the number of the subgroup's plane orbits inside one class `J`".  Both claims
are wrong.  On `U + U(2) + <-4>` the quotient returns **4** at a plane of the
kernel row, and that row has **three** plane cusps over **three** classes: one
per class, a fibre of 1.  For a kernel `ρ(Stab_Γ(P)) = 1`, so the quotient is
`|Stab(J)| = 4` -- an order, not a fibre count.

## The correct statement, and its proof

The ambient index is constant over all liftable `J`, and the proof needs no
normality: for `g` in `O(q)`, `Stab(gJ) = g Stab(J) g^{-1}` and
`ρ(Π_{gP}) = g ρ(Π_P) g^{-1}`, so the quotient of the two orders does not move.
The normality argument of the earlier notes was aimed at a different question
and is not what this one rests on.

**Measured, three lattices** (probe `.scratch/w286-probes/probe-index.py`, logs
`probe-idx2.log`, `probe-idx3.log`; each row and each order computed in the same
process):

| lattice | `|O(q)|` | `|Stab(J)|` | `|ρ(Stab_{O(L)}(P))|` | index | classes `J` | kernel plane cusps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `U + U(2)` | 2 | 1 | 1 | 1 | 2 | 2 |
| `U + U(2) + <-4>` | 12 | 4 | 4 | 1 | 3 | 3 |
| `T_Co` | 46998591897600 | 1981808640 | 247726080 | **8** | **23715** | **189720** |

and in every row `classes × index = cusps`: `2·1 = 2`, `3·1 = 3`,
`23715·8 = 189720`.  The `T_Co` line's three orders are `#360`'s measurement at
a `T_Co` plane (`results/issue360-coble-plane-row.md:48`), and its cusp count is
the row's recorded value (`results/issue286-the-stage-1-call.md:372-373`).

So on `T_Co` the index is **8**, for every row and every liftable class -- the
number the page's `thm:plane-fibre` item 1 states, and the `8` of `23715·8`.

## What changed in the code

`record_plane_class_indices` now records the ambient index for **every** row
from the plane's own parabolic (`stabilizer_discriminant_image_orders`,
`stabilizer_discriminant_image_index`), with the class count
`|O(q)| / |Stab(J)|` and the row's own cusp count, so the run prints
`cusps = classes × index` where a reader can see it.  It no longer asks a
character quotient for the number: that quotient answers a different question,
and it is left in the library as what it is, `[Stab(J) : ρ(Stab_Γ(P))]`.

## The tests

* `tests/lattices/test_the_plane_class_index_counts_the_fibre.sage` -- on
  `U + U(2) + <-4>`, the class count, the index and the row's cusp count are
  each computed, and `cusps = classes × index` is asserted with `3` and `1`.
  Measured 22.47 s under a loaded VM (the row itself 4 s).
* `tests/lattices/test_the_plane_class_index_by_two_routes.sage` -- unchanged
  from the previous round: `|Stab(J)|` three ways (the parabolic's bound, the
  quotient's meet, `O(q)`'s setwise stabilizer), which is what pins the two
  orders the index is made of.

## What remains owed, and it is not this index

`Γ_{Co,2}` returns **7** plane cusps over 23715 classes, so its fibre is not the
ambient index: `ρ(Γ) = Stab_{O(q)}(A_{U(2)})` is not trivial, and the number of
its orbits per class is a different question from the issue's index.  That
distribution -- which 7 of the 23715 classes carry an orbit of `Γ_{Co,2}` -- is
owed and is not claimed here.
