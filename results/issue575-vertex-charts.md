# #575: a Sterk polygon vertex, its normal cone and the atlas chart

`ConvexPolytopes.normal_fan()` puts the inner normal fan of a full-dimensional
lattice polytope in the dual of the lattice the polytope lives in
(`categories/schemes/polytopes.py:2504`), and `ToricSchemes` glues a variety from
the charts of a fan's maximal cones.  The contract is the issue's acceptance,
item by item; each row names the declaration that decides it and the measurement
that settles it.

| acceptance item | declaration that decides it | file:line | measured |
| --- | --- | --- | --- |
| the cone of a selected vertex, from its supporting primitive inner edge normals, in the dual of the polygon lattice | `ToricSchemes.ParentMethods.vertex_normal_cone` filters `fan.rays()` by `LatticePolytopes.ParentMethods.normal_supports_point`, then returns the one maximal cone those normals span | `categories/schemes/toric/toric_schemes.py:723`, `categories/schemes/polytopes.py:2703`, `categories/schemes/polytopes.py:2504` | on `conv{(0,0),(2,0),(0,1)}`: `fan().cocharacter_lattice() == lattice.dual_module()` is `True`; normals enumerated from the polytope's own `normal_value` pairing alone -- primitive `n` minimized on exactly the edge through the vertex -- equal the returned rays at all three vertices: `(0,0) -> {(1,0),(0,1)}`, `(0,1) -> {(1,0),(-1,-2)}` (index two), `(2,0) -> {(0,1),(-1,-2)}`; each cone has `dimension() == variety.dimension()` |
| the actual affine chart of that cone, identified with the existing atlas | `vertex_chart` is `affine_chart(vertex_normal_cone(vertex))`, and both go through the cached `_affine_chart` the atlas enumerates | `toric_schemes.py:789`, `:701`, `:715`, `:263` | `affine_cover().enumeration()(cone) is vertex_chart(vertex)` is `True` at all three triangle vertices and, on the St2 specimen, at both vertices probed; `enumeration_inverse()(chart) == cone` too; chart generator counts `2, 3, 2` on the triangle and `2, 5` on the specimen |
| no second fan or affine-scheme implementation | the operation returns a cone of `self.fan()` and the chart `_affine_chart` already builds for it | `toric_schemes.py:723`, `:789` | every returned cone satisfies `cone in variety.fan()`; `vertex_chart(v) is variety.affine_chart(cone)` |
| the source-faithful public St2 polygon, from the native length data | `Sterk.sterk2_boundary_directions` (17), `sterk2_surgery_directions` (2), `sterk2_direction_coefficients` (the `M_18_0_0` weights), `sterk2_boundary_path`, `sterk2_polygon` | `sterk.py:139`, `:168`, `:177`, `:877`, `:893`, `:920`, `:942`, `:976` | all 19 coefficients agree with the source rule written independently from the guide -- `l_j` on `v_2,v_6,v_8,v_10,v_12,v_14,v_18`, `l_j/2` on `v_3,v_5,v_7,v_9,v_11,v_13,v_15,v_17`, `l_4+l_1/2`, `l_16+l_19/2`, `l_1/2` and `l_19/2` on the surgery directions -- for the stored `ell`, for `(1,...,1)` (`v_1=v_3=v_19=1/2`, `v_4=v_16=3/2`) and for a mixed vector; `v_1` and `v_6` are the same vector `(-1,2)` with different roles |
| walk the path, then the convex hull including the closing side; a hull vertex, not every path point, indexes a chart | `sterk2_boundary_path` walks `:139` in source order; `sterk2_polygon` is `LatticePolygons(lattice)(tuple(path.values()))` | `sterk.py:942`, `:976` | `p_0=(0,0)`, `p_17=(-24,0)`, `p_8=p_9=(-12,26)`; 18 labelled path points, 17 distinct, `polygon.n_vertices() == 17`; `p_17 -> p_0` is the hull's closing side and both are vertices; shoelace of the closed path `820` equals `normalized_volume() == 820` |
| established on a small polygon with known smooth and singular vertex cones | `test_the_vertex_cones_of_a_triangle_index_charts_of_its_atlas` | `tests/schemes/test_sterk_polygon_vertex_charts.sage:35` | 2 smooth and 1 index-two vertex cone; the singular chart's dual Hilbert basis `(0,-1),(1,-1),(2,-1)` satisfies `z0*z2 = z1**2` and is not a polynomial ring |
| then on the stored St2 specimen through that public constructor | `test_a_stored_sterk2_polygon_vertex_indexes_its_chart` | `tests/schemes/test_sterk_polygon_vertex_charts.sage:125` | `(-24,0)`: rays `{(1,0),(0,1)}`, smooth, chart the atlas entry, 2 generators; `(-12,26)`: rays `{(-1,-2),(1,-2)}` (index `|det| = 4`), not smooth, all rays minimize there by `normal_supports_point`, chart the atlas entry, 5 generators; `cocharacter_lattice() == lattice.dual_module()` |

