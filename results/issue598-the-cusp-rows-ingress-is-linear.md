# The cusp rows are admitted as their orbits: the ingress is linear

`cusps(rank)` hands its row to the literal ingress, which identifies repeated
points through a table of them, and a cusp's hash is constant over its universe
-- two cusps of one orbit need not share a span, so a cusp has no cheap
canonical key -- so every cusp of the row was compared with every other and each
comparison was a transporter question.  The row's construction yields one
representative per orbit and therefore cannot contain a repetition, so the
repair is to stop re-deciding it: the points are admitted as they are produced
and their own identity is the enumeration's inverse.  Measured on `Otilde(T_Co)`,
the row of #381: **100 plane cusps cost 249.986 s of ingress before and under a
millisecond after, and 1 000 / 10 000 / 100 000 planes cost 1.77 / 2.11 / 2.11
microseconds a plane at admission**, flat, on a row whose per-plane build is
6.86 / 6.47 / 6.79 ms.

All measurements are on the adopted runtime (Sage 11.0.beta5), port
`991b88b0`, `61b3fa1` (the parent) against the tree of this note; probes and
logs are under `.tmp/issue598-ingress/`.  `T_Co = <2> + U(2) + E8(-2)` is
constructed as in #381's note (`NamedLattices.Tco`, Dolgachev--Kondo, Izv. Math.
77:3 (2013), section 3, equation (3.6), printed p. 513).

## 1. What was quadratic, and where

The row ended in `finite_ordered_set(tuple(...))`.  That is two passes over all
pairs:

* `FiniteOrderedSets._on_points` (`finite_ordered_sets.py:544`) is literally
  `tuple(dict.fromkeys(points))`: insertion *i* calls `__eq__` against every
  point already in the bucket;
* `from_indexed`'s default inverse (`finite_ordered_sets.py:596`) builds
  `lookup = dict(zip(points, indices, strict=True))`, a second table of the same
  points, and pays the same questions again.

A cusp's hash is constant on purpose: `_ArithmeticCuspEngine.__hash__`
(`isotropic_orbits.py:899-903`) is `hash((class, id(subgroup), rank))`, and the
docstring says why -- representatives are not canonical.  So every point lands
in one bucket.  The comparison is `_ArithmeticCuspEngine.__eq__`
(`isotropic_orbits.py:882-894`): equal spans answer cheaply, otherwise
`transporter_witness`, i.e. `predicate_subgroups.py:741` into
`_subgroup_isotropic_equivalence_witness` (`orthogonal_quotients.py:4244`),
which asks `invariant_separates_isotropic_orbits`
(`orthogonal_quotients.py:2411`) and that computes `_divided_discriminant_classes`
(`isotropic_orbits.py:2021`) of both planes -- three
`divided_discriminant_class` calls a plane.

Measured on 100 plane cusps of `Otilde(T_Co)`, drawn from the route's own walk:
**249.986 s**, which at 4 950 pairs a pass and 9 900 questions is **25.3 ms a
question**.

The full orthogonal group's row has the same defect at its own site:
`lattice_morphisms.py:5427` (at the parent) admits `tuple(_cusp(...))` the same
way, and `_CuspEngine.__hash__` (`isotropic_orbits.py:774-778`) is constant for
the same reason.

## 2. The linear form, and whether the relation's applies

`tits_building_incidence` already does the linear thing
(`predicate_subgroups.py:1375-1380` at the parent):

```python
points = tuple(incidences)
positions = {id(point): position for position, point in enumerate(points)}
return FiniteOrderedSets().from_indexed(
    finite_ordinal_set(len(points)),
    lambda position: points[int(position)],
    index_of=lambda point: positions.get(id(point)),
)
```

with the mechanism in its comment just above (`:1363-1372`).  That form applies
here, for the reason it applies there: the points are distinct by construction.
The walk `_yield_subgroup_isotropic_orbit_representatives` yields one
representative per double coset, so the cusps it names are pairwise distinct
orbits, and a table of them can only ever answer "not equal".  Supplying the
inverse also skips both passes at once -- `_on_points` is not called, and
`from_indexed`'s `lookup` is inside `if index_of is None:`.

It does not apply unchanged, and the difference is what a cusp *is*.  The
relation's points are `DividedClassCuspIncidence` certificates the walk itself
built and nobody else can construct, so identity names them completely.  A cusp
is an orbit, so a cusp rebuilt from a span is equal to a point of the row
without being it, and membership must still answer for it.  The repair therefore
supplies identity first and the cusps' own equality for a candidate that is not
one of the retained objects, asked when the candidate is put rather than once
per pair while the row is built.

So the operation is named once, at the owner of the ingress, and both rows call
it: `_distinct_finite_ordered_set` (`finite_ordered_sets.py:1095-1134`), next to
`finite_ordered_set`, whose docstring states the caller's obligation -- two equal
points leave the enumeration non-injective.

