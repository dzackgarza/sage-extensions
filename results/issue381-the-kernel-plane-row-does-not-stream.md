# The kernel plane row gathers its split: 74 KB a plane, and the guard at 6162 MiB

`tests/coble_gamma_co_2_incidence_rows.py --rows Otilde --lattice Tco --route
divided-class` does not return at `main` `da742b3`, one process, the driver's own
caps (`--cap 10800`, `--budget 28800`).  The 6144 MiB guard of this project's
heavy runs stops it at **6 162 MiB, 783 s in, with no row line printed**, and
the term is the plane row: `_plane_orbit_from_parabolic_stabilizer`
(`categories/orthogonal_quotients.py:3867-3874`) appends every transported
plane of the split to a list and returns the tuple, so all 189 720 planes of the
row are built and held before the first cusp exists.  Measured at **74.4 KB a
plane** on the row's own shape, and rising, that is **13.47 GiB** at the row's
length; the guard is reached at the 50 000th-60 000th plane.

The driver's two other terms do not eat anything: the line row returns, and the
contract step -- which nobody had priced -- is **4.22 ms and 3.6 KB a plane**,
flat over a thousand cusps, **801 s and 0.64 GiB** at the row's length, and it
runs outside the row's cap in any case.

All measurements on the adopted runtime (Sage 11.0.beta5), the port `991b88b0`,
`main` `da742b3`; probes, launchers and logs under `.tmp/issue381-rows/`.

## 1. The stages, in the driver's own order

One process, the row's three stages run through their own owners
(`probe-phases.py`, which names the frame the process is in every 30 s):

| stage | wall | resident after |
| --- | ---: | ---: |
| `T_Co`, `Otilde(T_Co)`, the character quotient | 0.1 s | 279.6 MiB |
| the line row, 527 cusps | 200.5 s | 978.4 MiB |
| the plane row, up to the guard | 550 s | 6 155 MiB |

The line row costs **1.33 MiB a line cusp** and returns.  The plane row emitted
no cusp before the guard: no per-10 000-planes line was ever printed, and the
stage grew at 11 MiB/s from 978 MiB to 6 155 MiB.  That is what a gather looks
like from outside -- the row's items exist only when the whole split does.

## 2. The term, at the owner

```python
representatives = []
for splitting, discriminant_image in quotient._iter_splitting_isometries_in_im_rho(family):
    transported = splitting.transport_isotropic_object(representative)
    quotient.register_isotropic_lift(transported, splitting, family, discriminant_image)
    representatives.append(transported)
return tuple(representatives)
```

The walk underneath is lazy -- `_iter_splitting_isometries_in_im_rho` yields the
lift and its finite element one at a time, and `splitting_isometries_from_line_class`
(the line row's split) is a generator expression -- and this consumer is what
throws the laziness away.  The function's own docstring says the opposite of what
it does: *"The lifts are consumed as they arrive: a kernel row numbers 189720 of
them, and holding every lift beside every transported plane doubles the row's
footprint for no mathematical content."*  The lifts were released; the planes
were not.  A cusp keeps a span, not a plane (`#588`, `_ArithmeticCuspEngine`), so
no consumer of the row needs the plane after its cusp exists.

This is also why `#584`'s 63 KB a plane and this row's death are one number and
`#598`'s 16.5 KiB a plane is another: `#598`'s curve rebuilt the per-plane steps
itself and **released** each transported plane (`del transported`) after making
its cusp.  The row does not release it.  Both arms are measured here.

## 3. The two shapes of the same split, and the contract step

One process an arm, 1 000 planes each, the same source plane, the same parabolic
family and the same walk (`probe-terms.py`).  "Gathered" is the row's shape;
"released" is the split streamed into cusps, which is what a cusp row needs.

| arm | ms a plane | first -> last band | KB a plane | at 189 720 planes |
| --- | ---: | ---: | ---: | ---: |
| gathered, as the row does | 6.785 | 6.348 -> 5.771 | 74.4 (69.6 -> 74.3) | **13.47 GiB** |
| released, as a cusp row needs | 6.086 | 6.367 -> 5.492 | 12.8 (20.2 -> 8.4 -> 12.1) | **2.31 GiB** |
| the contract step over those cusps | 4.223 | 4.329 -> 4.198 | 3.6 | **801 s, 0.64 GiB** |

* The two shapes cost the same time: 6.8 ms against 6.1 ms a plane, both flat
  (the second band is *cheaper* than the first in both arms).
* They do not cost the same memory: **74.4 KB against 12.8 KB a plane**, a factor
  of 5.8.  The released arm's residue is the lift registry (7.5 KB a plane,
  `#584`) plus the span a cusp keeps; the gathered arm's extra is the plane.