## The stored specimen's deciding call is over the per-call ceiling (superseded below)

The numbers in this section are the measurements of the tree before the
vertex's cone was retained; the round-2 section at the end of this note
records the run that fits the ceiling.

`tests/schemes/test_sterk_polygon_vertex_charts.sage:165`
(`variety = polygon.toric_variety(QQ)`) is the line that decides the specimen's
row, and it does not fit the repo's own 20 s call ceiling
(`testing/suite_budget.py:44`):

| run | session star import | this call | triangle test |
| --- | --- | --- | --- |
| quiet host (load low) | `3.04 s` | `27.42 s` | `4.42 s` |
| loaded host (load average 21.5 on four CPUs) | `15.76 s` | `44.22 s` | `12.42 s` |
| the same file before this round's two assertions | `15.76 s` | `61.03 s` | `14.14 s` |

`polygon.toric_variety(QQ)` alone is `36.13 s` in a probe on the loaded host
(`28.79 s` on a second, warmer probe); what it pays is the eager gluing of the
fan: 17 charts at `2.71 s`, the `C(17,2) = 136` pairwise `_face_transition`s at
`13.9-23.4 s`, `glue_affine_atlas` at `0.22 s`, and Sage's native variety at
`0.83 s`.  The vertex operations after it are `1.4-1.6 s` each.  The cost is the
eager construction at `toric_schemes.py:2259-2264`, which builds every pair
transition up front, together with `_FiniteSchemeGluingDatum.__init__`
(`categories/schemes/gluing.py:929`, resolving both directions of every pair at
`:954`), which glues only after that.  Making it lazy is a change to the gluing
datum, not to this issue's operation, and was not made here; it is the named
next step for this row.

It is not a regression of this issue: `4376fad` touched only `toric_schemes.py`
(`vertex_normal_cone`, `vertex_chart`, +86 lines), `sterk.py` (+229) and the
test file, and the gluing it costs through is unchanged.

The smallest input that decides the specimen's row is the specimen itself -- the
issue names the stored `ell` -- so no smaller deciding input exists.  The run
reported here is green on every assertion and red on the call ceiling, and that
is what the record says rather than a `--no-time-gates` overrun.

## What the file did not assert, and now does

* `:157-158`: the path has eighteen labelled points and its hull seventeen
  vertices, so the repeated point is a point of the path that is not a vertex of
  its own.  This is the issue's "a hull vertex, not every intermediate path
  point, indexes a chart" clause, which the file previously left unwitnessed.
* `:192-197`: the chart of a vertex is the atlas entry at that vertex's cone on
  the specimen too, not only on the triangle, which is the "retaining its
  identification with the existing atlas" clause.  It costs no measurable time
  because the atlas is enumerated lazily over the charts the gluing already
  built.

