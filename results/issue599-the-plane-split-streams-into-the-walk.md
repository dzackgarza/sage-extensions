# The plane split streams into the walk

`Otilde(T_Co)`'s plane row -- 189720 primitive isotropic planes under
`ker rho` -- is the row of #381, and its resident set was never the relation's
or the cusp row's: the split built every plane of the row and returned them as a
tuple before the first cusp existed.  The split now yields.

All measurements are on the adopted runtime (Sage 11.0.beta5), the port
`991b88b0`, from a worktree of `f2c519c` carrying only the two repairs of this
issue; probes, launchers and logs under `.tmp/issue599/` of that worktree.

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

## 5. What was run, and what was not

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
