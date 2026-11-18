# #578 the proper real chart domain's owned smooth inclusion, item by item

Pushed on `main` at `0ae8ecd0692d46160753d68dfd475a56370784e0`
(`1cc067f` the test, `0ae8ecd` the repair), on `f4e467f`.
Independently verified: `git ls-remote https://github.com/dzackgarza/sage-extensions.git refs/heads/main`
answers `0ae8ecd0692d46160753d68dfd475a56370784e0`.

Runtime: `~/sage-image/run.sh`, image `dzackgarza/sage@sha256:332aebe9b1361210466d7d5a6ac2df855f5795c9e8a1f013ecd9379b72323698`
(revision `6301b4e4`), Python 3.14.10. Every run below is

    PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src \
      /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
        -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --durations=0 <files>

with `~/ai-review-ci/tool-artifacts` bound at `/ci/tool-artifacts` and the tree at `/work`.

The specimen throughout is the real plane `R^2`, its chart `x, y` on the proper
open subset `{x != 0}`, the open submanifold that chart is the domain of, and
the point `(3, -1)` of the plane in it.  The contract's path is exactly
`tests/objects/test_the_proper_chart_domain_includes_smoothly.sage:44`:
`plane.open_submanifold_inclusion(domain)`.

## 1. Public red proof of the missing map constructor

On `f4e467f`, the box the repair is pushed onto,
`tests/objects/test_the_proper_chart_domain_includes_smoothly.sage` is red in
all three rows, `3 failed in 2.52 s`:

    tests/.../test_the_proper_chart_domain_includes_smoothly.sage:46
    E  assert None in Set of Morphisms from 2-dimensional open submanifold U of
       2-dimensional smooth manifold R^2, the domain of its chart U to
       2-dimensional smooth manifold R^2 in Category of smooth manifolds

    tests/.../test_the_proper_chart_domain_includes_smoothly.sage:65
    E  assert None in Set of Morphisms from ... (the same)

    /work/src/sage_extensions/categories/abstract_categories/mor_foundation.py:61
    E  TypeError: SmoothManifoldMor._element_constructor_() missing 1 required
       positional argument: 'chart_maps'

The third is the smooth map constructor itself: at `f4e467f`,
`src/sage_extensions/categories/manifolds.py:1362` is
`def _element_constructor_(self, topological_map, chart_maps): pass`, and
`SmoothManifolds.ParentMethods.open_submanifold_inclusion`
(`manifolds.py:2821` there) is a `pass` stub too, so the operation answers
`None` and the two membership rows say so.

## 2. The owned smooth inclusion, with its source and its target

`SmoothManifolds.ParentMethods.open_submanifold_inclusion`
(`src/sage_extensions/categories/manifolds.py:1673`) finds the chart that has
the open submanifold as its domain and builds the arrow through the smooth
morphisms' own Mor, `open_manifold.Mor(self)` (`manifolds.py:1701`).

Source and target are the rows
`tests/objects/test_the_proper_chart_domain_includes_smoothly.sage:49-50`
(`inclusion.domain() is domain`, `inclusion.codomain() is plane`), and the row
`:48` states that the chart the subset is the domain of is that subset, not the
plane.  The arrow's own Mor is `:46`, `inclusion in domain.Mor(plane)`: it is a
morphism of the smooth manifolds, not the ambient parent pointer that
`containing_manifold()` returns.

## 3. Point values: the same intrinsic point of the ambient manifold

`SmoothManifoldMor.ElementMethods._evaluate_point`
(`src/sage_extensions/categories/manifolds.py:1380`) reads the point in the
chart it is given in, evaluates the map's sections of that chart's function
ring, and builds the codomain point with those values in the target chart.

`..._includes_smoothly.sage:51`, `inclusion(inner) == point`, compares a point
of the plane given in the chart `U` with one given in the chart `base`; that
equality is the two SageManifolds points' own equality (`manifolds.py:919`), so
the row says the image is the same intrinsic point, not merely the same pair of
numbers.  `:52` reads the image's coordinates in the ambient chart `U` as
`(3, -1)`, and `:54-57` state that the inclusion's coordinate sections are
sections of the functions on the open submanifold and take `(3, -1)` at that
point.

