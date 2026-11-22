# Card 0128's Table 4 `#Γ̄_h` rows, one row per process

The seeding repair (`364ab82`) makes the flag leg of a subgroup row decide, and
`0128:#Gamma_h:2` then returned the card's triple in 252 s.  This note records
the same module run over the degrees that were still `UNDECIDED` at the 1800 s
per-row cap, one row per process, each under the same cap, and compares each
value with its card.  Nothing here repairs the ambient `O(T_En)` flag row.

## How a row was run

    python3 tests/enriques_polarization_rows_by_card.py --one '0128:#Gamma_h:N' --cap 1800

for `N` in 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, in that order, one process each,
in the pinned image (Sage 11.0.beta5) with the port the image carries at
`54d12c2`, at `acb675c`.  A row's expected value is the card's, read by tag from
`tests/cards/lattice-database-enriques.json`; the row's stage record is that
process's own `.timings/stages-*.jsonl` (CONTRIBUTING.md ENV-03), so the split
below is the run's, not a wrapper's.

The row's definition is the module's: `#h` is
`O(U + E8(-1)).vector_orbit_representatives(2d).cardinality()` and `#Γ̄_h` is the
number of distinct triples of `Γ_h`-orbit counts of primitive isotropic lines,
planes and flags over that degree's classes.

## Where a row's time goes

A row builds one `Γ_h` per class of primitive vectors of square `2d` and asks
each for its three orbit counts, so a row's cost is a sum over classes.  The row
`0128:#Gamma_h:4` (two classes, `PASS`, 418.3 s) splits as:

| stage | class 1 | class 2 |
| --- | --- | --- |
| ambient `O(T_En)` line row | 6.86 s | 0.00 s |
| line split under `Γ_h` | 28.58 s | 2.99 s |
| ambient `O(T_En)` plane row | (in the split below) | 1.67 s |
| plane split under `Γ_h` | 20.02 s | 3.27 s |
| ambient `O(T_En)` flag row | **148.82 s** | **144.41 s** |
| flag split under `Γ_h` | 30.89 s | 12.60 s |
| leg totals (lines, planes, flags) | 35.45, 25.28, 179.71 s | 3.00, 4.95, 157.03 s |

The line and plane ambient rows fall to nothing on the second class of the same
lattice — the line row's classes come from the port's cached
`primitive_vector_classes`, and the plane row is `T_En`'s certified pair of
plane classes — while the flag ambient row is paid again in full: 148.82 s and
then 144.41 s for the *same* six-dimensional flag row of the *same* lattice.
`isotropic_orbit_representatives` and the port's `primitive_marking_classes`
behind it are not cached, so a row with `n` classes pays that row `n` times.

The flag ambient row is also the only term that does not follow the group: the
two classes' flag splits differ (30.89 s against 12.60 s) because their groups
have different numbers of flag orbits, while their ambient rows are the same
~146 s.  So the row's cost is `n × ~146 s` of ambient flag row plus a split that
follows the flag count at roughly a second an orbit.

## The rows

Every value is the card's.  `#h` is the card's number of `O(U + E8(-1))`-classes
of primitive vectors of that square, so it is also the number of `Γ_h` groups the
row builds; `#Γ̄_h` is what the row computed and what the card states.

| `2d` | classes (`#h`) | expected `#Γ̄_h` | computed | row | flag ambient rows | share |
| ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 4 | 2 | 2 | 2 | 418.3 s | 148.8, 144.4 | 70% |
| 6 | 2 | 2 | 2 | 404.8 s | 147.8, 141.4 | 71% |
| 8 | 2 | 2 | 2 | 396.2 s | 145.9, 141.1 | 72% |
| 10 | 3 | 3 | 3 | 372.2 s | 89.2, 82.6, 84.3 | 69% |
| 12 | 4 | 3 | 3 | 584.9 s | 110.9, 105.4, 107.2, 106.8 | 74% |
| 14 | 3 | 3 | 3 | 448.4 s | 109.0, 104.0, 103.7 | 71% |
| 16 | 4 | 4 | 4 | 574.0 s | 110.2, 102.7, 101.7, 105.4 | 73% |
| 18 | 4 | 4 | 4 | 723.7 s | 147.7, 138.5, 142.7, 142.0 | 79% |
| 20 | 5 | 4 | 4 | 887.4 s | 145.4, 141.9, 143.1, 139.7, 138.6 | 80% |
| 22 | 5 | 5 | 5 | 779.6 s | 110.3, 106.2, 112.2, 139.5, 120.2 | 75% |

