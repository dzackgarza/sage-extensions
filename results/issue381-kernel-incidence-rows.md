# The `Otilde(T_Co)` and `Otilde+(T_Co)` incidence rows (#381)

What #381 still owed after #390 and #391 closed: the incidence of the two
kernel plane rows of `T_Co` -- `Otilde(T_Co) = ker rho` and
`Otilde+(T_Co) = ker(rho, sn_RR)`, the 189720-plane rows of #390 -- with the
line rows of #357, each edge joining a line that lies in its plane.

## What this round delivered

* `tests/coble_gamma_co_2_incidence_rows.py` now runs the two kernel rows
  (`--rows 'Otilde,Otilde+'`), through the public
  `tits_building_incidence()`, asserting for every edge that its line term
  lies in its plane term and that one subgroup element carries the selected
  line cusp representative into the selected plane cusp representative, that
  no two edges share their cusp endpoints, that no cusp of either row is
  isolated, and that the relation is the subgroup's own flag row read as
  endpoint pairs.  Each row's edge count is printed per group and in one
  `recorded counts:` line.  `--lattice` runs the same code on a lattice the
  per-test gate can afford.
* `results/coble-kernel-incidence-rows.yml` is the dispatchable job;
  `tests/lattices/test_the_kernel_incidence_rows.sage` gates the same
  guarantees on `6JRS = U + U + <-2>` and `U + U(2) + <-4>`.

## Dispatching the T_Co rows

```
mkdir -p .github/workflows && cp results/coble-kernel-incidence-rows.yml .github/workflows/
```

then dispatch **Coble kernel incidence rows (#381)** with

| input | value | meaning |
| --- | --- | --- |
| `rows` | `Otilde,Otilde+` (default) | the two kernel rows |
| `lattice` | `Tco` (default) | `T_Co` itself |
| `cap` | `10800` (default) | seconds one row may take before it is *undecided* |
| `budget` | `28800` (default) | seconds for the whole run |

`rows: "O,Gamma_{Co,2}"` re-runs the two decided rows of #391 (one edge; 13
edges over 4 line and 7 plane cusps), and `lattice: "6JRS"` runs the
small-lattice check, which must exit 0.  `--lattice` also names
`U+U+<-4>`, `U+U(2)+<-2>` and `U+U(2)+<-4>`.

## Measured on the pinned image (the head this pushes)

| run | result |
| --- | --- |
| driver, `--lattice 6JRS` | 1 edge over 1 line and 1 plane cusp for each kernel row, then agreement with the ambient rows, exit 0 |
| driver, `--lattice 'U+U(2)+<-2>'` | 4 edges over 3 line and 2 plane cusps for each kernel row, exit 0 |
| driver, `--lattice 'U+U(2)+<-4>'` | 6 edges over 4 line and 3 plane cusps for each kernel row, exit 0 |
| gate file, three tests | **3 passed in 62.84 s**, the longest call 21 s over the 20 s gate |
| the #391 `T_Co` incidence gate file | **2 passed in 1696.37 s** -- `Gamma_{Co,2}` 1685.31 s, `O(T_Co)` 10.11 s |

That last row is the cost witness, and it is new: on `main` before this round
the same file raised `NameError` in its first line row, so it had never run to
completion.  `Gamma_{Co,2}` -- four line cusps, seven plane cusps, thirteen
edges -- costs 28 minutes, and almost all of it is the per-flag cusp matching:
the incidence call matches every flag's line against every cusp of the line
row, and a probe the divided-class invariant does not separate falls through to
the exact isometry search.

## The repairs this row needed first

Neither kernel incidence row could return on `main` when this round started,
and neither could #391's:

* `488f06f` (#390) deleted `_isotropic_line_class_points` and left its two call
  sites, so every subgroup line row raised `NameError`; the function is
  restored verbatim from `1da602e`, the commit that added it;
* `2291235` (#531) made a finite ordered set identify its points through
  `dict.fromkeys`, which the two incidence record classes cannot enter because
  they define no `__hash__`; each now carries the equality its own docstring
  states plus a hash that agrees with it (constant over its owner, as the
  category prescribes for a point whose owner has no canonical hash).

Two defects of other routes were found and are **not** repaired here, because
they are not this row's: `flag_stabilizer` passing `description=` where #537
requires a nullary `stated_clause` (the base of this push carries the repair,
made independently while this round ran), and the same function inverting a
basis change of the rank-two zero-form reduction lattice of
`U + U(2) + <-2>` whose determinant is `-2`, which is why that lattice is the
driver's and `U + U(2) + <-4>` is the gate's.

## What is *not* decided, and why

The two kernel rows on `T_Co` are the dispatched job's to decide against its
per-row cap, and on the measured rate they will come back **undecided**, not
failed.  The measured rate is the `Gamma_{Co,2}` row above: 1685 s for four
line cusps and seven plane cusps.  The kernel rows add a line row of 527
cusps and a plane row of 189720 planes, and the incidence call matches every
flag's line against every cusp of the line row, so the matching alone is
`527 × flags × 189720` probes.  The next repair is named, not taken here: the
cusp matching should be indexed by the divided-class invariant that
`invariant_separates_isotropic_orbits` already computes, so that a probe the
invariant separates costs no exact search; for a group whose discriminant
image is trivial -- both kernel rows -- the invariant is a complete decision,
because the class set of an isotropic line is then `Gamma`-invariant.

The cost is therefore in the incidence call's cusp matching and not in the
plane rows of #390, and that is the finding this round's measurements carry.
