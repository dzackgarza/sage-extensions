r"""A surgery glues the replacement in along the region's boundary and retains the region's structure.

Cutting a region out of an integral-affine surface and sewing a replacement in along its
boundary does not change the surface as a smooth manifold: the base of a Symington
surgery is the surface it was cut from, with its integral-affine structure reglued and
the replacement's singular points added (Alexeev--Engel, *Compactifications of moduli
spaces of K3 surfaces with a nonsymplectic involution*, arXiv:2208.10383v2, Construction
6.16, pp. 31--32).

The specimen is the smallest surface that decides it: the real line with its one-chart
integral-affine structure, cut where the coordinate does not vanish.  The region is the
punctured line, the replacement is the line with the origin as its singular point, and
the two collars are the punctured line's own chart on the two sides of the seam.  The
result is the line, singular at the origin, integral-affine on the punctured line, with
the collar's chart among its charts.
"""

import pytest

from sage_extensions.all import *


def _the_punctured_line_with_its_affine_atlas():
    r"""The line, the open submanifold ``{x != 0}``, the affine model, and the line's atlas."""
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


def _the_surgery_specimen():
    r"""The line, its region, the replacement singular at the origin, and the two collars."""
    line, region, model, atlas = _the_punctured_line_with_its_affine_atlas()
    structure = IntegralAffineManifolds().on(line, atlas)
    singular = line.power_set()((line((0,)),))
    replacement = SingularIntegralAffineSpaces().on(
        line,
        singular.inclusion(),
        Sets().Mor(line, line).identity(),
        structure,
    )
    inclusion = line.open_submanifold_inclusion(region)
    collar_chart = Sets().Mor(region, model)(lambda point: model(tuple(point.coordinates())))
    source_collar = IntegralAffineCollars().on(structure, inclusion, inclusion, collar_chart)
    target_collar = IntegralAffineCollars().on(structure, inclusion, inclusion, collar_chart)
    return line, region, model, replacement, inclusion, source_collar, target_collar


def test_the_surgery_is_the_ambient_line_with_the_replacements_singular_point() -> None:
    r"""The result is the line, singular at the origin, integral-affine on the punctured line.

    The underlying space is the line the region was cut from, the singular locus is the
    replacement's, the regular locus is the region, and the regular integral-affine
    structure is the replacement's atlas restricted to the region.  Its charts include
    the two collars', each read in the line's affine model.
    """
    line, region, model, replacement, inclusion, source_collar, target_collar = (
        _the_surgery_specimen()
    )
    operated = SingularIntegralAffineSpaces().surgery(
        inclusion, replacement, Sets().Mor(region, region).identity(),
        (source_collar, target_collar),
    )
    inner = region(line((3,)))

    assert operated in SingularIntegralAffineSpaces()
    assert operated.underlying_topological_space() is line
    assert operated.singular_locus_inclusion() is replacement.singular_locus_inclusion()
    assert operated.singular_locus() is replacement.singular_locus()
    assert operated.regular_locus_inclusion() is inclusion
    assert operated.regular_locus()[0] is inclusion
    regular = operated.regular_affine_manifold()
    assert regular.underlying_smooth_manifold() is region
    assert regular.affine_atlas().affine_model() is model
    assert sorted(operated.regular_locus()[0].codomain().chart_labels()) == sorted(
        line.chart_labels()
    )
    assert tuple(regular.affine_atlas().affine_chart(source_collar)(inner)) == (RR(3),)
    assert tuple(regular.affine_atlas().affine_chart(target_collar)(inner)) == (RR(3),)


def test_a_boundary_isomorphism_of_another_pair_of_faces_is_refused() -> None:
    r"""The boundary isomorphism is required to join the two collars' faces.

    The collars' faces are both the punctured line here; the boundary isomorphism of a
    surgery is checked against them, so one that starts at the whole line is refused
    rather than read as the identity.
    """
    line, region, _model, replacement, inclusion, source_collar, target_collar = (
        _the_surgery_specimen()
    )
    whole_line = Sets().Mor(line, region)(lambda point: region(point))

    assert source_collar.face() is region
    assert target_collar.face() is region
    assert whole_line.domain() is line
    with pytest.raises(AssertionError):
        SingularIntegralAffineSpaces().surgery(
            inclusion, replacement, whole_line, (source_collar, target_collar)
        )