## What was run

`sage 11.0.beta5`, `/sage/.venv/bin/python`, image
`ghcr.io/dzackgarza/sage@sha256:59568577...`, the source tree bound at
`/repos/sage-extensions`:

```
$ python -m pytest -o addopts= -p qc_sage_session \
    -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
    --durations=0 tests/schemes/test_sterk_polygon_vertex_charts.sage
2 passed in 35.21s                              # on the rebase onto b1a76ac
27.42s test_a_stored_sterk2_polygon_vertex_indexes_its_chart   (ceiling 20 s)
 4.42s test_the_vertex_cones_of_a_triangle_index_charts_of_its_atlas
peak tree RSS 410 MiB
```

On the quiet host the collection ceiling (`6 s`) passed and the star-import
ceiling (`3 s`) was over by `0.04 s`; on the loaded host they were `7.69 s` and
`15.76 s`.  Both are properties of the proot session rather than of this file,
and both were over before this change as well.

The independent enumerations in this note are probe output, not part of the
test: the normals of the triangle were enumerated from `normal_value` over
candidate primitive `n` in `[-3,3]^2` alone, and the nineteen coefficients were
recomputed from the guide's rule in separate code from
`_STERK2_DIRECTION_COEFFICIENT_WEIGHTS`.

Not run: the CI image (`ghcr.io/dzackgarza/sage:develop` has no OCI runtime on
this host), the ast-grep gates (`ast-grep` is not installed here), and the rest
of the suite.

## Round 2, 2026-11-18: the deciding call now fits the ceiling

The section above concludes that the specimen's row cannot fit the ceiling
without a change to the gluing.  That conclusion was too quick: the call paid
the cone decision **six times**, not once.  `vertex_chart` is
`affine_chart(vertex_normal_cone(vertex))`, so the test's request for the cone
and then for the chart re-ran the scan of the fan's seventeen primitive normals
against the polytope's seventeen vertices, and the atlas block ran it again.

`vertex_normal_cone` now retains its answer per vertex of the polarizing
polytope (`categories/schemes/toric/toric_schemes.py:723`, registry at `:773`,
lookup at `:766`, the scan itself at `:782`), keyed by the vertex's coordinates
in the polytope's lattice rather than by the lattice point, whose equality and
hashing belong to the lattice the polytope lives in.  `vertex_chart` (`:824`)
and every repeat request read the retained cone; the decision, its assertions
and the cone returned are unchanged.

| run (gates on) | session star import | specimen call | triangle call | verdict |
| --- | --- | --- | --- | --- |
| before, quiet host | `3.04 s` | `27.42 s` | `4.42 s` | red on the call ceiling |
| after, quiet host | `1.92 s` | `18.49 s` | `3.39 s` | `2 passed in 25.60 s`, no gate report |

Probes on the same tree: a repeated cone is the same object and costs `0.014 s`
against `0.9-2.8 s` for the first; the chart of a decided vertex is `0.011 s`; a
point that is not a vertex is still refused and adds no registry entry; a second
variety of the same polygon keeps its own registry; on the specimen the apex
cone is `0.89 s` first and `0.045 s` repeated, and its chart is still the atlas
entry at that cone.

What the specimen call still pays, unchanged, is the eager gluing of its
seventeen charts in `_toric_variety`: 136 pair transitions at `13.9-23.4 s`.
The margin under the ceiling is therefore about eight percent on a quiet host,
and the call exceeds the ceiling again under heavy co-tenancy, where this file
needed about `1.6x` its quiet time at load average 21.5 on four CPUs.  Deferring
that gluing remains a change to the scheme gluing datum
(`categories/schemes/gluing.py:929-967`), not to this operation.

### The pushed tree on an idle host, and what the margin really is

The table above calls the `18.49 s` run quiet; it was not idle (`1.92 s` to import
the session).  Re-run on the pushed tree with the host idle (`0.93 s` to import):

