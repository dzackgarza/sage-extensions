# The plane split streams into the walk

`Otilde(T_Co)`'s plane row -- 189720 primitive isotropic planes under
`ker rho` -- is the row of #381, and its resident set was never the relation's
or the cusp row's: the split built every plane of the row and returned them as a
tuple before the first cusp existed.  The split now yields.

All measurements are on the adopted runtime (Sage 11.0.beta5), the port
`991b88b0`, from a worktree of `f2c519c` carrying only the two repairs of this
issue; probes, launchers and logs under `.tmp/issue599/` of that worktree.

## 0. The acceptance, clause by clause

| clause of #599's acceptance | verdict | measured on |
| --- | --- | --- |
| the split yields its plane cusps to the walk without holding them all | **holds**: one draw, one plane (`U + U(2) + <-2>`, section 3) | `yield-new.log` |
| the relation's records are what a row keeps | **holds for this issue's term**: 394.5 B an edge, 0.21 GiB at 189720; the row keeps more (section 2 and section 5) | `record-size.log` |
| measured at 10 000, 50 000 and 100 000 planes as a flat resident set rather than a rising one | **flat for the relation** (4 379.0, 4 491.3, 4 448.1 MiB); **rising for the split** (`Otilde`: 1 297.3, 1 644.7, 2 536.7 MiB, ~18 KB a plane), and the rising term is the lift registry, #584's | `row-Otilde.log` |
| the row's edges equal the gathered route's on a slice both can still do | **holds exactly**: endpoint pairs and witnesses equal, 600 of 600 | `slice-wt2.log` |
| the two edge counts and witnesses per group at 189720 planes under 4 GiB | **the 4 GiB clause fails by measurement** (4982 MiB at 550 000 of 569 160 records); **the counts are not obtained**: both rows were killed by this host's OOM killer, and are queued to run again one at a time (section 5) | `row-Otilde.log`, `row-Otilde+.log`, `chain.log`, `gated.log` |

The registry term is **not** #584's any more: #584 is closed and its repair is why an entry is 9.2 KiB and not the 63 KB its body measures.  What remains is the *coexistence* of 189720 lifts -- the split filling the registry before the relation reads one -- which only a walk that drives the split itself removes.

## 1. The gather

`_plane_orbit_from_parabolic_stabilizer` (`orthogonal_quotients.py:3867-3874`
at the parent):

```python
representatives = []
for splitting, discriminant_image in quotient._iter_splitting_isometries_in_im_rho(family):
    transported = splitting.transport_isotropic_object(representative)
    quotient.register_isotropic_lift(transported, splitting, family, discriminant_image)
    representatives.append(transported)
return tuple(representatives)
```

The walk under it is lazy: `_iter_splitting_isometries_in_im_rho` yields one
lift and its finite element at a time, and the comment above the loop said the
planes were consumed as they arrive.  This loop is what threw that away.

What is held per plane, beyond the span the cusp keeps:

| datum | held by the parent | held now |
| --- | --- | --- |
| the transported plane | the `representatives` list, one constructed `PrimitiveIsotropic` parent each, which the construction caches above it retain for the process | nothing: the plane is the caller's to drop |
| the tuple slot | the returned tuple | nothing |
| the lift, its source parabolic family, its discriminant image | `register_isotropic_lift`, keyed by the plane's span | the same, unchanged (7.5 KB a plane, #584) |
| the cusp (span, rank, subgroup) | built after the gather, by `_arithmetic_cusp` | the same, built as each plane arrives |

Cost of the gathered shape, measured on this row's own split: **67.8 KB a plane
over the first 200 planes** and 74.4 KB a plane over the first thousand (the
latter in `results/issue381-the-kernel-plane-row-does-not-stream.md`), against
12.8 KB a plane for the released shape in the same note.  At 189720 planes that
is 13.47 GiB on 1.25 GiB of standing row.

## 2. The streamed form

`_plane_orbit_from_parabolic_stabilizer` keeps its guard -- the parabolic's
completeness, the index-one case, the character data it refuses without -- and
returns `_iter_transported_planes(quotient, representative, family)`, a
generator that transports, registers and yields one plane.  The caller
(`_yield_subgroup_isotropic_orbit_representatives`) already did
`yield from from_parabolic`; nothing else changes.