Rows 12 and 20 are the two degrees in this set where the card's `#h` exceeds its
`#Γ̄_h`, that is, where two classes of primitive vectors give conjugate groups:
the row's invariant reproduces the card's number there too (4 classes, 3 triples;
5 classes, 4 triples), so the three orbit counts separate exactly the classes the
card says are distinct.

No row missed its cap; the longest is 887.4 s at `2d = 20`, against 1800.  Peak
resident memory per row was 1.18 to 1.58 GB.

## The ambient flag row against the flag count

Across the 32 classes of these ten rows the ambient `O(T_En)` flag row was called
34 times and cost between **82.6 s and 148.8 s**.  It is the largest single term
of every row: 69% to 80% of the row's total.

All 34 calls carry the *same* input string -- `the flag row with dimensions (1, 2)
of the rank-12 lattice ... under O(L)` -- so neither the group nor its flag count
enters the call at all, and the spread is not the input's.

It does not follow the flag count either.  Within a row the classes' ambient rows
agree to within about 7% (degree 20: 138.6, 139.7, 143.1, 141.9, 145.4 s) while
the work left after them differs by class: at degree 12 the four flag legs are
139.6, 116.1, 117.7 and 118.1 s, whose ambient rows are 110.9, 105.4, 107.2 and
106.8 s, leaving splits of 28.7, 10.7, 10.5 and 11.3 s -- a threefold spread
under an ambient row that itself varies by 4%.  The ambient row is one
`O(T_En)`-orbit of a flag of `T_En`; the split is what follows the group's flag
count, at roughly a second an orbit.

What moves the ambient row between rows is not established here.  The load
average at each row's start was 0.92 to 1.33, one runnable process on four CPUs,
and the dearest rows are not the ones that started under the heaviest load.  The
34 calls fall into two clusters: degrees 4, 6, 8, 18 and 20 have every class at
138.5-148.8 s, degrees 10, 12, 14 and 16 every class at 82.6-110.9 s, and degree
22 has four classes at 106.2-120.2 s and one at 139.5 s.  No cause is claimed.

## What is not repaired here

The ambient flag row itself.  It is `_isotropic_orbit_representatives`'s flag
branch handing the flag to the port's `primitive_marking_classes`, which has no
cheap certified route like the plane branch's, and it is recomputed for every
`Γ_h` class although it depends on the lattice alone — the line and plane rows
are already shared across a row's classes (0.00 s and 1.67 s on the second class
at `2d = 4`).  Making it once per lattice, or giving the flag branch a certified
classification of `T_En`'s flag classes, is the next unit and belongs to its own
issue, as does the port's `isotropic_stabilizer_action` failure on flags whose
top term has rank three.
## Where this sits in the volume

The objects are the volume's: the Tits building of a lattice of signature
`(2, n)` (`def:signature-two-tits-building`), whose edges are the primitive
isotropic flags this row counts; and the quotient of the building by a
finite-index subgroup, computed from the ambient quotient and a transversal
(`prop:dawes-building-descent`), which is the double-coset split each class
performs.  That the `Γ_h` fall into 87 classes and that the cusps are their
orbits of primitive isotropic lines and planes is `thm:sh23-enriques-moduli-groups`.
The numbers are D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Table 1 (the
87 groups) and card 0128's Table 4 (the degrees).  Nothing here departs from
those statements.
