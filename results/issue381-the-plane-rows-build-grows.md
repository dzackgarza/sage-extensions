# The plane row's build is flat and its set ingress is quadratic: which the cap caught

`Otilde(T_Co)`'s row did not return inside its 10800 s cap (#381, run
44135163725, head `34c9be89`, route `divided-class`).  The 199-plane slice that
priced it at 1.65 ms a plane is a *different* statement -- it measured the
route's per-plane arithmetic at planes that already existed -- so two
extrapolations were left open: the per-plane cost rises with the planes already
processed, or the row's own build (`cusps(2)`, 189720 planes at 5.98 ms a
plane, 1179 s) rises with them.

**Neither.  The per-plane cost is flat to within 5% from 120 to 50000 planes,
and the row's build is flat with it -- 1205 s at 189720 planes, 20 minutes.
What grows is the row's set ingress: `cusps(2)` ends in
`finite_ordered_set` over a row of cusps that share one hash, so every cusp
compares with every cusp already inserted, and each comparison asks an
invariant question that costs 24.7 ms.  That is quadratic in the row's length
and it is 14 years at 189720, not a slow row.**

The cap therefore caught a defect that no cap can cover: the row would not
return in 10800 s *or* in 10^8 s, and the two parts of its build have different
owners.  Measurements below are on the adopted runtime (Sage 11.0.beta5), port
`991b88b0`, on `T_Co = <2> + U(2) + E8(-2)` (Dolgachev--Kondo, Izv. Math. 77:3
(2013), section 3, equation (3.6), printed p. 513), probe
`.tmp/issue381-growth/probe-row-growth.py`, one process a run.  The first two
runs are on `ba51bdf`, the rest on `0516a0f7`; the `#596` changes between them
touch neither the ingress path nor the equality below.

## 1. What one plane costs, at five row lengths

The row is built from the statements the library makes for it, because no slice
of it exists: the route's iterator materializes the whole row before it yields
(`_plane_orbit_from_parabolic_stabilizer` collects its `representatives`,
`orthogonal_quotients.py:3867-3874`), so its first `next` is the whole walk.
Per plane, therefore, the probe times exactly what that walk does:

* `next(splittings)` -- `_iter_splitting_isometries_in_im_rho`, which
  materializes its transversal of the finite coset action on the first draw;
* `lift.transport_isotropic_object(source)` and `register_isotropic_lift`;
* `_arithmetic_cusp(subgroup, plane)`: the span key (a row Hermite form) and the
  cusp object, which is what `cusps` keeps a plane as;
* `_composite_divided_class_action`: the route's own per-plane finite action.

First and last band are equal-sized windows at the two ends of the run; "plane,
all stages" is their sum.

| planes | the split's walk, first -> last | transport and lift | the cusp (span key) | the finite action | plane, all stages, first -> last | all | end RSS |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1.72 -> 0.82 ms | 4.52 -> 4.35 ms | 0.77 -> 0.74 ms | 0.84 -> 0.28 ms | 7.85 -> 6.19 ms | 7.01 ms | 1243 MiB |
| 800 | 1.22 -> 0.85 | 4.56 -> 4.42 | 0.77 -> 0.72 | 0.56 -> 0.31 | 7.11 -> 6.31 | 7.00 | 1308 |
| 1000 | 1.37 -> 0.98 | 5.03 -> 4.76 | 0.82 -> 0.78 | 0.67 -> 0.32 | 7.89 -> 6.85 | 6.97 | 1338 |
| 10000 | 0.95 -> 0.87 | 5.16 -> 4.25 | 0.73 -> 0.70 | 0.33 -> 0.27 | 7.18 -> 6.10 | 6.27 | 1481 |
| 50000 | 0.87 -> 0.97 | 4.53 -> 4.30 | 0.73 -> 0.70 | 0.30 -> 0.33 | 6.43 -> 6.29 | 6.35 | 2025 |

Every stage is flat, and the sum is flat: 7.01, 7.00, 6.97, 6.27, 6.35 ms a
plane over a factor of 417 in the row's length.  The walk's own per-plane cost
is also flat (0.87--1.37 ms), and its materialization -- the whole transversal
of the finite coset space, 189720 double cosets -- is one fixed cost of
174.4--219.5 s, paid before the first plane exists and independent of how many
planes are then drawn.