**What the index needs.**  `row_contract` prints the coordinates of every plane
cusp "by index", and its index is a position in the cusp row, not a plane: the
row is a `FiniteOrderedSet` of cusps, `cusp_positions` maps a cusp's identity to
its position, `len(planes)` is the row's cardinality, and every read of a cusp's
gestalt goes through `cusp.representative()`, which rebuilds the plane from the
span.  So the random access the contract step needs is answered by the cusp row,
which is spans -- and the rebuild is the 3.564 ms a plane that
`row_contract` already pays (801 s and 0.64 GiB at the row's length, measured in
`results/issue381-the-kernel-plane-row-does-not-stream.md`).  Nothing has to be
retained for an index to resolve.

### One draw costs one plane, on the smallest input that decides it

`U + U(2) + <-2>` has two plane cusps under `Otilde`, so its yielded orbit row
has two planes to give, and the split's lift registry holds the planes it has
built so far: the source it seeds, and one per drawn plane.  Drawing them one at
a time from `_yield_subgroup_isotropic_orbit_representatives`
(`orthogonal_quotients.py:4249`), which is the row `cusps(2)` consumes
(`predicate_subgroups.py:772`):

| draw | parent `f2c519c` | this tree |
| --- | ---: | ---: |
| before the row | 0 | 0 |
| after the first plane | **2** | **1** |
| after the second plane | 2 | 2 |

The parent's first draw bought both planes -- `return tuple(representatives)` at
`orthogonal_quotients.py:3874` of the parent is what a draw cost -- and this
tree's first draw buys one (`_iter_transported_planes`,
`orthogonal_quotients.py:3966-3987`, drawn by `yield from from_parabolic` at
`orthogonal_quotients.py:4316`).  `yield-parent.log`, `yield-new.log`.

### What a record of the relation costs a row

`DividedClassCuspIncidence` (`isotropic_orbits.py:1263`) retains two cusps --
which the row keeps anyway -- and the class pair that decided the edge.  On the
same lattice, whose two kernel rows are four edges each, one record measured
through the group's own relation (`predicate_subgroups.py:1177`) is:

| part | bytes |
| --- | ---: |
| the record itself | 48.0 |
| its divided-class set | 216.0 |
| the strings of that set | 54.5 |
| its slot in `points` and the relation's identity index | 76.0 |
| **one edge** | **394.5** |

Three edges a plane, as the covering has three lines: **0.21 GiB** at 189720
planes.  The issue's 1427 B a record would make that 0.76 GiB and #585's 121 B
a record 0.07 GiB; the difference is what each counted -- 394.5 B is the record
with its set, its strings and its slot in the row's own two tables.
`record-size.log`.

## 3. The two shapes are one row

One walk of `Otilde(T_Co)`, its first 200 double cosets, produced the row in
both shapes in one process: the parent's list-and-tuple, and the library's own
generator.

```
  the two rows' spans, in order:     EQUAL
  distinct spans: gathered 200, streamed 200
  the registry's record per span:    EQUAL
```

(`slice-200b.log`.)  Both rows then go through the library's own
`tits_building_incidence_by_divided_classes` -- the subgroup's `cusps(2)` cache
is cleared and seeded with the slice, and the seed is checked -- and the two
relations are compared edge by edge, by the pair of cusp positions each names
(positions resolved by span, since the two rows are equal spans and not shared
objects) and by the divided-class witness each record carries (`slice-wt2.log`,
`d89dc76`, clean tree):

```
  edges: gathered 600, streamed 600
  unresolved vertices: gathered 0, streamed 0
  the two relations' endpoint pairs: EQUAL
  the two relations' witnesses:      EQUAL
  distinct endpoint pairs: 600 of 600
  plane cusps carrying an edge: 200 of 200
  line cusps carrying an edge:  202 of 527
```

Three edges a plane, as the row's one covering has three lines; every plane cusp
of the slice carries an edge; 202 of the row's 527 line cusps are met by these
200 planes (the whole row must meet all 527, which is the contract's own clause
and is what the 189720-plane run checks).  The two relations are one relation,
down to the witnesses, so the streamed row is the row the gathered one was.

Through the driver on `U + U(2) + <-2>` the two trees print
the same relation: `Otilde` and `Otilde+` each 4 edges over 3 line and 2 plane
cusps, and the four endpoint pairs `L0 < P0`, `L2 < P0`, `L0 < P1`, `L1 < P1`
line for line (`smoke-parent-1.log`, `smoke-new.log`).  The cusp *coordinates*
differ between processes, because the ambient representative is chosen per
process; the relation does not.

## 4. The relation's own cost, which nobody had measured at length