## 4. The proper domain is preserved; no global chart and no engine map

* The map's source is the open submanifold (`:49`), and the chart presenting it
  is the one whose domain it is (`:48`), not the plane's global chart.
* `..._includes_smoothly.sage:60-68` states the negative side: the point
  `(0, 1)`, on `x = 0`, is refused by the inclusion
  (`pytest.raises(ValueError)`), because the restricted chart is what reads the
  point.  A global chart would accept it.
* The constructor takes one datum, the coordinate sections
  (`manifolds.py:1431`), each admitted by the source chart's ring of functions
  (`manifolds.py:1461` through `_admit_manifold_expression_family`,
  `manifolds.py:714`).  The map of points is derived from those sections
  (`manifolds.py:1349-1354`), so an unconstrained callable or a private engine
  map is not a datum this owner accepts.

## 5. Composition and chart restriction through the existing owners

`SmoothManifoldMor.ElementMethods.__mul__`
(`src/sage_extensions/categories/manifolds.py:1406`) substitutes the inner
map's sections in the outer map's with `_substitute_chart_coordinates`, and
re-raises the result in the composite's own source chart ring with
`_raise_manifold_expression` (`manifolds.py:1427`); both are the owners the
atlas transitions and the chart formulas already use, so a composite's
coordinate sections are sections of its own source chart's ring.

The row is `..._includes_smoothly.sage:70-95`: the map
`(x, y) |-> (x, y^2)` of the open submanifold (`:81`, built by
`domain.Mor(domain)` from the chart's own coordinate sections), composed with
the inclusion by `inclusion * squaring`.  `:88-89` state that the composite is
an arrow of `domain.Mor(plane)` with source the submanifold and target the
plane, `:90` that it carries `(3, -1)` to `(3, 1)` and `:91` that this is not
the image of the inclusion alone, and `:92-95` that its coordinate sections on
the chart take `(3, 1)`.

## Runs

Green, pushed tree:

    tests/objects/test_the_proper_chart_domain_includes_smoothly.sage
    3 passed in 5.42 s   (first row 3.64 s, others 0.03 s and 0.08 s)

Consumers of the touched owner, same command, `24 passed in 47.15 s`
(`tests/categories/test_the_euclidean_line_is_a_riemannian_manifold.sage`,
`tests/objects/test_a_hyperbolic_arrow_is_induced_by_an_isometry.sage`,
`tests/objects/test_manifold_atlas_transition_expressions.sage`,
`tests/objects/test_manifold_chart_coordinates.sage`,
`tests/objects/test_manifold_chart_section_products.sage`,
`tests/schemes/test_integral_affine_atlas_of_a_lattice_polygon.sage`,
`tests/schemes/test_lattice_affine_unit_shear.sage`), with one call-gate
overrun that this change does not cause:
`test_a_coordinate_of_a_complex_chart_is_a_section_valued_in_the_complex_field`
takes 42.86 s here and 194.14 s on `f4e467f` with the same command, so that
complex chart's cost is its own.

The same three rows were re-run after the rebases onto `f59686c` and `f4e467f`:
`3 passed`, first row 133.26 s and 28.60 s while the VM carried another
session's work (load average 27-31 on 4 CPUs).  A step timing under that load
puts the cost in the pre-existing construction of the plane and its chart on a
proper open subset (59.98 s for `SmoothManifolds()(2, "R^2")` plus the two
charts, no line of this change in that span) and 0.069 s in
`open_submanifold_inclusion` and 0.025 s in evaluating it.

Not touched, and said so here rather than left implicit:
`SmoothManifoldMor.weaken_to` and `as_ck_morphism`, the `C^k` presentation of a
smooth map, are still stubs (`manifolds.py:1400`, `manifolds.py:1403`); this
issue is the smooth inclusion, not the `C^k` functor.  The whole-tree session
plugin path `/ci/tool-artifacts` is not installed in the image and was bound
from `~/ai-review-ci` for these runs.
