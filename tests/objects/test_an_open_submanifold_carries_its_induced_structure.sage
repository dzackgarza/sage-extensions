r"""An open submanifold carries the ambient charts restricted, with the initial topology.

An open subset of a manifold, with the restricted atlas, is a manifold of the same
dimension and class (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Example 1.4),
and its inclusion is the presentation: the domain of the inclusion is the open
submanifold, the charts of the ambient manifold restrict to charts of it, and a subset
of it is open exactly when its image is open in the ambient manifold (Mathlib,
``TopologicalSpace.induced``).  That last statement is a rule about images, retained as
a predicate; it is not a list of the subsets of either manifold.

The specimen is the smallest manifold that decides it: the real line cut where its
coordinate does not vanish, the two open halves ``{x != 0}``, and the single chart the
line presents.  A chart of the line read on the punctured line is a chart of the
punctured line, and an integral-affine atlas of the line restricted to it is an
integral-affine atlas of the same model.
"""

import pytest

from sage_extensions.all import *


def _the_punctured_line():
    r"""The real line, its chart ``x``, and the open submanifold ``{x != 0}`` it is the domain of."""
    line = SmoothManifolds()(1, "R")
    chart = line.chart("x", "x")
    punctured = line.chart_on_open_subset("U", "x", "x", (chart.coordinate(0),), same_coordinates=True)
    return line, chart, punctured, punctured.domain()


def test_the_open_submanifold_of_an_inclusion_is_its_domain_with_the_ambient_charts() -> None:
    r"""The open submanifold is the inclusion's domain, and the line's chart ``x`` is a chart of it.

    A second manifold on the same points would be a second authority for the same
    subset, so the returned object is the inclusion's domain; the chart ``x`` of the
    line, read on the punctured line, is registered on it under the same label, and it
    takes the point ``3`` to the coordinate ``3``.
    """
    line, chart, _punctured, domain = _the_punctured_line()
    inclusion = line.open_submanifold_inclusion(domain)
    submanifold = line.open_submanifold(inclusion)
    inner = domain(line((3,)))

    assert submanifold in SmoothManifolds()
    assert submanifold is domain
    assert submanifold.dimension() == line.dimension()
    assert submanifold.manifold_structure() == line.manifold_structure()
    assert sorted(tuple(submanifold.chart_labels())) == sorted(tuple(line.chart_labels()))
    assert submanifold.atlas()["x"].domain() is submanifold
    assert tuple(submanifold.atlas()["x"](inner)) == tuple(line.atlas()["x"](inclusion(inner)))
    assert tuple(submanifold.atlas()["x"](inner)) == (RR(3),)


def test_a_subset_of_the_open_submanifold_is_open_exactly_when_its_image_is() -> None:
    r"""The empty subset and the whole submanifold are open, and a point is asked of the ambient line.

    The initial topology is a predicate: a subset of the submanifold is open exactly
    when its image is open in the ambient manifold, so the question of a subset that is
    not the empty one and not the whole one is the ambient manifold's to decide.  The
    ambient line decides the empty set and itself, and refuses the rest rather than
    enumerating the subsets of an infinite set.
    """
    line, _chart, _punctured, domain = _the_punctured_line()
    submanifold = line.open_submanifold(line.open_submanifold_inclusion(domain))

    assert submanifold in SmoothManifolds()
    power = submanifold.power_set()
    assert submanifold.is_open_subset(power.bottom())
    assert submanifold.is_open_subset(power.top())
    with pytest.raises(AssertionError):
        submanifold.is_open_subset(power((domain(line((3,))),)))


def test_the_restricted_atlas_is_the_affine_atlas_read_on_the_open_submanifold() -> None:
    r"""The restricted atlas is an atlas of the punctured line, into the line's own model.

    The line's affine atlas has one chart, on the whole line, whose affine map reads a
    point's coordinate.  Restricted along the inclusion it is one chart on the whole
    punctured line, into the same model, and its affine map is the line's chart
    composed with the inclusion: the point ``3`` goes to the model point ``3``.
    """
    line, _chart, _punctured, domain = _the_punctured_line()
    inclusion = line.open_submanifold_inclusion(domain)
    lattice = ZZ.free_module(1)
    model = RR.free_module(lattice.module_generating_set())
    atlas = IntegralAffineAtlases().on(
        line,
        model,
        {line: line},
        {line: Sets().Mor(line, line).identity()},
        {line: Sets().Mor(line, model)(lambda point: model(tuple(point.coordinates())))},
        {},
        {},
    )

    restricted = atlas.restrict(inclusion)
    inner = domain(line((3,)))

    assert restricted in IntegralAffineAtlases()
    assert restricted.underlying_smooth_manifold() is domain
    assert restricted.affine_model() is model
    assert tuple(restricted.affine_charts()) == (domain,)
    assert restricted.chart_domains()[domain] is domain
    assert restricted.chart_domain_inclusion(domain).domain() is domain
    assert restricted.chart_domain_inclusion(domain).codomain() is domain
    assert tuple(restricted.affine_chart(domain)(inner)) == (RR(3),)
    assert restricted.integral_affine_manifold().underlying_smooth_manifold() is domain