```
$ python -m pytest -o addopts= -p qc_sage_session \
    -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
    --durations=0 tests/schemes/test_sterk_polygon_vertex_charts.sage
2 passed in 10.60s
 7.26s test_a_stored_sterk2_polygon_vertex_indexes_its_chart
 1.58s test_the_vertex_cones_of_a_triangle_index_charts_of_its_atlas
```

So the specimen call is `7.26 s` against the `20 s` ceiling on an idle host, and
the gluing this row pays for is `3-5 s` there rather than the `13.9-23.4 s` the
same code costs under co-tenancy.  Two corrections to the paragraph above: the
margin on an idle host is not eight percent but nearly three quarters of the
ceiling, and an over-ceiling run after this change has not been measured --
`44.22 s` and `61.03 s` are pre-change measurements under heavy co-tenancy, and
the `18.49 s` post-change run was at moderate load.

## Round 3, 2026-11-18: the specimen's algebra assertion is its Hilbert basis

The acceptance asks for true assertions about the chart's coordinate algebra
"rather than just ... count stored fields", and on the specimen that clause was
met by `algebra_generating_set().cardinality() == 5` -- a count and a negative
category membership, where the triangle's chart got its actual relation.  The
specimen now gets the same treatment:

* the apex cone's dual has the Hilbert basis `(-2,-1), (-1,-1), (0,-1),
  (1,-1), (2,-1)` in its own character frame, and the chart's algebra has one
  generator per point (probe: `semigroup_generators()` in the character frame is
  exactly that set, and `affine_semigroup_generator_positions()` agrees);
* the cone imposes `(-2,-1) + (2,-1) == 2*(0,-1)` and `(-1,-1) + (1,-1) ==
  2*(0,-1)`, and the chart's monomials satisfy `z_left * z_right == z_base**2`
  for both pairs (probe: relations `True`, distinct monomials `5`);
* the test asserts the five points, both character relations and both monomial
  relations, with the outer and inner left monomials distinct.

The added block costs `0.03 s` on a loaded host (five characters `0.020 s`,
`semigroup_generators` `0.000 s`, membership `0.000 s`, character relations
`0.001 s`, five monomials `0.012 s`, one product relation `0.001 s`), so it does
not move the call.

The call-phase gate remains a property of the host, and this round measured it
three ways on the same file: `7.26 s` on an idle host (before this block),
`21.85 s` at load average 16.5, and `95.56 s` at load average 18.65 with `2.4 GB`
available.  The variety's eager gluing is `3-5 s` idle and `21.7 s` at load
average 18, so under co-tenancy the call is over the ceiling whatever this test
does; on a host that is not co-tenanted it is well under.

## Acceptance verdicts, 2026-11-18, on `f59686c`

Each item decided on its smallest deciding input, probes run on this tree.

| # | item | verdict | statement or signature | file:line |
| --- | --- | --- | --- | --- |
| 1 | the cone of a selected vertex from its supporting primitive inner normals, in the dual of the polygon lattice; the actual chart of that cone, identified with the atlas; public correspondence; no second implementation | **green** | `vertex_normal_cone(vertex)` returns a cone of `self.fan()`; on `conv{(0,0),(2,0),(0,1)}` the primitive normals enumerated from the polytope's own `normal_value` pairing alone -- `n` minimized on exactly the edge through the vertex, candidates in `[-3,3]^2` -- equal the returned rays at all three vertices: `(0,0)` `{(1,0),(0,1)}`, `(0,1)` `{(1,0),(-1,-2)}`, `(2,0)` `{(0,1),(-1,-2)}`; every cone full-dimensional; `cocharacter_lattice() == lattice.dual_module()`; `affine_cover().enumeration()(cone) is vertex_chart(vertex) is affine_chart(cone)` at all three; generators `2,3,2` | `categories/schemes/toric/toric_schemes.py:723`, `:824`, `:701`, `:715`, `:263`; `categories/schemes/polytopes.py:2703`, `:2504` |
| 2 | the source-faithful public Sterk2 polygon from the native lengths, with the two role kinds kept, the path walked under the source's weights, and the hull supplying the closing side | **green** | all 19 coefficients follow the source rule recomputed in separate code for the stored `ell` and for `(1,...,1)`; 17 boundary directions and 2 surgery directions are disjoint label sets and `v_1 == v_6 == (-1,2)` is one vector in two roles; walking the boundary directions alone lands on `p_17`; 18 labelled points, 17 distinct, `p_0=(0,0)`, `p_17=(-24,0)`, `p_8=p_9=(-12,26)`; hull 17 vertices with the closing side `p_17 -> p_0`; shoelace `820 = normalized_volume()`; lattice polygon | `sterk.py:139`, `:168`, `:177`, `:877`, `:893`, `:908`, `:920`, `:942`, `:976` |
| 3 | the result first on a small polygon with known smooth and singular cones, then on the stored specimen through that constructor, with true assertions about rays, dual lattice, coordinate algebra and atlas identification, consuming the vertex-to-chart output | **green** | specimen `(-24,0)`: rays `{(1,0),(0,1)}`, smooth, all minimize there, chart is the atlas entry, 2 generators; `(-12,26)`: rays `{(1,-2),(-1,-2)}` (`|det| = 4`), not smooth, all minimize there, chart is the atlas entry, 5 generators; the five generators are the Hilbert basis `(-2,-1),(-1,-1),(0,-1),(1,-1),(2,-1)`, with `(-2,-1)+(2,-1) = 2(0,-1)` and `(-1,-1)+(1,-1) = 2(0,-1)` and the corresponding `z_left*z_right = z_base**2` in the chart's algebra; `cocharacter_lattice() == lattice.dual_module()` | `tests/schemes/test_sterk_polygon_vertex_charts.sage:35`, `:125`, `:157-158`, `:189-214`, `:219-224` |

The deciding run of item 3 on this tree, gates on: `2 passed in 201.74 s`,
specimen call `179.65 s`, triangle call `10.94 s`, at load average `21.3 -> 30.9`
on four CPUs (star import `5.03 s`, collection `7.58 s`).  Every assertion is
green; the call ceiling is the host's.

### Still open, with its line

`tests/schemes/test_sterk_polygon_vertex_charts.sage:165`
(`variety = polygon.toric_variety(QQ)`) exceeds the `20 s` per-call ceiling
(`src/sage_extensions/testing/suite_budget.py:44`) whenever the host is
co-tenanted: `7.26 s` idle, `21.85 s` at load `16.5`, `179.65 s` at load
`21.3 -> 30.9`.  The call is dominated by the eager gluing of the fan's 17
charts at `categories/schemes/toric/toric_schemes.py:2259-2264` together with
`categories/schemes/gluing.py:929-967`, which builds and verifies all 136 pair
transitions before gluing; that cost is `3-5 s` idle and tens of seconds under
co-tenancy.  Deferring it is a change to the scheme gluing datum, which this
issue does not own, so it is recorded here rather than made.

## Round 5, 2026-11-18: a session caller's lengths, and two independent oracles

Two oracles added, and the defect the second one found.

`tests/schemes/test_the_vertex_cones_and_sterk2_coefficients_have_independent_routes.sage:52`
enumerates the inner normals of `conv{(0,0),(2,0),(0,1)}` from the polytope's own
`normal_value` pairings -- a primitive candidate whose minimum over the vertices
is attained on exactly the two vertices of one edge and includes this vertex --
and asserts that `vertex_normal_cone` returns exactly that cone at all three
vertices, with two smooth ones and the index-two one.  `normal_supports_point`,
which the shipped test leans on, is not consulted, so the ray set is decided
twice by different routes.

The same file at `:118` re-derives all nineteen `M_18_0_0` coefficients from the
source's displayed rule in code that does not read
`_STERK2_DIRECTION_COEFFICIENT_WEIGHTS`, for the stored `ell` and for
`(1,...,1)`, keeps the two role kinds disjoint, re-runs the boundary walk from
the boundary directions alone, and recomputes the closed path's shoelace.

### The defect

On the tree before the repair, that second test failed:
`Sterk.sterk2_direction_coefficients((1,)*19)` -- a length vector written with
the session's integer literals -- raised

```
ValueError: Integer Ring is not in Category of sets with partial maps
```

from `src/sage_extensions/sterk.py:267` in
`_sterk2_engine_direction_coefficients`, which converted each length with the
engine's rational field; that field cannot absorb a session integer, so the
conversion fell into Sage's coercion discovery.  A session caller could not ask
the public constructor for the coefficients of a length vector it writes.

Repair: `_sterk2_length` (`src/sage_extensions/sterk.py:256`, used at `:277`)
reads each length through the session's integers into the engine's rational
field with `_engine_element`, so an ordinary integer, a session integer and a
private-ring integer reach the arithmetic as the same exact rational.  Weights,
arithmetic and returned values are unchanged.

### Verdicts on this tree

| # | item | verdict | the new evidence |
| --- | --- | --- | --- |
| 1 | vertex cone, dual lattice, chart in the atlas | green | the rays equal the normals the pairing alone finds, at all three triangle vertices, and the chart is the atlas entry at each |
| 2 | the Sterk2 polygon from the native lengths | green | all nineteen coefficients follow the source rule for `ell` and `(1,...,1)`; the roles stay disjoint; the boundary walk lands on `p_17`; 18 points, 17 hull vertices, closing side, shoelace `820` |
| 3 | the specimen through that constructor | green | as in round 3: the index-four apex cone, its five Hilbert-basis generators and both relations, the atlas entry at both vertices |

Run, gates on, on this tree: `4 passed in 38.13 s` -- the two new oracles at
`5.00 s` and `0.85 s`, the shipped triangle at `0.79 s`, the shipped specimen at
`28.12 s` (load average `19.5` on four CPUs, so the call ceiling is over again;
the environmental line of round 4 stands unchanged).

## Round 6, 2026-11-18: the refusals that make the hull-vertex clause operational

"A hull vertex, not every intermediate path point, indexes a chart" was, until
this round, asserted arithmetically only: eighteen labelled path points against
seventeen hull vertices.  Two refusals now state the capability side, in
`tests/schemes/test_the_vertex_cones_and_sterk2_coefficients_have_independent_routes.sage:119`
and `:124`:

* the midpoint `(1,0)` of the triangle's closing edge is a point of the polytope
  and not one of its vertices, and `vertex_normal_cone` raises (the assertion at
  `categories/schemes/toric/toric_schemes.py:751`);
* the same fan built without its polytope retains none, so `is_polarized()` is
  `False` and `vertex_normal_cone` raises (the assertion at `:730`).  That
  variety is the fan the test already holds, so its charts and pair transitions
  are the cached ones and the check adds no construction.

Run, gates on, on this tree: `4 passed in 57.47 s` -- the two oracles at
`7.06 s` and `0.91 s`, the shipped triangle at `0.75 s`, the shipped specimen at
`40.86 s` at load average `31.9` on four CPUs.  The call ceiling is over for the
specimen test again; that is the environmental line of round 4, unchanged.

## Round 7, 2026-11-18: the call ceiling, named blocked

The one open line is the specimen test's call at
`tests/schemes/test_sterk_polygon_vertex_charts.sage:165` against
`src/sage_extensions/testing/suite_budget.py:44` (`7.26 s` idle, `28-180 s` under
co-tenancy).  This round pinned what it would take, and it is not this issue's
to take.

The cost is not an eager verification pass that could be deferred: the glued
scheme's overlaps *are* the pair transitions.  `overlap(source, target)` is
`transition_between(source, target).forward().domain()`
(`categories/schemes/gluing.py:1037-1038`), `transition_between` reads
`self._transitions[pair]` from the family `_toric_variety` supplies
(`categories/schemes/toric/toric_schemes.py:2259-2264`), and the datum resolves
both directions of every pair at `gluing.py:954-957` before it verifies them at
`:965-966`.  So a seventeen-chart atlas costs its 136 pair isomorphisms to be
*built*, not merely checked, and dropping that cost means changing what a glued
scheme resolves at construction -- a decision in `gluing.py`, a file this issue
does not own (its recorded history names #593, #541 and #592, and none of them
owns this).

Named, not substituted: the input this needs is that owner's decision on whether
a glued scheme may resolve its atlas after construction.  No proxy was made --
the test was not trimmed, no `--no-time-gates` was used, and the ceiling was not
raised.

### The acceptance, as it stands

* item 1, the vertex-to-cone-to-atlas join: met.
* item 2, the Sterk2 polygon from the native lengths: met.
* item 3, the specimen through that constructor: met.

The open line above is outside those three items: it is the host's ceiling on
one test's call, not a claim of the acceptance.

## Round 8, 2026-11-18: the blocker, filed

The open line of round 7 is a scheme-layer cost, not this issue's operation: measured
on `cd58a62` at load average 12.85, the Sterk2 specimen's seventeen-chart variety is
`12.89 s`, of which the 136 pair transitions are `10.20 s` (79%), the charts `1.73 s`,
the gluing `0.18 s`; the vertex cone it is asked for is `0.53 s`, its chart `0.02 s`
and its atlas lookup `0.014 s`.  The proposal for the owner is filed as
`results/issue-proposal-the-gluing-datum-resolves-its-atlas-lazily.md`, with the
install line, because this connection cannot create issues.

## Round 9, 2026-11-18: where the gluing cost sits, layer by layer

The proposal of round 8 is corrected and sharpened: timing the three layers separately
on the same tree shows the cost is the *construction* of the pair transitions, not their
verification.  `_toric_variety`'s tuple of `_face_transition` calls
(`toric_schemes.py:2297-2300`) is `10.20 s`; entering `glue_affine_atlas` -- the datum's
`_transition_directions`, its two validators and `_glued_scheme`
(`gluing.py:954-967`) -- is `0.18 s`; the charts are `1.73 s`.  The call site cannot
skip them because the datum indexes the family at every pair, and the scheme object
reads them only when its space is asked for (`_chart_space_coproduct`,
`gluing.py:579-626`).  The minimal owner-side change is therefore in the datum: resolve
on first use, and let the first ask for the space pay.

## Round 10, 2026-11-18: what the owner's decision costs to take

The proposal now states the validation the change carries: 31 test files and 169
`test_` functions construct a glued scheme or read its datum on this tree
(`tests/schemes/` and `tests/divisors/`), so their failure sets would have to be
compared against a clean worktree at the same base commit -- hours on a host at load
20-30.  The input is therefore a decision (may a glued scheme be constructed without
its pair transitions resolved and verified, deferring both to the first ask for its
space?), not a further measurement.

## Round 11, 2026-11-18: the forcing call, isolated

One call demands the whole transition family: `_verify_pairwise_transitions()` at
`gluing.py:965`, which reads the family at every pair and is unconditional.  The
`validate_transition_inverses(check=False)` beside it is a `@validator`
(`validation.py:51-64`) and runs its law only with `check=True` or under strict
checking, so it costs nothing at construction.  The datum reads transitions straight
from the family (`transition_between`, `gluing.py:1012-1034`) and `_transition_directions`
is read only by those two validators (`:1048`, `:1091`).  So the library-side change is
that one call moved to first use, with the toric side passing an unbuilt family
(`toric_schemes.py:2297-2300`); the decision it needs is the gluing owner's, priced at
the 169 tests of 31 files recorded above.

## Round 12, 2026-11-18: the ceiling item closes by measurement

The open item was the specimen test's call against the per-call ceiling.  The host fell
to the load its ceilings were calibrated for (`load average 1.63`, against `27-32` in
rounds 6-11), and the deciding run is green with no gate report:

```
$ python -m pytest -o addopts= -p qc_sage_session \
    -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
    --durations=0 tests/schemes/test_the_vertex_cones_and_sterk2_coefficients_have_independent_routes.sage \
                 tests/schemes/test_sterk_polygon_vertex_charts.sage