What is deliberately unchanged: `finite_ordered_set`'s literal ingress still
identifies repeated points (a caller that states nothing still gets the table),
and `from_indexed`'s default inverse still builds its table and still raises when
the enumeration selects a repeated point.

## 3. The row is unchanged, element by element

One list of 100 plane cusps of `Otilde(T_Co)`, both admissions applied to it in
one process (`probe-slice.py`), so the comparison is of the change and not of two
runs:

| question | old ingress | repaired admission |
| --- | --- | --- |
| cardinality | 100 | 100 |
| retained points | the 100 drawn, in their own positions | the 100 drawn, in their own positions |
| the plane each position names (span), position by position | 0 positions differ | 0 positions differ |
| `enumeration_inverse()` at every position | `0, 1, …, 99` | `0, 1, …, 99` |
| every drawn cusp admitted by the row | yes | yes |
| a cusp rebuilt from a member's span | placed at 0, admitted | placed at 0, admitted |
| the subgroup's rank-1 cusp (no member of a plane row) | placed nowhere | placed nowhere |

That the dedup never dropped anything is the same measurement from the other
side: the 100 cusps have **100 distinct span keys** (`_span_key` of each
representative), and `_span_key` names the sublattice exactly, so 100 distinct
spans are 100 distinct sublattices and therefore 100 distinct orbits.

Across trees the rows cannot be compared as sequences, and this is a fact about
the walk rather than about this repair: two runs of the *same* tree
(`rows-base.log`, `rows-base2.log`) differ in the order of the orbits and in
which representative each orbit retains.  What is compared across trees is the
cardinality of every row the leakage could change: four lattices
(`6JRS = U+U+<-2>`, `U+U(2)+<-2>`, `U+U(2)+<-4>`, `E10 = U+E8`) × {`O(L)`,
`Otilde(L)`} × {rank 1, rank 2} = 16 rows, **identical counts on the two trees**
(`rows-base.log` against `rows-fixed.log`): 1, 1, 1, 1, 2, 1, 3, 2, 2, 1, 4, 3,
1, 0, 1, 0 in the order the probe reads them.

## 4. The curve

`Otilde(T_Co)`'s rank-2 row, one process a row length, the statements the row
makes measured per plane and the admission measured whole
(`probe-ingress-growth.py`).  "The plane, all stages" is the split's walk draw,
one transport and lift registration, one span key and cusp, and the route's own
finite action; its first and last band are equal windows at the two ends of each
run.

| planes | the row's transversal | plane, all stages, first -> last | plane, all stages | the row built | admission | admission a plane |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 000 | 198.7 s | 7.71 -> 6.25 ms | 6.86 ms | 206.3 s | 0.002 s | 1.77 us |
| 10 000 | 212.8 s | 6.78 -> 6.28 ms | 6.47 ms | 277.5 s | 0.021 s | 2.11 us |
| 100 000 | 207.4 s | 6.37 -> 6.25 ms | 6.79 ms | 886.2 s | 0.211 s | 2.11 us |

**The per-plane cost is flat** over a factor of 100 in the row's length: 6.86,
6.47, 6.79 ms a plane, first band against last band 7.71 -> 6.25, 6.78 -> 6.28,
6.37 -> 6.25.  The admission is linear with a constant of order a microsecond:
1.77, 2.11, 2.11 us a plane, i.e. 0.002, 0.021, 0.211 s.  The transversal is one
fixed cost of 198.7--212.8 s, paid before the first plane.

At the row's own length (189 720): `189720 * 6.79 ms = 1288 s` of planes plus a
207 s transversal plus 0.40 s of admission -- **25 minutes**, where the ingress
alone was `189720 * 189719 / 2 = 1.80e10` pairs at 25.3 ms, **14.4 years a
pass**: 27 years through the call the route makes.

The same repair on the other row it touches: `Otilde(T_Co)`'s line row of 527
cusps builds in **245.2 s** in its walk, and its literal ingress costs 11.1--12.0
ms a pair (measured on prefixes of 20, 40 and 80: 2.282, 8.946, 35.177 s), so
139 351 pairs were ~1 600 s of that row's old admission on top of its walk.

## 5. The test, and what it cannot see

`tests/lattices/test_a_cusp_row_admits_its_orbits.sage` (new) asserts the two
statements the admission rests on, on four specimens -- the kernel plane and line
rows of `U+U(2)+<-2>` (two and three cusps), those of `U+U(2)+<-4>` (three and
four), the full group's line row of the same lattice (two), and `E10`'s empty
kernel plane row:

* the row's cusps are **pairwise distinct orbits**, read off the cusps' own
  equality, one question a pair -- this is the obligation the repair takes on,
  because the admission no longer identifies a repetition, so a walk that
  yielded one orbit twice would leave it standing in the row twice;