At 189720 planes the build is `189720 * 6.35 ms = 1205 s` plus the walk's
174 s: **23 minutes**.  With the line row (308 s, measured earlier) and the
route's own per-plane arithmetic (313 s at 1.65 ms) the row is 33 minutes.  The
build does not exceed the cap, and the per-plane cost does not grow.

## 2. What the ingress costs, at five row lengths

`cusps(2)` is not only the planes: it ends in
`finite_ordered_set(tuple(...))` (`predicate_subgroups.py:768-775`), whose
literal ingress is `tuple(dict.fromkeys(points))`
(`finite_ordered_sets.py:544`), and then `from_indexed`'s
`lookup = dict(zip(points, indices, strict=True))`
(`finite_ordered_sets.py:596`).  A cusp's hash is constant over its universe on
purpose -- `_ArithmeticCuspEngine.__hash__` (`isotropic_orbits.py:899-903`) is
`hash((class, id(subgroup), rank))`, because representatives are not canonical
-- so every point lands in one bucket, insertion *i* compares against all
*i - 1* points already there, and `dict` calls `__eq__` on each.

| cusps | `tuple(dict.fromkeys(...))` | per comparison | distinct |
| ---: | ---: | ---: | ---: |
| 20 | 4.748 s / 6.052 s | 25.0 / 31.9 us | 20 |
| 40 | 19.232 s / 20.552 s | 24.7 / 26.3 us | 40 |
| 80 | 81.276 s | 25.7 us | 80 |
| 120 | 175.996 s | 24.6 us | 120 |
| 40, through `finite_ordered_set` | 35.976 s | 1.87 passes | 40 |

Doubling the row multiplies the ingress by 4.05 and by 3.96: quadratic, with a
per-comparison cost that is constant at 24.6--25.7 us and two passes through
the row because `from_indexed` builds its own table as well.

Extrapolated to the row: `189720 * 189719 / 2 = 1.7997e10` comparisons at
24.66 ms is **4.44e8 s, 14.1 years**, and 8.3e8 s through the library call the
route actually makes.

## 3. The mechanism, with its function and line

Each of those comparisons is one cusp asking another whether it is the same
orbit, and the answer is a mathematical question, not a span comparison:

* `_ArithmeticCuspEngine.__eq__` (`isotropic_orbits.py:882-894`) compares the
  spans, and where they differ returns
  `self.transporter_witness(other.representative()) is not None` (line 894) --
  which also builds the other cusp's subobject from its span
  (`representative()`, line 873);
* `transporter_witness` (line 935) is
  `subgroup().isotropic_equivalence_witness`, which is
  `predicate_subgroups.py:741` into `_subgroup_isotropic_equivalence_witness`
  (`orthogonal_quotients.py:4244`);
* that asks `invariant_separates_isotropic_orbits`
  (`orthogonal_quotients.py:2411`) first, and for rank two that computes
  `_divided_discriminant_classes` (`isotropic_orbits.py:2021`) of *both* planes
  -- three `divided_discriminant_class` calls a plane
  (`lattices.py:7212`), each a `div` (`lattices.py:6969`) on the lattice -- and
  builds a GAP set of the classes before deciding.

The profile of eight cusps' insertion (3.072 s under the profiler) attributes
it: 46 `__eq__` calls cost 3.072 s, of which
`_subgroup_isotropic_equivalence_witness` 3.001 s,
`invariant_separates_isotropic_orbits` 2.100 s,
`_divided_discriminant_classes` 1.584 s, `divided_discriminant_class` 1.563 s,
`div` 0.867 s, on 67215 `set_categories.__call__` calls for the class sets.

So the growing structure is not a per-plane registry that grows: it is the
row's length, squared, in the ingress that `cusps` ends with -- one interval of
the row's build that no `stage()` wraps.

## 4. Where the cap landed