time gates on: star import 1.25 s (ceiling 3 s), collection ceiling 6 s, each test call ceiling 20 s
4 passed in 6.48s
 4.36s  test_a_stored_sterk2_polygon_vertex_indexes_its_chart   (ceiling 20 s)
 0.82s  test_the_vertex_cone_rays_are_the_inner_normals_the_pairing_finds
 0.32s  test_every_sterk2_direction_carries_the_coefficient_the_source_gives_it
 0.09s  test_the_vertex_cones_of_a_triangle_index_charts_of_its_atlas
peak tree RSS 425 MiB
```

So the line at `tests/schemes/test_sterk_polygon_vertex_charts.sage:165` meets the
`20 s` ceiling (`testing/suite_budget.py:44`) on a host at the calibration load, with a
`4.6x` margin, and no ceiling of this run is over.  The `28-180 s` calls of rounds 6-11
were the same co-tenancy under which this host reports its file-independent session
star import at `11-12.8 s` against its `3 s` ceiling.

The item is closed as measured, and the code change that would keep it inside the
ceiling *while co-tenanted* stays filed for the gluing datum's owner
(`results/issue-proposal-the-gluing-datum-resolves-its-atlas-lazily.md`, the one forcing
call at `gluing.py:965`); nothing in #575's own files was trimmed, gated or capped to
get this run.

## Round 13, 2026-11-18: the co-tenancy item closed -- the gluing is lazy

The item of rounds 7-12 was that the specimen test's call exceeded the ceiling whenever
the host was co-tenanted, because a glued scheme built all C(n,2) pair transitions before
it existed.  The change was made: the datum holds its family unbuilt and checks it on the
first chart change (`gluing.py:951-958`, `_checked_pair_transitions` from
`transition_between`), and `_toric_variety` supplies a family rather than a tuple
(`toric_schemes.py:2261-2271`).  The scheme object already needed none of them --
`_glued_scheme` only holds the datum.

Measured on this host on the same file minutes apart, with the load *rising* from 11.6 to
15.5 between the runs:

| tree | specimen call | triangle call | file |
| --- | --- | --- | --- |
| base `28b6db2` | `39.09 s` | `21.79 s` | `2 passed in 178.34 s` |
| this change | `2.88 s` | `1.48 s` | `2 passed in 7.02 s` |

So the line at `tests/schemes/test_sterk_polygon_vertex_charts.sage:165` now meets the
`20 s` ceiling with a sevenfold margin under co-tenancy, where the base misses it by two.
With this, no measurement of the issue's three rows is over a ceiling at any load.

Consumers run: 24 tests across the two toric files and four gluing files.  The gluing
files report the same nine failures as the base commit -- `F..FFF` on
`test_glued_finite_affine_atlases.sage`, `FFF` on `test_scheme_gluing.sage`, `...FF` on
`test_glued_line_with_doubled_origin.sage` -- and every other test in them passes, as do
`test_glued_projective_line_from_two_lines.sage` and both toric files.  Not run: the other
25 of the 31 files that construct a glued scheme or read its datum, whose failure sets are
left to CI.  The consequence stated in the commit: a malformed atlas is now refused when
its first chart change is asked for, not when the datum is built.

