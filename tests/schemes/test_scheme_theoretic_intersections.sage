r"""Scheme-theoretic intersections of closed subschemes, and the tangency they see.

``Z cap W = V(I + J)`` is the fibre product ``Z x_X W``, so it comes with a
factorization through each of the two subschemes.  Taking the ideal sum
rather than the intersection of the point sets is what distinguishes a
tangential meeting from a transverse one.
"""

from sage_extensions.all import *


def _plane():
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    algebra = plane.coordinate_ring()
    return plane, algebra, algebra.algebra_generator("x"), algebra.algebra_generator("y")


def test_two_transverse_lines_meet_in_the_reduced_origin() -> None:
    plane, algebra, x, y = _plane()
    horizontal = plane.closed_subscheme(y)
    vertical = plane.closed_subscheme(x)
    meeting = horizontal.intersection(vertical)

    assert meeting in ClosedEmbeddings(plane)
    assert meeting.defining_ideal_owned() == algebra.ideal(y, x)
    assert meeting.relative_dimension() == 0
    assert meeting.codimension() == 2
    assert meeting in IntegralSchemes(QQ)

    # The intersection factors through each of the two subschemes, and the
    # two factorizations compose back to its own inclusion.
    into_horizontal = horizontal.corestriction(meeting.inclusion())
    into_vertical = vertical.corestriction(meeting.inclusion())
    assert into_horizontal.codomain() is horizontal
    assert into_vertical.codomain() is vertical
    assert horizontal.inclusion() * into_horizontal == meeting.inclusion()
    assert vertical.inclusion() * into_vertical == meeting.inclusion()


def test_a_tangent_line_meets_the_parabola_in_a_non_reduced_double_point() -> None:
    plane, algebra, x, y = _plane()
    parabola = plane.closed_subscheme(y - x**2)
    tangent = plane.closed_subscheme(y)
    meeting = tangent.intersection(parabola)
    local_algebra = meeting.coordinate_algebra()
    local_x = local_algebra.algebra_generator("x")

    assert meeting.defining_ideal_owned() == algebra.ideal(y, y - x**2)
    assert meeting.relative_dimension() == 0
    # The tangency is visible only scheme-theoretically: x vanishes to order
    # two on the meeting, so its coordinate algebra is Q[x]/(x^2), which is
    # not reduced and therefore not integral.
    assert local_x != local_algebra.zero()
    assert local_x**2 == local_algebra.zero()
    assert meeting not in IntegralSchemes(QQ)

    # The same subscheme is the fibre product of the two inclusions over the plane.
    pullback = tangent.scheme_category().fiber_product(
        tangent.inclusion(),
        parabola.inclusion(),
    )
    pullback_x = pullback.coordinate_algebra().algebra_generator(("left", "x"))
    assert pullback_x**2 == pullback.coordinate_algebra().zero()
    assert pullback_x != pullback.coordinate_algebra().zero()


def test_tangent_intersection_has_local_multiplicity_two() -> None:
    plane, algebra, x, y = _plane()
    parabola = plane.closed_subscheme(y - x**2)
    tangent = plane.closed_subscheme(y)
    origin = plane.underlying_space()(algebra.ideal(x, y))

    assert tangent.intersection_multiplicity(parabola, origin) == 2


def test_transverse_intersection_has_local_multiplicity_one() -> None:
    plane, algebra, x, y = _plane()
    horizontal = plane.closed_subscheme(y)
    vertical = plane.closed_subscheme(x)
    origin = plane.underlying_space()(algebra.ideal(x, y))

    assert horizontal.intersection_multiplicity(vertical, origin) == 1
