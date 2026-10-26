r"""The toric variety as the scheme glued from the charts of its maximal cones.

Values are Cox--Little--Schenck, *Toric Varieties*: the atlas and its gluing
are Thm. 3.1.5, the face localization presenting an overlap is Prop. 1.3.16,
and the identification of the intersection of all the charts with the dense
torus is the orbit-cone correspondence, Thm. 3.2.6.

Unverified: written by eye against the construction, not run.
"""

from sage_extensions.all import *


# One lattice per rank for the whole file: a free module is a fresh object on
# every construction, so building it twice would give two unrelated categories
# of fans.
_PLANE_FANS = RationalPolyhedralFans(ZZ.free_module(2))
_LINE_FANS = RationalPolyhedralFans(ZZ.free_module(1))


def _projective_plane():
    fan = _PLANE_FANS.projective_space_fan()
    return fan, fan.toric_variety(QQ)


def _projective_line():
    fan = _LINE_FANS.projective_space_fan()
    return fan, fan.toric_variety(QQ)






def test_the_toric_transitions_agree_on_a_triple_overlap() -> None:
    r"""The cocycle condition on the three charts of ``P^2``: going from the
    first chart to the second and on to the third is the same map as going
    from the first to the third.  The triple overlap is the intersection of all
    three charts, which for a complete fan is the dense torus (CLS Thm. 3.2.6),
    so every coordinate of a chart is invertible there."""
    fan, plane = _projective_plane()
    first, second, third = tuple(fan.maximal_cones())

    left_middle = plane.transition_on_triple(first, second, third)
    middle_right = plane.transition_on_triple(second, third, first)
    left_right = plane.transition_on_triple(first, third, second)

    assert middle_right * left_middle == left_right
    assert left_middle.domain() is plane.triple_overlap(first, second, third)

    chart_algebra = plane.chart(first).coordinate_algebra()
    triple_algebra = plane.triple_overlap(first, second, third).coordinate_algebra()
    into_triple = triple_algebra.localization_map()
    for label in chart_algebra.algebra_generating_set():
        assert into_triple(chart_algebra.algebra_generator(label)).is_unit()


def test_the_two_charts_of_the_projective_line_glue_by_inverting_the_character() -> None:
    r"""CLS Prop. 1.3.16 on the smallest complete fan.  ``P^1`` has the two
    cones ``<e>`` and ``<-e>``, whose semigroup algebras are one-generator
    algebras on the characters ``chi^m`` and ``chi^{-m}``.  The two cones meet
    in the origin, so the transition carries the target chart's character to
    the inverse of the source chart's: their product is ``chi^0``.  A
    transition that dropped or inverted the power of the localized character
    would fail this."""
    fan, line = _projective_line()
    source_cone, target_cone = tuple(fan.maximal_cones())

    source_algebra = line.chart(source_cone).coordinate_algebra()
    target_algebra = line.chart(target_cone).coordinate_algebra()
    assert source_algebra.algebra_generating_set().cardinality() == 1
    assert target_algebra.algebra_generating_set().cardinality() == 1
    assert source_cone.intersection(target_cone).dimension() == 0

    forward = line.transition_between(source_cone, target_cone).forward()
    source_overlap_algebra = forward.domain().coordinate_algebra()
    target_overlap_algebra = forward.codomain().coordinate_algebra()

    source_character = source_algebra.algebra_generator(
        next(iter(source_algebra.algebra_generating_set()))
    )
    target_character = target_algebra.algebra_generator(
        next(iter(target_algebra.algebra_generating_set()))
    )
    pulled_back = forward.coordinate_algebra_morphism()(
        target_overlap_algebra.localization_map()(target_character)
    )

    assert (
        pulled_back * source_overlap_algebra.localization_map()(source_character)
        == source_overlap_algebra.one()
    )
