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

## The stored specimen's deciding call is over the per-call ceiling

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
