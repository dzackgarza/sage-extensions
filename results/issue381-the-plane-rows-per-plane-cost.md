# The kernel plane row's per-plane cost, and the call that grows with the planes before it

One row of `T_Co`'s two kernel incidence rows is 189720 planes and 569160 edges.
Its *time* fits the driver's 10800 s cap with room: `Otilde(T_Co)`'s relation
returned 569160 edges in 3014.9 s inside a 4369 s run (`#599`,
`results/issue599-the-plane-split-streams-into-the-walk.md`).  What does not fit
is the host: that run peaked at **5408 MiB** and the kernel's killer takes the
largest process when `MemAvail` reaches about 1 GiB, which on a shared 16 GiB
host it does.  This note measures what a plane of the row costs, separates the
term that grows with the planes already processed from the terms that do not,
and lands the repair of the largest term the row's own calls pay.

All measurements: the adopted runtime (Sage 11.0.beta5), the port `991b88b0`,
`main` `3998bd8`, one process, the row's own calls (`PROBE_PLANES=200`,
`.tmp/issue381b/probe-growth.py`, `growth-200.log`).

## 1. What a plane costs, split into construction and computation

Two numbers, because the row has two halves that do different work.

**Construction** -- the split: `transport_isotropic_object` of the source plane
by the walk's lift, `register_isotropic_lift`, and the cusp made from the
transported plane (`_yield_subgroup_isotropic_orbit_representatives`).  Measured
over the 200 planes the walk yields first, in bands of 20:

| | first 20 | middle | last 20 |
| --- | ---: | ---: | ---: |
| transport + registration + cusp | **14.693 ms** | 9.266 ms | 13.173 ms |

**Computation** -- the relation's per-plane body, replayed on the same 200
planes in the relation's own order (`tits_building_incidence_by_divided_classes`,
per plane and per covering position), each step timed apart:

| step | first 20 | middle | last 20 | the row pays it? |
| --- | ---: | ---: | ---: | --- |
| `plane_cusp.representative()` (rebuild from the span) | 6.284 | 5.589 | 4.182 | **yes** |
| `_span_key(plane)` (the registry's key, derived back) | 0.892 | 0.927 | 0.791 | **yes** |
| `registered_isotropic_lift(plane)` (the dictionary hit) | 1.642 | 1.024 | 0.787 | yes |
| `~reference_lift` | 0.059 | 0.002 | 0.002 | no: `check_move` is lazy |
| `target_lift * ~reference_lift` | 1.328 | 0.965 | 0.783 | no: `check_move` is lazy |
| `_composite_divided_class_action` (finite action on `A_L`) | 2.360 | 0.571 | 0.485 | yes |
| `_carried_divided_classes` (GAP's setwise action) | 0.035 | 0.024 | 0.025 | yes |
| `isotropic_class_orbit` (recorded by class set) | 0.038 | 0.017 | 0.029 | yes |
| **whole body** | **9.268** | | | 8.3 ms of it |

The rebuild and the key derived from it are **5.0-7.9 ms of the 8.3 ms the row
pays per plane**: `plane_cusp.representative()` builds a primitive isotropic
plane out of the span the cusp holds, and `registered_isotropic_lift(plane)`
then derives that same span back to look the plane's lift up in a registry
**keyed by the span**.  Nothing at that plane is read from the plane.  The
relation's arithmetic -- the finite action, the carried classes, the orbit
record -- is 0.5-2.4 ms, and `#599`'s record of walked class sets is what keeps
it there (three GAP orbit walks a plane became three dictionary hits).

## 2. Which call grows with the planes already processed

Not one of the relation's.  Replayed over 200 planes its body is flat to
slightly *falling* in every step, and the split's intervals are flat too, so a
200-plane slice cannot see the growth at all -- which is why the growth has to
be named from the row's own length.

It is **`register_isotropic_lift`** (`categories/orthogonal_quotients.py`), the
span-keyed registry the split fills and the relation reads, and the mechanism is
what it keeps: one **owned integral lift** per plane.  A lift of a kernel row is
a word in the ambient orthogonal group's generators spelled along the walk's own
tree (`_iter_splitting_isometries_in_im_rho_from_image`), and the word grows
with the double coset the walk has reached, so the lift's integer matrix grows
with it.  The row's own marks show it: the entry is **9.2 KiB** where the walk
starts and the row's last bands sit at **~18 KB a plane** (`#599`, section 5,
and the entry measured by dropping the registry, `attribution.log`).  At 189720
planes that is **1.67 GiB as a lower bound and ~3.4 GiB at the tail bands**, on
a 0.71 GiB standing row: this is the row's peak, and it is a cache keyed by
something that grows with the walk.

The whole per-plane split, for the record: 189720 planes at the measured rates
are ~1900 s of construction and ~1570 s of computation, and with the line row
(200-315 s), the transversal (~190 s) and the contract step (~801 s before the
driver bounded its printing) the row is **~4300 s against the 10800 s cap** --
4.4x inside it.  The row that "cannot return inside the cap" cannot return
inside the *host*.

## 3. The repair landed: the row reads its lift by the span its cusp holds

`OrthogonalCharacterQuotient.registered_isotropic_lift_of_span(span)` is the
registry's read at the key the row actually holds, and
`_registered_isotropic_split` is now that read with the span derived for a
plane-keyed caller.  `tits_building_incidence_by_divided_classes` asks by
`plane_cusp.span()` and no longer reconstructs the plane; the one per-plane
comparison that needs a lattice element -- the carried line's own classes, at
the planes that make it -- still builds the one element it transports.  The
covering's reference plane is compared by span rather than by object identity,
which is the same answer for the row's own cusps and the right one for an
equal-but-distinct copy.

That removes **5.0-7.9 ms of the 8.3 ms a plane** the row's relation pays --
**950-1500 s** of the row's calls -- and 189720 constructed planes from the
relation's path.

**It does not lower the peak.**  The peak is section 2's registry, and its
repair is a different change at the same owner: the walk spells each lift as a
word in the ambient family, so the registry could retain **the word** (a tuple
of edge letters, hundreds of bytes) and the finite element, and spell the
integral lift where a consumer asks for one -- the relation asks at no plane but
the `check_move` plane, and the coverings at theirs.  That changes the walk's
protocol and every registration site, and it has to be verified on a row of the
row's own length; it is not in this change.

## 4. The contract the read rests on, and why it is not a red

The registry is keyed by `_span_key(plane)`; a cusp holds `_span_key` of the
representative it was made from, and the plane `representative()` rebuilds from
that span derives the same key back.  The test landed with this change asserts
exactly that, on `U + U(2) + <-2>`'s `Otilde` plane row (two cusps): each cusp
answers one registered lift through the span and through the rebuilt plane, the
lift is an isometry of the row's lattice whose character image is the finite
element beside it, and the composite `s_2 s_1^{-1}` carries the first cusp's
plane into the second.

It is a **contract, not a red**, and said so rather than manufactured: the
parent answers the same lift, and what the repair removes is a reconstruction
and not a wrong answer.  The red that would exist -- the span-keyed call is
absent at the parent -- is an `AttributeError` for the missing fix, which is
not a red.

## 5. What was run, and what was not

Run, off a worktree of `3998bd8` carrying only this change:

* the per-plane probe above (`growth-200.log`, 200 planes, 1449 MiB peak);
* `tests/lattices/test_a_cusp_names_its_plane_by_span.sage`: **3 passed in
  45.23 s**, its slowest call the row's own two-plane build;
* the driver on `U + U(2) + <-2>`, both kernel rows: **`Otilde` and `Otilde+`
  each 4 edges over 3 line cusps and 2 plane cusps**, the four endpoint pairs
  `L0 < P0`, `L2 < P0`, `L0 < P1`, `L1 < P1` and the ordered endpoint digest
  `04c17f79…` -- the small-lattice value #381 records, unchanged by the repair;
* the two-route gate, `test_the_incidence_decided_by_divided_classes.sage` with
  `test_a_row_computes_one_plane_covering.sage`: **5 passed in 185.17 s** -- the
  divided-class relation, the certificate relation and the subgroup's own flag
  row are one relation on this tree as they were on the parent.

Not run, and not reported: **either kernel row at 189720 planes.**  The host
cannot carry one now: the completed relation needs ~5.4 GiB against 4-6 GiB of
`MemAvailable` on this shared 16 GiB machine (other projects hold 8-10 GiB), and
the killer fires at ~1 GiB.  A row launched now dies in its split and takes an
hour to say so.  Its counts are the independent integral certificate's
`(569160, 527, 189720)`, which the driver checks and which this note does not
re-derive.

## Provenance

`main` `3998bd8`; adopted runtime Sage 11.0.beta5; port `991b88b0` (the `T_Co`
construction: D. Dolgachev and S. Kondō, Izv. Math. 77:3 (2013), §3, eq. (3.6),
printed p. 513).  Probes, launchers and logs: `.tmp/issue381b/`.
