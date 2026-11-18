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
repair is a different change at the same owner, landed after this note was
first written: the walk spells each lift as a word in the ambient family, so the
registry now keeps **the word** and the finite element, and spells the integral
lift where a consumer asks for one -- the relation asks at no plane but the
`check_move` plane, and the coverings at theirs.  Section 6 is that change.

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

## 6. The peak's repair: the registry keeps the word, not the product

The walk that reaches a double coset composes one ambient generator per edge of
its own tree, and the double coset is spelled by the word section, so every lift
it yields is *already* a word: the product's integer entries grow with the plane
only because the product is taken.  A registry that keeps the product costs
9.2 KiB an entry where a row starts and ~18 KB a plane in its tail bands; the
word costs what a tuple of small integers costs, and the isometry is spelled
where something is transported by it.

`register_isotropic_lift` therefore takes the lift's `spelling`
(`_LiftSpelling`: the signed one-based letters into the ambient generating
family, in left-to-right product order, and the sign sheet's kernel witness
where the lift is that sheet's), and `_registered_isotropic_split_of_span`
spells the product on demand (`_spelled_lift`).  The walk yields the word beside
the lift only when asked (`spellings=True`), records it along its own tree, and
releases it with the values it already releases.  The divided-class relation
reads the **finite element** a plane
(`registered_isotropic_discriminant_of_span`) and spells an integral lift only at
the planes that make the `check_move` comparison; `isotropic_lift_discriminant_of`
gained the same read.

**Measured** (`.tmp/issue381b/probe-registry.py`, `registry-200.log`, the same
lattice, the same 200 planes, the same process shape as `#599`'s drop
measurement):

| what the registry keeps a plane | bytes |
| --- | ---: |
| the word (`_LiftSpelling` with its letters) | **150 B** |
| the product, as `#599` measured it | 9 200 B |
| at 189720 planes | **28.5 MB** against **1.67 GiB** |

The word grows one letter an edge of the walk's tree -- eight bytes a letter --
so a plane at depth `d` costs about `60 + 8d` bytes against a product whose
entries grow multiplicatively with the same `d`.  The drop-and-read measure that
priced the product frees nothing measurable here (-8 B a plane over 200 entries:
the entries are small and the allocator does not return the pages), so 150 B is
the number, taken directly from what the registry holds.

**What decides it.**  Two assertions in
`tests/lattices/test_a_cusp_names_its_plane_by_span.sage` fail if a word spells
something other than its lift: the character image of the spelled lift is the
finite element registered beside it (`quotient.image(lift)["discriminant"]`),
and the composite `s_2 s_1^{-1}` of two planes' spelled lifts carries the first
cusp's plane into the second.  The walk also checks, once per row, that the word
it hands the registry spells the very lift it yields, and raises instead of
registering a word whose product carries the source plane elsewhere.  On
`U + U(2) + <-2>` both kernel rows still decide 4 edges over 3 line and 2 plane
cusps with the ordered endpoint digest `47249bbc…`, unchanged.

**The sign sheet's half of a spelling is not exercised here.**  A spelling
carries the kernel witness a sign sheet's lift is multiplied by, and none of the
lattices a test or a short probe can afford registers one: `U + U(2) + <-2>`,
`U + U(2) + <-4>`, `6JRS` and `U + U + <-4>` each register 0 such entries
(`probe-spelling.py`, `spelling-small.log`, `spelling-uu24.log`).  That row is
`Otilde+`'s on `T_Co` and on the Scattone lattices, which are the rows this
issue is about.  The walk therefore checks that sheet too, once per row, against
the lift it yields -- and says so where it does -- so a registry of `Otilde+`
words never silently holds a witness on the wrong side.

## 7. Why two rows do not share this VM

The two rows of this issue cannot run together on a 15 GiB machine, and the
reason is two numbers, not a preference:

| row | peak tree RSS | where the number comes from |
| --- | ---: | --- |
| `Otilde`/`Otilde+` after both repairs | **~3.4 GiB** | projected from the measured per-plane terms: 0.71 GiB standing, ~0.8 GiB of GAP walk workspace, ~9 KB a plane of cusp row (1.7 GiB at 189720), 0.2 GiB of relation records. No run of it has returned yet to confirm the total. |
| the stage-1 cusp computation (`p12_plane_cusps`) | **5.8 GiB** | that job's own measurement, on its own chat |

Together that is 9.2 GiB of row on a machine whose other tenants hold 5–10 GiB,
so the kernel's killer — which fires at about 1 GiB of `MemAvail` — takes
whichever process is largest.  The stage-1 frontier has priority, and a row is
launched only when `MemAvailable` exceeds the row's own peak plus 1 GiB
(4.4 GiB for the figure above), which is the floor the kernel acts on; a check
of a process name is not, because a restarted or renamed job still holds the
memory.

## 8. Which allocation dominates the peak

Everything below is from measurements already taken -- `#599`'s row marks and
drop test, and this note's two probes -- not from a new run.

| term | bytes a plane | at 189720 planes | where it is measured |
| --- | ---: | ---: | --- |
| **the cusp row** (`_ArithmeticCuspEngine`, one owned object a plane, beside `_distinct_finite_ordered_set`'s admitted tuple and its identity table) | **~9 000** | **~1.66 GiB** | the split's own marks less the registry: 16.1-18 KB a plane total against 9.2 KiB of product |
| the transversal's GAP workspace (`FactorCosetAction`, the coset walk's lists, `DoubleCosets`' residue) | -- | **~0.88 GiB** | 887 MiB between the pre-split mark and the mark after 200 planes, of which the planes' own datums are ~4 MiB |
| the standing row (527 line cusps, the ambient plane row, the subgroup and its character quotient) | -- | **0.71 GiB** | `#599` §5, 709.9 MiB at 866 s |
| the relation's records (`DividedClassCuspIncidence`, 569160 of them) | 394.5 B an edge, three a plane | **0.21 GiB** | `#599` §2, counted with the record's set, its strings and its slot in the row's two tables |
| the lift registry, now words | 150 B | **0.028 GiB** | section 6 (`registry-200.log`) |
| the lift registry, before section 6 | 9 200 B | 1.67 GiB | `#599`'s drop test |

The sum is **~3.5 GiB**, which is the ~3.4 GiB the last row reports.  **The
dominant allocation is the cusp row**: 1.66 GiB, 48% of the peak, and it is the
only term over a gigabyte that no repair of this issue has touched.

What is *not* separated, and is the one thing the next window should not spend
itself re-deriving: inside that 9 KB a plane, the split between

* the **owned cusp object** -- `_object_of(Sets(), _engine=(Sets(),
  _ArithmeticCuspEngine, None), subgroup=..., span=..., subobject_rank=...)`,
  which carries its defining-construction tuple, its constructing category and
  the parent machinery above it (`categories/isotropic_orbits.py`,
  `_arithmetic_cusp`), and
* **`_distinct_finite_ordered_set`'s two tables** -- the `admitted` tuple and the
  `{id(point): position}` map the row's ingress builds
  (`categories/sets/finite_ordered_sets.py`), plus whatever
  `FiniteOrderedSets().from_indexed` keeps of them,

is unmeasured: the 9 KB is the difference of two row-level marks, and either
term could be most of it.  One probe decides it and costs one split: drop the
ingress's tables and read the resident set, then drop the cusps and read it
again.  Until that is done, no allocation inside the cusp row is attributed, and
the row's peak cannot be lowered by editing either side on a guess.

## 9. What was run, and what was not

Run, off a worktree of `3998bd8` carrying only this change:

* the per-plane probe above (`growth-200.log`, 200 planes, 1449 MiB peak);
* `tests/lattices/test_a_cusp_names_its_plane_by_span.sage`: **3 passed in
  45.23 s**, its slowest call the row's own two-plane build;
* the driver on `U + U(2) + <-2>`, both kernel rows: **`Otilde` and `Otilde+`
  each 4 edges over 3 line cusps and 2 plane cusps**, the four endpoint pairs
  `L0 < P0`, `L2 < P0`, `L0 < P1`, `L1 < P1` and the ordered endpoint digest
  `47249bbc…` -- the small-lattice value #381 records, unchanged by either
  repair;
* the two-route gate, `test_the_incidence_decided_by_divided_classes.sage` with
  `test_a_row_computes_one_plane_covering.sage`: **5 passed in 185.17 s** -- the
  divided-class relation, the certificate relation and the subgroup's own flag
  row are one relation on this tree as they were on the parent.

Run for section 6, on the tree carrying both repairs:

* `probe-registry.py`: **150 B a plane** in the registry's words over the first
  200 planes of `Otilde(T_Co)`'s split (`registry-200.log`, 200 planes drawn in
  472.7 s, 1295 MiB), the same probe shape `#599` priced the product with;
* `tests/lattices/test_a_cusp_names_its_plane_by_span.sage`: **3 passed in
  38.96 s**;
* the driver on `U + U(2) + <-2>`, both kernel rows: 4 edges each, the digest
  `47249bbc…` that the tree before this change prints;
* the two-route gate on the same tree, run again after the rebase:
  **5 passed in 172.01 s** -- the divided-class relation, the certificate
  relation and the subgroup's own flag row are one relation on the tree both
  repairs are published on.

Not run, and not reported: **either kernel row at 189720 planes.**  The host
cannot carry one now: the completed relation needs ~5.4 GiB against 4-6 GiB of
`MemAvailable` on this shared 16 GiB machine (other projects hold 8-10 GiB), and
the killer fires at ~1 GiB.  A row launched now dies in its split and takes an
hour to say so.  Its counts are the independent integral certificate's
`(569160, 527, 189720)`, which the driver checks and which this note does not
re-derive.

Five attempts of that row are on `main` already: killed at 3400, 3956, 4803,
4982 and 5490 MiB, every one with `MemAvail` at about 1 GiB and `/proc/vmstat`'s
`oom_kill` 43 -> 50 across them; the fifth reached 180 000 of 189 720 planes at
2003 s and 3908 MiB, so the split's own term is the one measured above and the
row's own length was never the question
(`results/issue599-the-plane-split-streams-into-the-walk.md`).  **One `Otilde`
row is started off this change as a job that reports later**
(`.tmp/issue381b/probe-row.py`, one process, the driver's own caps 10800/28800,
the 6144 MiB guard, launched on 9.2 GiB of `MemAvailable`); its count, its
coverage clauses and its peak are the run's own numbers, and they are appended
here when it returns.

## Provenance

`main` `3998bd8`; adopted runtime Sage 11.0.beta5; port `991b88b0` (the `T_Co`
construction: D. Dolgachev and S. Kondō, Izv. Math. 77:3 (2013), §3, eq. (3.6),
printed p. 513).  Probes, launchers and logs: `.tmp/issue381b/`.