* The gathered coefficient **rises** with the row's length (69.6, 67.5, 70.1,
  71.6, 72.4, 73.1, 73.7, 74.0, 74.3 KB a plane at 100-plane marks), so 74.4 KB
  is the mean of the first thousand and a lower bound at 189 720.  The driver's
  own window agrees and is worse: the line row ended at 200.7 s, the transversal
  took ~190 s, so the plane row had ~360 s of building before the guard, which at
  6.785 ms a plane is ~53 000 planes, and the 5.2 GiB it gained over them is
  **~100 KB a plane**.
* The contract step -- `row_contract`'s `_coordinates(cusp.representative())` for
  every plane cusp, rebuilding the plane from its span -- is **4.22 ms a plane,
  3.564 ms of it the rebuild and 0.658 ms the coordinate read**, flat
  (4.329 -> 4.198 ms between the first and last hundred).  At 189 720 cusps that
  is **801 s and 0.64 GiB**: it fits the 6144 MiB guard with room, and it is not
  cap-bound at all, because `run_row` cancels the `setitimer` before calling
  `row_contract`.  Its 3.6 KB a plane is the weak `_primitive_isotropic_subobject`
  record's key (the spanning family), which is held strongly while the value is
  not.

## 4. Which cap the row would have met first

Neither: it met the guard.  At the measured rates the plane row's *time* is
`189720 * 6.785 ms = 1288 s`, and with the line row's 200 s and the transversal's
190 s the row's calls are **~1 680 s against the 10 800 s cap** -- 6.4x inside it.
The memory is what stops it, and not by a margin: 13.47 GiB of gathered planes
plus the 1.25 GiB the row stands on is 2.4x the guard and 0.85x this VM's
16 GiB, so no cap, no budget and no quieter machine changes the outcome.  A row
that dies at 6 162 MiB after 783 s with no row line printed has died in the plane
row; the line row had already returned and the contract step had not been
reached.

## 5. The wiring is not the question

The same driver on the same route on `U+U(2)+<-2>`: both kernel rows decided in
**24 s at 536 MiB**, `Otilde` and `Otilde+` each **4 edges over 3 line cusps and
2 plane cusps**, which is the small-lattice value #381 records.  The binder, the
import path and the class route are the ones the row takes on `T_Co` too -- its
own log says `divided-class, as the run asked`.  The failure on `T_Co` is
capacity.

## 6. What a streamed row would cost, and what would then be reportable

The released arm's coefficients, applied to the row as it is otherwise built:

| term | wall | resident |
| --- | ---: | ---: |
| the line row (measured, returns) | 200 s | 0.68 GiB |
| the transversal (measured) | 190 s | 1.27 GiB |
| the plane row, streamed (12.8 KB, 6.086 ms a plane) | 1 155 s | 2.31 GiB |
| the contract step (measured) | 801 s | 0.64 GiB |
| the edge loop | not measured at this length | `DividedClassCuspIncidence` is 1 427 B a record and a plane carries three |

so ~3.4 GiB before the edge loop and ~1 600 s of row, both inside the guard and
the cap.  **The edge counts and the witnesses per group are not reportable at
`main`** and cannot be made reportable by any cap: they need the split streamed
at its owner, and the edge loop's own memory measured at length once it is.

## 7. The dispatch shape

Two things, not one.  The single-process `rows=Otilde,Otilde+` shape is 2 x the
plane row and cannot run (this was priced before the run: 8.6 GiB against the
guard); **one row a job is necessary and not sufficient**, because one row alone
is the 13.47 GiB measured here.  A per-row job is worth having for the day the
split streams; until then any shape meets the guard in the plane row.

## 8. What was run, and what was not

Run: the driver row alone at `main` `da742b3` (one process, caps 10800/28800,
route `divided-class`), stopped by the guard at 6 162 MiB after 783 s; the same
driver and route on `U+U(2)+<-2>` (24 s, 536 MiB, both rows 4 edges over 3 line
and 2 plane cusps); the stage probe; and the three arms, one process each, 1 000
planes.

Not run: the `Otilde+` row, which was stopped after the first row's death because
it holds a plane row of its own and would meet the same guard; the edge loop at
length; the certificate route; any run with the guard raised, which is not a
measurement this project takes; the whole suite; and the ast-grep gates, which
are not installed on this host.

## Provenance

`main` `da742b3`, adopted runtime Sage 11.0.beta5, port `991b88b0` (the `T_Co`
construction of `#381`: D. Dolgachev and S. Kondo, Izv. Math. 77:3 (2013),
section 3, equation (3.6), printed p. 513).  Probes and logs:
`.tmp/issue381-rows/` -- `probe-phases.py`, `probe-terms.py`, the two launchers,
and `Otilde.log`, `phases.log`, `term-gather.log`, `term-drop.log`,
`term-contract.log`.
