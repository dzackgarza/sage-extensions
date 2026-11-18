# The plane row as one stream: the walk, the cusp, the edges, the lift spent

A kernel plane row of `T_Co` is 189720 planes.  The split registers a lift a
plane and the relation reads a plane's lift once and never asks again, so the
two halves were one pass of work held apart by a `list`: the split filled the
registry, and only then did the relation start releasing it -- which frees memory
from the *second* plane onwards and never the peak, since the peak is the moment
the split has finished.

This change fuses the two.  `divided_class_incidence_of_planes` is the relation's
per-plane body, public, reading its planes lazily; the walk yields a plane, the
plane's cusp is made from it, its edges are decided from the covering the row has
carried so far, and the plane's lift is released by the plane it belongs to.  The
covering is seeded at the planes the caller streams instead of in a pass over the
row, and the whole relation (``tits_building_incidence_by_divided_classes``) is
that call composed over the subgroup's own cusps -- one body, two callers, not a
second algorithm.

## What the fusion has to get right, and does

* **The covering need not be seeded at the first plane.**  On
  `U + U(2) + <-2>` two ambient flag orbits are carried, and the isotropic
  equivalence witness fails at the first plane for one of them.  So a plane
  reached before the coverings are complete is *held* -- its span and its finite
  element, which is all its own edges need -- and decided at the plane that
  completes them.  The caller sees every plane of the row with its own edges, in
  the row's order.
* **A plane's lift is released after its edges, not before.**  One plane per
  covering position spells an integral lift, to check the finite image's action
  against the carried line's own classes; releasing on arrival made that read
  `None` (`TypeError: 'NoneType' object is not subscriptable`).  The release is
  therefore keyed to the plane's decision, which for a held plane is a plane
  later -- so the resident set is the cusps, the records and the held planes, and
  never the whole registry.
* **The relation spends the registry.**  Asking it twice of one subgroup finds no
  registered lifts the second time; that is the release working, and it is why
  the test's second route is taken on another presentation of the lattice.

## What was run

The adopted runtime, `U + U(2) + <-2>`, every run under `peakrss.py`:

| instrument | what it returned |
| --- | --- |
| `probe-fused-row.py`, the `Otilde` row (`fused-small.log`) | 2 plane cusps, 3 line cusps, 4 edges, **decided**, digest `47249bbc0b3c3303…`, **519 MiB** |
| the driver, both rows (`fused-driver-small.log`) | 4 edges over 3 line and 2 plane cusps each, digest `04c17f79b45ca82a…` -- the parent's value on this tree |
| `tests/lattices/test_the_divided_class_relation_is_decided_one_plane_at_a_time.sage` | **3 passed in 42.66 s**, 647 MiB |
| `tests/lattices/test_the_incidence_decided_by_divided_classes.sage` | the two-route gate, unchanged |

The fused probe's digest differs from the driver's because the two drawings of
the row name their cusps differently, not because the rows differ: the counts,
the endpoint pairs and the contract's verdict agree, as
`results/issue381-the-kernel-row-checkpoint.md` records for the two-process run.

## What is not measured

`T_Co`'s own peak under the fused row, and this is now a two-term question rather
than a projection.  The registry is no longer held -- 1.67-3.4 GiB of the row's
former peak -- but the cusp row is, and the stage-1 line has just measured that
row alone at **189720 cusps in 2171.0 s at 3476.4 MiB** (`c6bfbae`, item 5 of
the stage-1 call).  So the fused row's floor is that 3476 MiB plus the 569160
edge records, and what the fusion buys is the registry term on top of it, not a
small row: the run that would give the number is ~70 minutes and is a background
run, not this note's.

Provenance: `main` at the commit this lands on; port `991b88b0`; probes and logs
under `.tmp/issue381b/`.