`tits_building_incidence_by_divided_classes` asks
`isotropic_class_orbit` three times at every plane, once per line of the row's
covering.  That method is `cached_method`, but its argument is a live GAP set, so
the cache is keyed by the object and not by the class data -- and the
`rho(Gamma)`-orbit walk behind it costs about **20 ms** on this row's class sets
(600 walks in 16.2 s over a 200-plane slice).  The relation is therefore
**66-81 ms a plane**, and at 189720 planes it is **3.5-4.3 hours of calls
against the driver's 10800 s cap**: with the memory repaired, the row's own
relation is what the cap meets, and the two edge counts of #599 are not
reportable through it as it stands.

The second repair closes that: the orbit is a function of the class set's value,
the carried set is the divided class of a line and `A_L = (Z/2)^11` on `T_Co`
has 2048 classes, so the whole row asks about at most 2048 distinct class sets.
The answer is now recorded under the rendering the walk already compares by
(`str`), which turns 569160 walks into at most 2048.

On the 200-plane slice the record holds **527 class sets after each relation**,
which is the number of line cusps the relation indexes -- the two relations
together added no walk to those.  The rows' own relation times are the measure
of what the record is worth at length, and they are in the logs of section 5.

## 5. The rows at 189 720 planes

One process a row, the driver's own stages, off this worktree (`probe-row.py`),
with a counter on the split's `register_isotropic_lift`
(`orthogonal_quotients.py:2626`) and on the relation's record constructor, so the
resident set is recorded every 10 000 planes and every 10 000 records.

**`Otilde(T_Co)`, the split.** Standing row after the line row's 527 cusps:
**709.9 MiB** at 866 s.

| planes | wall | resident | KB a plane since the mark before |
| ---: | ---: | ---: | ---: |
| 10 000 | 2 212 s | 1 297.3 MiB | -- |
| 50 000 | 3 045 s | 1 644.7 MiB | 8.7 |
| 100 000 | 3 543 s | 2 536.7 MiB | 17.8 |
| 180 000 | 4 664 s | 3 973.5 MiB | 17.9 |

The split's own term is therefore **not flat**: it settles at about 18 KB a
plane, and 189 720 planes is ~3.3 GiB on the 0.71 GiB standing row.  What is
left in it is the lift registry -- the lift's word, its source parabolic family
and its discriminant image, keyed by the plane's span
(`register_isotropic_lift`, `orthogonal_quotients.py:2626-2662`) -- which is
#584's 63 KB a plane, not the relation this issue is about.

**`Otilde(T_Co)`, the relation.** The same row, its 569 160 records:

| records | wall | resident |
| ---: | ---: | ---: |
| 10 000 | 4 770 s | 4 379.0 MiB |
| 50 000 | 4 856 s | 4 491.3 MiB |
| 100 000 | 4 969 s | 4 448.1 MiB |
| 510 000 | 6 087 s | 4 948.4 MiB |

At the three counts the acceptance names the relation's resident set is **flat to
within 50 MiB** -- 4 379.0, 4 491.3, 4 448.1 MiB, and the third is *below* the
second -- and over all 510 000 records it rises 569 MiB, 1.15 KB a record
against the 394.5 B a record measured in section 2.  The rest is not the records:
the loop keeps one `endpoint_pairs` entry an edge (`predicate_subgroups.py:1305`)
and builds three GAP class sets a plane (`_carried_divided_classes`) whose
workspace is not returned to the host between marks.  Which of the two it is is
not separated here.

The relation's rate is what the record of walked class sets buys: 520 000
records in 1 480 s, **2.6 ms a record** and so ~7.8 ms a plane, where the same
relation measured 66-81 ms a plane before the record was added.

**The 4 GiB clause is answered, and the answer is no.**  The row's peak was
**4 982 MiB of tree RSS** and **4 990 MiB of single-process VmHWM** at 550 000 of
its 569 160 records, with 19 160 records and the whole contract step still to
come -- 1.2x the 4 GiB the acceptance names, and inside this project's 6 144 MiB
guard.  The terms are the two measured above: ~3.3 GiB of lift registry (the
split's 18 KB a plane, #584's) and 0.21 GiB of relation.

