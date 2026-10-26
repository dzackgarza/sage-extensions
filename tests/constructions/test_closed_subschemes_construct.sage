r"""Closed subschemes retain their ambient schemes and defining immersions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_closed_subschemes_of_the_affine_plane(commutative_ring) -> None:
    ring = commutative_ring
    plane = AffineSpaces(ring)(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")
    y = plane.coordinate_ring().algebra_generator("y")
    cusp = plane.closed_subscheme(y**2 - x**3)
    origin = plane.closed_subscheme(x, y)

    assert cusp in ClosedSubschemes(ring)
    assert cusp in Schemes(ring)
    assert cusp.ambient_scheme() is plane
    assert cusp.codimension() == 1
    assert cusp.relative_dimension() == 1
    assert cusp.inclusion().codomain() is plane
    assert cusp not in SmoothSchemes(ring)
    assert origin.codimension() == 2
    assert origin.relative_dimension() == 0
    assert origin.coordinate_ring().Mor(ring).cardinality() == cardinal(1)


def test_closed_subscheme_over_a_field_is_a_curve(field) -> None:
    plane = AffineSpaces(field)(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")
    y = plane.coordinate_ring().algebra_generator("y")
    parabola = plane.closed_subscheme(y - x**2)

    assert parabola in Curves(field)
    assert parabola in SmoothSchemes(field)
    assert parabola in IntegralSchemes(field)
    assert parabola.dimension() == 1
