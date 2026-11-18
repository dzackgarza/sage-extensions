r"""A singular integral-affine space of a fixed dimension is stated from its regular locus.

The general category states a singular integral-affine space by four data: one
topological space, the singular locus selected in it, the regular locus selected in it,
and the integral-affine manifold on that regular locus.  The fixed-dimension stratum
adds the dimension, which the regular locus must have, and the singular local models,
which a stratum with none selected states as none.

The specimen is the smallest one that decides it: the real line with its one-chart
integral-affine structure, the origin as the singular locus, and the punctured line as
the regular locus.  The stratum of dimension one states it; the stratum of dimension one
refuses the plane's two-dimensional structure, because a line's regular locus is a line.
"""

import pytest

from sage_extensions.all import *


def _the_line_with_its_affine_atlas():
    r"""The line, the punctured line, the affine model, and the line's atlas."""
    line = SmoothManifolds()(1, "R")
    chart = line.chart("x", "x")
    punctured = line.chart_on_open_subset("U", "x", "x", (chart.coordinate(0),))
    model = RR.free_module(ZZ.free_module(1).module_generating_set())
    atlas = IntegralAffineAtlases().on(
        line,
        model,
        {line: line},
        {line: Sets().Mor(line, line).identity()},
        {line: Sets().Mor(line, model)(lambda point: model(tuple(point.coordinates())))},
        {},
        {},
    )
    return line, punctured.domain(), model, atlas


def _the_singular_line():
    r"""The line, its structure, the origin's selection, and the punctured line's selection."""
    line, region, _model, atlas = _the_line_with_its_affine_atlas()
    structure = IntegralAffineManifolds().on(line, atlas)
    singular = line.power_set()((line((0,)),))
    return line, region, structure, singular.inclusion(), line.open_submanifold_inclusion(region)


def test_the_dimension_stratum_states_the_space_from_its_regular_locus() -> None:
    r"""The state of the line is one topological space, two selected parts and one affine manifold.

    The stratum of dimension one reports the line, the origin's selection, the punctured
    line's selection, the line's structure on it, its dimension, and no singular local
    models, because none were selected.
    """
    line, region, structure, singular_inclusion, region_inclusion = _the_singular_line()
    regular_structure = structure.affine_atlas().restrict(region_inclusion).integral_affine_manifold()
    space = SingularIntegralAffineSpaces(1).on(
        line, singular_inclusion, region_inclusion, regular_structure
    )

    assert space in SingularIntegralAffineSpaces()
    assert space in SingularIntegralAffineSpaces(1)
    assert space.underlying_topological_space() is line
    assert space.singular_locus_inclusion() is singular_inclusion
    assert space.regular_locus_inclusion() is region_inclusion
    assert space.regular_affine_manifold() is regular_structure
    assert space.singular_locus() is singular_inclusion.domain()
    assert space.regular_locus()[0] is region_inclusion
    assert space.local_models() is None
    assert int(space.regular_affine_manifold().dimension()) == 1


def test_the_dimension_stratum_refuses_an_affine_structure_of_another_dimension() -> None:
    r"""A one-dimensional stratum refuses the plane's two-dimensional regular locus.

    The regular locus of a dimension-one space is a line, so a two-dimensional affine
    structure is not its structure: the stratum refuses it rather than stating a line
    with a plane's atlas.
    """
    line, _region, _structure, singular_inclusion, _region_inclusion = _the_singular_line()
    plane = SmoothManifolds()(2, "R^2")
    plane_chart = plane.chart("x y", "x y")
    model = RR.free_module(ZZ.free_module(2).module_generating_set())
    plane_atlas = IntegralAffineAtlases().on(
        plane,
        model,
        {plane: plane},
        {plane: Sets().Mor(plane, plane).identity()},
        {plane: Sets().Mor(plane, model)(lambda point: model(tuple(point.coordinates())))},
        {},
        {},
    )
    plane_structure = IntegralAffineManifolds().on(plane, plane_atlas)
    plane_singular = plane.power_set()((plane((0, 0)),))
    plane_region = Sets().Mor(plane, plane).identity()

    assert plane_chart.domain() is plane
    assert int(plane_structure.dimension()) == 2
    with pytest.raises(AssertionError):
        SingularIntegralAffineSpaces(1).on(
            plane, plane_singular.inclusion(), plane_region, plane_structure
        )


def test_the_dimension_stratums_surgery_is_the_general_surgerys_result_in_that_stratum() -> None:
    r"""The stratum's surgery states the line, singular at the origin, integral-affine on the punctured line.

    The construction is the general one; the stratum adds its dimension and the local
    models it is given, so the result is the same space in the stratum of dimension one.
    """
    line, region, structure, singular_inclusion, region_inclusion = _the_singular_line()
    replacement = SingularIntegralAffineSpaces().on(
        line, singular_inclusion, Sets().Mor(line, line).identity(), structure
    )
    model = structure.affine_atlas().affine_model()
    collar_chart = Sets().Mor(region, model)(lambda point: model(tuple(point.coordinates())))
    source_collar = IntegralAffineCollars().on(
        structure, region_inclusion, region_inclusion, collar_chart
    )
    target_collar = IntegralAffineCollars().on(
        structure, region_inclusion, region_inclusion, collar_chart
    )

    operated = SingularIntegralAffineSpaces(1).surgery(
        region_inclusion,
        replacement,
        Sets().Mor(region, region).identity(),
        (source_collar, target_collar),
        None,
    )
    general = SingularIntegralAffineSpaces().surgery(
        region_inclusion,
        replacement,
        Sets().Mor(region, region).identity(),
        (source_collar, target_collar),
    )

    assert operated in SingularIntegralAffineSpaces(1)
    assert operated.underlying_topological_space() is line
    assert operated.singular_locus_inclusion() is general.singular_locus_inclusion()
    assert operated.regular_locus_inclusion() is general.regular_locus_inclusion()
    assert operated.local_models() is None
    assert int(operated.regular_affine_manifold().dimension()) == 1
    inner = region(line((3,)))
    assert tuple(operated.regular_affine_manifold().affine_atlas().affine_chart(source_collar)(inner)) == (
        RR(3),
    )