**Which term the 4 GiB clause fails on.**  Dropping the lift registry alone,
after 200 planes of `Otilde(T_Co)`'s split have been built the way the row builds
them, frees **1.8 MiB -- 9.2 KiB an entry**, so at 189720 planes at least
**1.67 GiB** is that one table (`attribution.log`).  The row's measured term is
~18 KB a plane, so at the row's length the registry is about half of it and the
rest is the cusp row's spans and the cusp ingress's two tables.  The 9.2 KiB is
what #584's repair left, not what it named: its acceptance was that
`register_isotropic_lift` retain nothing the caller does not read, and the
relation does read the lift, once a plane.  The 9.2 KiB is
a lower bound for the row's own figure: the entries are GAP-backed and the
allocator need not return their pages, and the per-entry word grows with the
double coset reached, which is why the row's last bands sit at 18 KB a plane
while the first 200 planes' registry is 9.2.

**A release inside the relation cannot lower the peak, and the 4 GiB clause
therefore needs the split fused into the walk.**  The row's peak is reached at the
*end of the split*, before the relation reads a single plane: every one of the
189 720 lifts has to exist at once for the walk to compose each plane's action
(`registered_isotropic_lift`, `predicate_subgroups.py:1295` and `:1342`), so
dropping a plane's lift after its edges are made reclaims memory that has already
been paid, not the peak.  Lowering the peak is the one-pass shape -- the walk
drawing the split as it goes, holding one lift at a time -- and that is a
redesign of `tits_building_incidence_by_divided_classes`
(`predicate_subgroups.py:1177-1420`), not a release at
`predicate_subgroups.py:1344`.  It is also why the certificate route and the
witness machinery make a *consumer-side* release unsound rather than merely slow:
they read the registry after the class route (`predicate_subgroups.py:1066`,
`orthogonal_quotients.py:4373-4374`), and
`tests/lattices/test_the_incidence_decided_by_divided_classes.sage:163` runs the
two routes on one quotient.

**The host's killer is not taking my rows for their size.**  The `Otilde+`
retry was killed at **1698 MiB** tree RSS after 40 000 planes, with low-water
MemAvail 1 076 MiB (`row-Otilde+-retry.log`, `# launcher exit: 0` at
2026-11-18T05:51:48Z), and `/proc/vmstat`'s `oom_kill` stands at **43**.  A row a
quarter the size of the one that died at 4 982 MiB died the same way, on a host
whose other tenants hold 13.6 GiB under `full avg10=23.50` memory-stall pressure,
so whatever is largest is killed and the row's own footprint is not what decides
it.  This also disposes of the one-pass redesign as a remedy for the *evidence*:
it would lower the peak from ~5 GiB to ~1.5 GiB and would still have been killed
here.

**The row ran to its counts.**  The gated retry started at 06:03:11 with
6 267 MiB of MemAvailable (`gated.log`, attempt 484) and printed, in
`row-Otilde-retry.log`:

```
[  1595.2 s rss  1853.5 MiB] the split: 10000 planes registered
[  1874.8 s rss  2001.4 MiB] the split: 50000 planes registered
[  2565.0 s rss  2837.8 MiB] the split: 100000 planes registered
[  3116.6 s rss  4320.1 MiB] the split: 180000 planes registered
[  3241.8 s rss  4637.6 MiB] the relation: 10000 records
[  3331.8 s rss  4710.8 MiB] the relation: 50000 records
[  3442.1 s rss  4846.8 MiB] the relation: 100000 records
[  4369.0 s rss  5406.7 MiB] the relation: 569160 edges in 3014.9 s
[  4369.0 s rss  5408.2 MiB] the plane row: 189720 plane cusps, 189721 planes registered
```

So `Otilde(T_Co)`'s relation is **569 160 edges over 189 720 plane cusps and a
527-cusp line row**: three edges a plane with no collision and no missed plane,
which is the count the acceptance asks for, and the class route's own.  At the
three record counts of clause 3 its resident set is 4 637.6, 4 710.8 and
4 846.8 MiB -- flat to within 210 MiB over 90 000 records, 2.3 KB a record
against the 394.5 B record measured statically.

The 4 GiB clause is therefore **answered no on a completed relation**: 5 408 MiB
at the relation's end, still rising, before the contract step.  The split's own
marks are those of the failed run (10 KB->50 KB->100 KB: 1 853.5, 2 001.4,
2 837.8 MiB, ~18 KB a plane at the end), so the row's resident set is neither
flat nor under 4 GiB, and the term is the one measured in section 5.

  The gated retry started at
06:03:11 with 6 267 MiB of MemAvailable (`gated.log`, attempt 484) and is in its
split at 130 000 of 189 720 planes, 3 335 MiB, 2 776 s, with the host at
7 170 MiB available and the line row done in 315.6 s (`row-Otilde-retry.log`).
Its peak, its two edge counts and the contract's witness verdict are the run's
own numbers, and they arrive when it returns.