* each cusp answers its **own position** under `enumeration_inverse()`, is
  admitted by the row, and names a primitive totally isotropic rank-`rank`
  subobject whose own membership in the cusp holds.

**It is not a red for this defect, and no gate test can be.**  The numbers say
why, and they are the reason the second branch of the issue's acceptance cannot
be met inside the harness's 20 s call ceiling:

* a red by time needs a row where the ingress dominates the build.  At the
  measured 50.6 ms a pair (two questions of 25.3 ms), the ingress alone passes
  the 20 s ceiling at 29 cusps and the 60 s hang bound at 49; and at that size
  the build is minutes, not seconds: `Otilde(T_Co)`'s plane row pays 199--213 s
  of transversal before its first plane and 6.8 ms a plane after that, and its
  line row, whose question is cheaper (11.1--12.0 ms a pair), needs 103 cusps to
  pass the 60 s bound and costs 0.47 s a cusp to walk, 245 s for its 527;
* every cusp row this host can build inside a test call is 1--9 cusps, where the
  ingress is 6 questions (6JRX, `O(L)` plane) to 36 (6JRY, 9 cusps) at 14 ms
  each: 0.1--0.5 s, a fraction of the build (33--88 s on those two lattices), so
  reverting the repair would not fail anything in the gate;
* the largest such rows do not even fit the ceiling today, independently of this
  repair: `tests/lattices/test_scattone_plane_orbits.sage` on `61b3fa1` with this
  change measures 85.37, 32.22 and 26.72 s for three of its five tests against
  the 20 s ceiling;
* and a red by *counting* is not available either: this project's test lint bans
  mocks and patches (`TL05`), `id` (`TL03`) and the bypass constructors
  (`TL08`, which is where `finite_ordered_set` is), so a test can neither count
  the equality questions nor name the ingress.

The new test therefore gates the mathematics and passes on both trees -- it was
run on the parent `61b3fa1` too (5 passed, 20.49 s) -- and the regression this
defect would need a *dispatched* row to catch: `Otilde(T_Co)`'s plane row, 25
minutes with this change against 27 years without it, is the CI job
`tests/coble_gamma_co_2_incidence_rows.py --rows Otilde,Otilde+ --lattice Tco`.

## 6. What was run, and what was not

Run: the probes above (`.tmp/issue598-ingress/`, one process a run, adopted
runtime, port `991b88b0`); the new test file on this tree (5 passed in 21.32 s,
slowest call 10.64 s) and on the parent tree (5 passed in 20.49 s); the cusp
consumers `test_a_cusp_names_its_plane_by_span.sage`,
`test_the_coble_incidence_vertices_are_its_cusp_representatives.sage`,
`test_the_incidence_line_vertex_is_the_cusp_of_its_line.sage`,
`test_the_lift_registry_carries_the_finite_element.sage` and
`tests/groups/test_a_subgroup_built_from_a_subgroup_states_its_description.sage`
(29 passed in 46.68 s, slowest call 11.90 s); and
`test_scattone_plane_orbits.sage` (5 passed in 156.61 s, three calls over the
ceiling as recorded above).

Not run to completion: the heavy consumers.  They were attempted twice -- once as
one six-file `pytest` call, killed at the command's 900 s bound with no report,
and once one file a process (`.tmp/issue598-ingress/run-consumers.sh`, 1500 s a
file), whose first file
`tests/lattices/test_the_coble_incidence_of_line_and_plane_orbits.sage` was still
running after twelve minutes when this note was written; its log is
`.tmp/issue598-ingress/consumer-test_the_coble_incidence_of_line_and_plane_orbits.log`.
That file builds `Otilde(T_Co)`'s cusp rows and their incidence -- the line row
this note measures at 245 s of walk, and a `Gamma_{Co,2}` plane row that #381's
note priced at 245.9--351.3 s -- so it does not fit a ten-minute command and its
outcome is not known here.  The same holds for
`test_the_incidence_decided_by_divided_classes.sage`,
`test_a_row_computes_one_plane_covering.sage`,
`test_the_row_retains_no_transport_for_a_carried_line.sage`,
`test_the_incidence_line_vertex_is_named_by_the_finite_image.sage`,
`test_special_orthogonal_split_building.sage`, `test_orbit_milestones.sage`,
`test_the_kernel_incidence_rows.sage` and
`tests/engineering/test_the_incidence_row_reports_a_broken_contract_apart_from_an_undecided_row.py`,
which the same driver dispatches after it.  Also not run: the whole suite; and the
ast-grep gates, which are not installed on this host.

The Scattone measurement above was taken on the repaired tree (base `61b3fa1`),
not on the parent; that file reads `isotropic_orbit_representatives`, which this
change does not touch, so the numbers are the parent's own, but the run was not
made there.
