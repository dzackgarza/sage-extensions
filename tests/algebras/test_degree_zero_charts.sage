r"""Standard charts of a projective spectrum, read as degree-zero parts.

Localizing a graded ring at homogeneous elements grades the result over the
integers by ``deg(a/s) = deg(a) - deg(s)``, and the degree-zero part of ``S_f``
is the coordinate ring of the standard open ``D_+(f)`` of ``Proj S``.  For the
polynomial ring on three variables these are the three affine planes covering
the projective plane, and the restriction between two localizations cuts down
to the overlap map between their charts.
"""

from sage_extensions.all import *


def _projective_plane_coordinates():
    ring = QQ.polynomial_ring("x,y,z")
    return (
        ring,
        ring.algebra_generator("x"),
        ring.algebra_generator("y"),
        ring.algebra_generator("z"),
    )


def test_the_chart_holds_exactly_the_degree_zero_fractions() -> None:
    ring, x, y, z = _projective_plane_coordinates()
    away_from_x = ring.localization(x)
    chart = CommutativeGradedIntegralDomains(QQ)(ring).degree_zero_chart(away_from_x)

    assert away_from_x.fraction(y, x) in chart
    assert away_from_x.fraction(y * z, x * x) in chart
    assert away_from_x.fraction(y) not in chart
    assert away_from_x.fraction(ring.one(), x) not in chart


def test_an_inhomogeneous_numerator_is_not_a_chart_function() -> None:
    ring, x, y, z = _projective_plane_coordinates()
    away_from_x = ring.localization(x)
    chart = CommutativeGradedIntegralDomains(QQ)(ring).degree_zero_chart(away_from_x)

    assert away_from_x.fraction(x + y * z, x) not in chart


def test_the_overlap_map_carries_a_chart_function_to_the_same_fraction() -> None:
    ring, x, y, z = _projective_plane_coordinates()
    away_from_x = ring.localization(x)
    overlap = ring.localization(x, y)

    specialized = CommutativeGradedIntegralDomains(QQ)(ring)
    restriction = specialized.degree_zero_chart_restriction(away_from_x, overlap)

    assert restriction.domain() is specialized.degree_zero_chart(away_from_x)
    assert restriction.codomain() is specialized.degree_zero_chart(overlap)
    assert restriction(away_from_x.fraction(y, x)) == overlap.fraction(y, x)
    assert overlap.fraction(x, y) in specialized.degree_zero_chart(overlap)
