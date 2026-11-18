# #577 chart section products, item by item, with the session gates run

Pushed on `main` at `57fe8b490ed0d15de5bdd563261575f2f07a0dd4` (`4b050da` the
tests of the quotient and the overlap, `57fe8b4` the two owner repairs, on
`43c8db6`; the products and the stereographic transition were pushed before
that at `f59686c`, on `7f33f66`).  Independently verified:
`git ls-remote https://github.com/dzackgarza/sage-extensions.git refs/heads/main`
answers `57fe8b490ed0d15de5bdd563261575f2f07a0dd4`.

Line numbers are of the tree this file is committed on.

Runtime: `~/sage-image/run.sh`, the pinned image, Python 3.14.10.  The session
gates run in the form the repository's own launchers use, with the CI
tool-artifacts bound at `/ci/tool-artifacts`:

    ~/sage-image/run.sh -w /work -b ~/ai-review-ci/tool-artifacts:/ci/tool-artifacts -b $TREE:/work -- \
      /bin/sh -c 'cd /work && \
        PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src \
        /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
          -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --durations=0 <files>'

## 1. Public red proof of the product recursion

`tests/objects/test_manifold_chart_section_products.sage:21` and `:41`, landed
at `c02640c`.  At `c02640c`'s parent `cee81aa` both fail with
`RecursionError: maximum recursion depth exceeded`; on `main` both pass.

## 2. The pointwise-algebra/module constructor owner

`src/sage_extensions/categories/algebras/algebras.py:1861`
`_element_of_unformed_module` and `:1891` `_element_from_unformed_module` cross
at the retained module's datum.  Two further holes at the same owner:
`algebras.py:3296` reads an integer literal as `unit_morphism()(ring(value))`;
`real_functions.py:582` `_ConstantMap` retains the value of a constant section,
lowered at `manifolds.py:458` and `manifolds.py:623`.

## 3. Ordinary products, powers and their values

On `R^2` with the chart `x, y`, at `(3, -2)`: `x*y = -6`, `x**2 = 9`,
`x**3 = 27`, `x**0 = 1`, `x*y*x = -18`, `-x = -3`, `2*x = 6`, `x-y = 5`, every
one an element of `chart.function_ring()`; they lower to `x*y`, `x^2`, `x^3`,
`x^2 + y^2`, `-x`, `2*x`, and `ring(2)` to `2`.
`tests/objects/test_manifold_chart_section_products.sage:21`, `:41`.

## 4. The consuming stereographic transition

`SmoothManifolds().sphere(2)`: `U_N(3,-2) -> (3/13, -2/13)`, the inverse
carries it back to `(3,-2)`, and the pole `(0,0)` is refused.
`SmoothManifolds().sphere(1)`: `2 -> 1/2` and back, `0` refused.
`manifolds.py:1962` `inversion`;
`tests/objects/test_the_stereographic_transition_of_the_sphere_is_a_quotient_of_sections.sage:26`,
`:45`, `:58`, `:71`.

## 5. The reciprocal and the restriction, at their owners

`manifolds.py:125` `ManifoldAtlasChart.section_ratio(numerator, denominator)`
states the quotient `g/f` as the function on the open subset `{f != 0}`
(`_SectionRatio`, `manifolds.py:384`), admitted for sections of the chart's own
ring at `manifolds.py:497`; the ring gains no inverse (`x**-1` refuses with
`no inverse computation is available for ... in its ambient monoid`, `x/y` with
`TypeError`).  The restriction owner is repaired in two places:
`chart_on_open_subset` cuts its subset inside the source chart's own domain
(`manifolds.py:1101`), and a point of an open submanifold is read as a point of
the manifold it lies in (`manifolds.py:1181`, `_is_a_point_in` at `:743`,
`_coordinates_of_a_point_in` at `:760`).
Measured: on `R^2`, `y/x` on `{x != 0}` at that open subset's own point is
`-2/3`, the quotient of the restricted sections there, refused at `x = 0`; on
`S^2`, `U_N cap U_S` is cut inside `U_N`, the restricted sections take
`3, -2` and `13`, and `x1/|x|^2` is `3/13`, their quotient.
`tests/objects/test_the_stereographic_transition_of_the_sphere_is_a_quotient_of_sections.sage:82`,
`:108`; at `43c8db6` they fail with `manifolds.py:1128 TypeError:
'SmoothManifolds.element_class' object is not iterable` and `manifolds.py:1062
-> sage/manifolds/chart.py:2456 ValueError: the specified subset is not a
subset of the domain of definition of the chart`.

## 6. The session gates

`tests/objects/test_the_stereographic_transition_of_the_sphere_is_a_quotient_of_sections.sage`,
six tests, all gates on:

    time gates on: star import 1.78 s (ceiling 3 s), collection ceiling 6 s, each test call ceiling 20 s
    collected 6 items
    ... 6 passed in 13.28s
    7.39s call  ...::test_a_sum_of_squares_of_chart_coordinates_is_a_section_of_the_chart_function_ring

The three consumer files that run here
(`test_the_proper_chart_domain_includes_smoothly.sage`,
`test_manifold_chart_coordinates.sage`,
`test_manifold_chart_section_products.sage`), nine tests:

    time gates on: star import 1.82 s (ceiling 3 s), collection ceiling 6 s, each test call ceiling 20 s
    collected 9 items
    ... 9 passed in 11.24s

The test lint is one of the plugins loaded above, and it ends a run red on any
finding; neither run reported one.

One earlier sample of the same form tripped the session star-import gate --
`session star import took 3.95 s; the measured ceiling is 3 s` -- with the same
six tests passing in 22.13 s.  That gate is the import of the session, not a
test row, and this host was at load 18.5 with 12 of 15 GB in use; the same file
measured 2.35 s and an untouched file, `test_manifold_chart_coordinates.sage`,
2.13 s in the same form.  The four samples of that gate here are 1.78, 1.82,
2.13, 2.35 and 3.95 s.

`tests/objects/test_manifold_atlas_transition_expressions.sage` was run without
the gates (`--timeout` raised), because its complex chart test alone takes
448-925 s on this host and is over the per-call ceiling on `main` too; it
passes, five tests, in the log of the round that changed the files it covers.

## 7. What stays separate

`#93`'s enumerated-function placement and `#256`'s integral-affine surgery and
sphere acceptance are untouched: the files changed for this issue are
`src/sage_extensions/categories/manifolds.py`,
`src/sage_extensions/categories/algebras/algebras.py`,
`src/sage_extensions/categories/functions/real_functions.py` and the two test
files named above.

The `ast-grep` gates do not run on this host (`ast-grep` is not installed), so
they are neither green nor red here.
