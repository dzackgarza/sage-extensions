# #578 the proper real chart domain's owned smooth inclusion, item by item

Pushed on `main` at `0ae8ecd0692d46160753d68dfd475a56370784e0`
(`1cc067f` the test, `0ae8ecd` the repair), on `f4e467f`.
Independently verified: `git ls-remote https://github.com/dzackgarza/sage-extensions.git refs/heads/main`
answers `0ae8ecd0692d46160753d68dfd475a56370784e0`.

The line numbers of the first section are those of the tree it measured
(`c71a004`); that tree was rewritten by the repair in the second pass below,
which re-decided every item on the tree pushed after it and gives the current
numbers.

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
(`src/sage_extensions/categories/manifolds.py:1738`) finds the chart that has
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
  (`manifolds.py:1353-1354`), so an unconstrained callable or a private engine
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

## Second pass: every acceptance item decided again, on one turn's tree

Rebased onto `fd029ab`, where the hyperbolic arrow now holds the smooth
morphism its coordinate sections define (that round builds on
`SmoothManifoldMor._element_constructor_`), the two commits of this pass are
`dd29434` (test) and `deead84` (fix), and this note is the head.

1. **Public red proof of the missing map constructor.** Decided on `f4e467f`
   in a tree of its own: `3 failed in 10.36 s`, the rows at
   `tests/objects/test_the_proper_chart_domain_includes_smoothly.sage:46` and
   `:65` (`assert None in Set of Morphisms from 2-dimensional open submanifold
   U of 2-dimensional smooth manifold R^2, ... to ... R^2 in Category of smooth
   manifolds`) and the constructor itself at
   `categories/abstract_categories/mor_foundation.py:61`,
   `TypeError: SmoothManifoldMor._element_constructor_() missing 1 required
   positional argument: 'chart_maps'`, from the `pass` stub at
   `manifolds.py:1362` (and the operation's own stub at `manifolds.py:2821`).

2. **The owned inclusion, source and target.** Probed on this tree:
   `inclusion in domain.Mor(plane)` True, `inclusion.parent() is
   domain.Mor(plane)` True, `inclusion.domain() is domain` True,
   `inclusion.codomain() is plane` True, `chart.domain() is domain` True,
   `domain.containing_manifold() is plane` True — the last is the relation the
   issue says is not the morphism.  Source:
   `SmoothManifolds.ParentMethods.open_submanifold_inclusion`,
   `src/sage_extensions/categories/manifolds.py:1738`;
   `SmoothManifoldMor._element_constructor_`, `manifolds.py:1496`.

3. **Point values are the same intrinsic point of the ambient manifold.**
   `inclusion(inner) == point` True for `inner` given in the chart `U` of the
   domain and `point = plane((3, -1), "base")`; the image's coordinates in the
   ambient chart `U` are `(3, -1)`; the two coordinate sections are sections of
   `domain.atlas()["U"].function_ring()` and take `(3, -1)` there.
   `_evaluate_point`, `manifolds.py:1440`; the point equality is
   `manifolds.py:919`.

4. **Restriction and composition through the existing owners.** Two halves,
   both decided.
   * Composition with a map written on the open subset's chart: green
     (`(x, y) |-> (x, y^2)` composed with the inclusion carries `(3, -1)` to
     `(3, 1)`), `__mul__` at `manifolds.py:1466`.
   * Restriction of a map of the plane: at `c71a004` refused —
     `tests/objects/test_the_proper_chart_domain_includes_smoothly.sage:118`,
     `AssertionError: cannot read Generic endomorphism ... on the chart 'U'`,
     `manifolds.py:1372`, `1 failed, 4 passed in 8.08 s`.  Now green by
     `SmoothManifoldMor.ElementMethods._representation_written_on`
     (`manifolds.py:1392`), which restates the outer map on the chart the inner
     map states its values in through
     `ManifoldAtlasTransition.forward_expressions` and the source chart's ring:
     `doubling * inclusion` is a map `U -> R^2` carrying `(3, -1)` to
     `(3, -2)`, with sections on `("U", "base")`
     (`...includes_smoothly.sage:98-127`).  With no change of coordinates
     stated the composition is refused and names the missing transition
     (`:130-147`), rather than the two charts being assumed to agree.  The
     restatement is used only where the atlas states the change on the whole
     chart (empty `source_overlap`): no representation here records the subset a
     formula holds on, so a change defined on a proper subset is refused.

5. **The proper domain is preserved; no global chart, no engine map.** The
   point `(0, 1)` on `x = 0` is refused by the inclusion
   (`ValueError: the point does not belong to the domain of Chart (U, (x, y))`,
   `...includes_smoothly.sage:60-68`); the map's only representation is on the
   open subset's own chart (`(('U', 'U'),)`); the constructor's one datum is
   the coordinate sections, each admitted by the source chart's ring
   (`manifolds.py:1496` and `:1526`), and the map of points is derived from
   them (`manifolds.py:1353-1354`), so a bare callable or a private engine map
   is not accepted.

6. **Scope.** The public additions are the two methods above; the neighbouring
   stage stubs are untouched: `weaken_to` (`manifolds.py:1460`),
   `as_ck_morphism` (`manifolds.py:1463`), `SmoothManifolds.ParentMethods`'
   `as_ck_manifold`, `underlying_topological_manifold` and `tangent_bundle`
   (`manifolds.py:1768-1774`), and no sphere or general manifold feature is
   added.

Runs on this turn's tree, time gates on:

    5 passed in 10.79s   tests/objects/test_the_proper_chart_domain_includes_smoothly.sage
    15 passed in 21.68s  that file, the hyperbolic arrow file and
                         test_the_standard_hyperbolic_plane_is_a_smooth_manifold.sage
                         together, after the rebase onto fd029ab

and the seven smooth-manifold consumer files earlier in this pass,
`25 passed in 219.96 s`, with the one pre-existing call-gate overrun
(`test_a_coordinate_of_a_complex_chart_is_a_section_valued_in_the_complex_field`,
200.29 s here, 194.14 s on the parent tree) named rather than fixed.

## Third pass: the six items decided again, and the last composition case closed

On this tree the two commits are `fb99f6f` (test) and `ec6a6ea` (fix); this
note is the head.  The line numbers below are this tree's; the first two
sections keep their own.

1. **Public red proof of the missing map constructor.** Delivered; unchanged by
   this pass.  On `f4e467f`: `3 failed in 10.36 s`, the rows at
   `tests/objects/test_the_proper_chart_domain_includes_smoothly.sage:46` and
   `:65` (`assert None in Set of Morphisms from ... open submanifold U ... to
   ... R^2 in Category of smooth manifolds`) and
   `categories/abstract_categories/mor_foundation.py:61`
   (`TypeError: SmoothManifoldMor._element_constructor_() missing 1 required
   positional argument: 'chart_maps'`, stub `manifolds.py:1362` there).

2. **The owned inclusion, source and target.** Delivered.
   `SmoothManifolds.ParentMethods.open_submanifold_inclusion`,
   `manifolds.py:1796`; the arrow is built at `manifolds.py:1824`.  Probed on
   this tree: in `domain.Mor(plane)`, `domain() is domain`,
   `codomain() is plane`, `chart.domain() is domain`.

3. **Point values are the same intrinsic point.** Delivered.
   `_evaluate_point`, `manifolds.py:1454`: the inclusion of the chart domain of
   `{x != 0}` carries `(3, -1)` to the same point of the plane, given in the
   domain's chart `U` and read in the plane's chart `base`; the image's
   coordinates in the ambient chart are `(3, -1)` and the two sections are
   sections of the open subset's function ring.

4. **Restriction and composition.** Delivered in full, and this is what this
   pass closed.  Three cases, all green in the file:
   * a map written on the open subset's chart composed with the inclusion
     (`:70-95`);
   * a map of the plane written on the plane's chart `base` restricted to the
     open subset through the atlas state of `U -> base` (`:98-127`), refused
     when no change of coordinates is stated (`:130-147`);
   * a map of the plane written on the *other* proper chart, `V` on
     `{x + y != 0}`, restricted through the overlap of the two charts
     (`:150-190`): red at `2be6b8e` on `:179` with
     `manifolds.py:1422`, `AssertionError: cannot restate Generic endomorphism
     ... its change of coordinates to the chart 'V' is defined only where (...)
     do not vanish`, `1 failed, 5 passed in 14.59 s`; now the composite is
     stated on `("U", "V")` with domain functions `x` and `x + y`, carries
     `(3, -1)` to the point of `V`-coordinates `(2, -2)`, and refuses
     `(1, -1)`, where `x + y` vanishes.

   The owner now records a representation's domain:
   `chart_map_domain` (`manifolds.py:1368`), admitted by the constructor's
   `domains` argument (`manifolds.py:1529`, `:1585`), used by evaluation
   (`:1454`), by composition (`:1486`) and by the restatement through an atlas
   transition (`:1408`).  A map stated only by its coordinate sections is
   unchanged: each pair defaults to the whole chart.

5. **The proper domain is preserved.** Delivered.  `(0, 1)` on `x = 0` is
   refused by the inclusion (`ValueError: the point does not belong to the
   domain of Chart (U, (x, y))`, `:60-68`), the map's source is the open
   submanifold, and its one datum is the coordinate sections, admitted by the
   source chart's ring (`manifolds.py:1529`, `:1570`).

6. **Scope.** The public additions are the inclusion operation and the smooth
   morphism owner's constructor, accessors and composition; the neighbouring
   stage stubs are untouched: `weaken_to` (`manifolds.py:1480`),
   `as_ck_morphism` (`:1483`), and `SmoothManifolds.ParentMethods`'
   `as_ck_manifold`/`underlying_topological_manifold`/`tangent_bundle`
   (`:1826-1832`).

Runs: `6 passed in 27.48 s` for this file; `29 passed in 454.38 s` for the
eight consumer files, with two pre-existing call-gate overruns under a load
average of 30 on 4 CPUs (`test_a_coordinate_of_a_complex_chart_is_a_section_valued_in_the_complex_field`
at 406.33 s against 194.14 s on the parent tree, and
`test_the_standard_riemannian_object_is_the_euclidean_line` at 26.40 s).

Rebased onto `1fa5e73`, which changes the chart-domain path itself (an open
submanifold inherits the structure of the manifold it is open in, and its points
are that manifold's points), the same rows are green again on the rebased tree:
`6 passed in 7.59 s` for this file and `29 passed in 62.64 s` for the eight
consumer files, with the complex chart's call gate still over at 53.09 s.

### Line numbers of this record against the tree it is pushed on

The sections above were written on three different trees, and each was rewritten
by the rebases that carried it to `main`.  The first measures `c71a004` and the
second `2be6b8e`, as the notes at their heads say.  The third claims to give
"this tree's" numbers and was written on `e86cdb2`; the two chart-domain commits
that `1fa5e73` carries above it add 57 lines to `manifolds.py`, so every library
line it cites is 57 higher here:

| third pass | here | symbol or line |
| --- | --- | --- |
| 1368 | 1425 | `SmoothManifoldMor.ElementMethods.chart_map_domain` |
| 1408 | 1465 | `SmoothManifoldMor.ElementMethods._representation_written_on` |
| 1454 | 1511 | `SmoothManifoldMor.ElementMethods._evaluate_point` |
| 1486 | 1543 | `SmoothManifoldMor.ElementMethods.__mul__` |
| 1529 | 1586 | `SmoothManifoldMor._element_constructor_` |
| 1570 | 1627 | the coordinate sections admitted in it |
| 1585 | 1642 | the representation domains admitted in it |
| 1796 | 1853 | `SmoothManifolds.ParentMethods.open_submanifold_inclusion` |
| 1824 | 1881 | the inclusion it builds |
| 1480, 1483 | 1537, 1540 | `weaken_to`, `as_ck_morphism` |
| 1826-1832 | 1883-1889 | `as_ck_manifold`, `underlying_topological_manifold`, `tangent_bundle` |

Its test lines need no correction: the file's first five rows are unchanged by
the rebase and the sixth is at `:150-193`, where the third pass already puts it.
The library lines quoted inside the red transcripts (`manifolds.py:1362` in the
first section, `:1372` and `:1422` in the second and third) are the lines the
failure was raised on in those trees, and are not rewritten.

### CI's verdict on this work

The repository runs its workflows on every push
(`.github/workflows/development.yml:3`, `push: {}`), and that workflow's
concurrency is `group: ${{ github.workflow }}-${{ github.ref }}` with
`cancel-in-progress: true` (`development.yml:16-18`).  Pushes to `main` arrive
every 30-90 s from concurrent sessions, so each run is cancelled by the next one
before a runner is assigned.  Read from the public Actions API (no token: the
repository reports `"private": false`):

* every head this work pushed is `cancelled` — `0ae8ecd` (run 1442),
  `2be6b8e` (1457), `cd58a62` (1469), `6a6f0c5` (1470), and the README example
  runs beside each;
* the job of `6a6f0c5`, `qc-ci / qc` (job 134602728029), ended `cancelled` with
  no runner assigned and no steps (`runner_id: 0`, `steps: []`), 59 s after it
  was queued and in the same second that the run for `1042213c` was created;
* of the runs on `main`, 807 concluded `success`, 785 `failure` and 886
  `cancelled`, so the workflows do run; it is these heads that never got a slot.

So there is no CI verdict on the code in this work: the run for its head was
superseded, not failed.  A verdict would need a re-run of that workflow (a write
on the repository, itself subject to the same cancellation) or a push whose run
stays newest long enough to be picked up.  No local re-run substitutes for it.