`10800 - 308` (the line row) `- 1379` (the plane row: 174 s of walk and 1205 s
of planes) leaves 9113 s of ingress, and `sqrt(2 * 9113 / 0.02466) = 860`.  The
run was killed at about **860 of 189720 plane cusps, 0.45% of the row**, with
the whole row already built in memory and nothing after it started.  A cap of
any size buys `sqrt`: 10^6 s reaches 9000 cusps, and the row needs 4.4e8.

What the artifact `timings-kernel-incidence-rows-34c9be89...` (986 bytes)
holds: it is the workflow's upload of `.timings/` (the stage record
`stages-<sha>-<stamp>.jsonl`, one JSON line per closed `stage()`/`timed_stage()`,
with the report log and JUnit file, CONTRIBUTING ENV-03), and 986 bytes zipped
is one or two records.  It cannot hold per-plane bands: the recorder writes one
interval per stage and the bands are not stages.  And by construction it holds
no record of the ingress -- `tuple(...)` exhausts the generator, which closes
"coset splitting and transport" when the last plane is drawn, and the ingress
then runs with no interval open -- so the last record a run killed there writes
is the plane row's walk closing.  **The artifact was not read**: the archive
download answers `401 Requires authentication`, and this project's GitHub
connection reads issues and pull requests and pushes branches; it has no
artifact download and no token for one.  What it holds above is read from the
workflow file that uploads it and from the recorder that writes it.

## 5. What is filed, and where

The defect is filed at the owner of the operation, not at the walk and not at
the retention:

* **`cusps`** (`predicate_subgroups.py:751`, its ingress at 768-775) hands
  `finite_ordered_set` a row whose points it knows are distinct -- the parabolic
  split yields one representative per double coset -- and pays the set's
  equality for each pair anyway.  The route's own relation does the opposite
  six hundred lines below (`predicate_subgroups.py:1375-1380`): it supplies
  `from_indexed`'s inverse by `id`, "which keeps the ingress linear".  Same
  repair here: name the row's positions by identity and skip the dedup.  The
  route's comment at `predicate_subgroups.py:1363-1372` states this mechanism in
  full -- "for constant hashes compares every point with every other ... supplying
  the inverse the walk already used keeps the ingress linear" -- so the same
  reasoning was applied at the relation and not at the row the relation is read
  from.
* **`FiniteOrderedSets._on_points`** (`finite_ordered_sets.py:544`) and
  `from_indexed`'s own table (`:596`, built under `if index_of is None:` at
  `:583`) are the general form: with a constant-hash point, both are
  `n(n-1)/2` equality questions, and a caller that knows its points are
  distinct has no way to say so.
* **`_ArithmeticCuspEngine.__eq__`** (`isotropic_orbits.py:894`) is where the
  24.7 ms is spent, and it is exact: it answers inequality by asking for a
  transporter, which is what a cusp's equality means.  It is not the owner of
  the quadratic; it is the price of asking it n^2 times.

`#588` is the row's retention (one constructed representative a plane, 12.29
GiB) and `#390`/`#391` are the cost of the walk; this is neither.  The two
owners above are `cusps`'s ingress and the set ingress it calls.

No red test is possible for the repair this note names: the row's answer is
unchanged (its cusps are distinct, so the dedup only ever compares distinct
cusps and never drops one), and a test that showed the defect would have to
assert how many equality questions the ingress asks -- a call count, which this
project's tests do not assert.  That is stated here rather than repaired
silently, and it is the same position `#553` recorded.

## What is not done here

* No row was dispatched and no cap was raised; no workflow file was edited.
* The divided-class route's own per-plane arithmetic (1.65 ms a plane) was not
  re-measured this turn; its 313 s is the earlier slice's number, and the
  `_composite_divided_class_action` band above (0.27--0.84 ms) is the part of
  it this probe can price without the line row.
* The line row's 308 s was not re-measured.  It is probable that most of it is
  the *same* ingress with a cheaper question -- 527 cusps are 139 thousand
  comparisons, and a line's invariant is one
  `divided_discriminant_class` a side rather than three -- but that is an
  inference from the recorded 308 s here, not a measurement.
* 100000 planes does not fit in a command of ten minutes: 100000 * 6.35 ms is
  635 s of planes and 174 s of walk, 809 s, before any ingress.  50000 (503.9 s
  measured) is the largest row this turn built.