**Why the counts have to be computed and cannot be extrapolated.**  The edge
count is not a fixed multiple of the plane count.  On `U + U(2) + <-2>` both
kernel rows decide **4 edges over 3 line cusps and 2 plane cusps** -- two edges a
plane, because the covering's three lines fall into two line cusps there -- while
the 200-plane slice of `Otilde(T_Co)` gives three a plane.  So nothing short of
the row's own relation answers the clause, and the record of the row is not a
count that a smaller row predicts.  That run, at the pushed head, is also the
witness clause decided for a pair of groups: a `DECIDED` outcome is the driver's
statement that every edge's divided-class witness is the orbit its line cusp is
indexed by, that every plane cusp carries an edge and that every line cusp does
(`divided_class_violation`, `coble_gamma_co_2_incidence_rows.py:279`, and the
coverage clauses at `:496` and `:502`).

**Neither row returned.  Both were killed by this host's OOM killer.**

`Otilde`, after 2 h 10 min and 550 000 of its 569 160 records: `row-Otilde.log`
ends `# launcher exit: 0  ended: 2026-11-18T04:36:46Z` with `peak tree RSS 4982
MiB`, `low-water MemAvail 1059 MiB`, no traceback and no
`STOPPED_AT_MEMORY_LIMIT`.  `/proc/vmstat`'s `oom_kill` went **37 -> 38** across
that minute (read at 04:09 and 04:37) and no process of mine left the host in
it except this one, so the reading is the kernel's killer taking the tracee and
proot reporting 0.

**`Otilde+` did not return either.**  Its process left the host at
`row-Otilde+.log`'s last line, `# launcher exit: 0  ended: 2026-11-18T03:36:26Z`,
after 130 000 planes at 3 299 MiB and a low-water MemAvail of 1 111 MiB, with no
traceback and no `STOPPED_AT_MEMORY_LIMIT`.  This host's kernel has killed 37
processes (`/proc/vmstat`, `oom_kill 37`) and its memory pressure stands at
`full avg10=41.37` (`/proc/pressure/memory`), so the reading is that the OOM
killer took the tracee and proot reported 0.  Both rows are queued to run again one at a
time and only on a host that can carry one: `chain-otildeplus.sh` (`chain.log`,
started 04:36:56) and `chain-otilde-gated.sh` (`gated.log`, gated on 6 GiB of
`MemAvailable` and no other row running).  One row on the host at a time is the
dispatch shape #599 itself asks for; two at once is what this host could not
carry, and neither could one, on a host whose other projects held 10-14 GiB.

## 6. What was run, and what was not

Run, off the worktree with only these two repairs:

* the four shapes' comparison above and the 200-plane slice (`slice-200b.log`);
* the driver on `U + U(2) + <-2>` on both trees (`smoke-new.log`,
  `smoke-parent-1.log`, `smoke-parent-2.log`);
* `test_a_dropped_plane_is_collected.sage` and
  `test_a_plane_transport_builds_one_span.sage`: **2 passed in 5.38 s**
  (`tests-plane.log`), and **2 passed in 9.13 s** after the rebase onto
  `e58cab8` (`tests-rebased.log`);
* `test_the_stable_plane_rows_equal_their_double_coset_counts.sage` together
  with the two incidence files: **9 passed in 298.83 s** at `f2c519c`
  (`tests-rows.log`); after the rebase the same three files gave **3 failed, 6
  passed in 986.82 s** (`tests-rebased-rows.log`), all three failures on
  `U + U(2) + <-2>` -- `0 of 2 coverings` on the two incidence tests and a
  radical-lift `ArithmeticError` in the independent double-coset count -- which
  is the flake that file documents ("`is_parabolic_complete` ... flips with the
  ambient row's per-process representative choice").  Re-run on the same tree:
  the plane-row file **3 passed in 46.65 s and 38.77 s**, the incidence file
  **3 passed in 171.10 s**.  The flake is not this change's and it is not
  fixed here.

Not run, and not reported: the two kernel rows at 189720 planes, which are the
acceptance of #599.  They are launched off the same worktree
(`row-Otilde`, `row-Otilde+`, one process a row, the split streamed and the
orbit recorded); this machine ran at load 10-24 from other projects' work while
these were taken, so their wall times are not the row's.  Their counts, their
resident-set curve at 10000, 50000 and 100000 planes, and the peak are appended
when they return, and `#599` is not closed by this note.
