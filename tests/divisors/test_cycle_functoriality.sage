r"""Proper closed pushforward and flat open pullback of affine cycles."""

from sage_extensions.all import *


def test_closed_immersion_pushes_prime_cycle_to_same_support_with_same_multiplicity() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    axis = plane.closed_subscheme(x)
    axis_ring = axis.coordinate_algebra()
    generic = axis.underlying_space()(axis_ring.ideal(axis_ring.zero()))
    source = axis.cycle_group(1)
    cycle = ZZ(3) * source.prime_cycle(generic)

    pushed = axis.proper_pushforward_cycle(cycle)
    ambient_generic = plane.underlying_space()(ring.ideal(x))

    assert pushed.parent().cycle_scheme() is plane
    assert pushed.parent().cycle_dimension() == 1
    pushed_coordinates = pushed.to_vector()
    assert pushed_coordinates.support().domain().cardinality() == 1
    assert pushed_coordinates(ambient_generic) == ZZ(3)


def test_distinguished_open_flat_pullback_drops_disjoint_component_and_preserves_the_other() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    cycle_group = plane.cycle_group(1)
    x_axis = plane.underlying_space()(ring.ideal(y))
    y_axis = plane.underlying_space()(ring.ideal(x))
    cycle = ZZ(2) * cycle_group.prime_cycle(x_axis) + ZZ(5) * cycle_group.prime_cycle(y_axis)
    away_from_y_axis = plane.distinguished_open(x)

    pulled = DistinguishedOpenImmersions(plane)(away_from_y_axis).flat_pullback_cycle(cycle)
    away_ring = away_from_y_axis.coordinate_algebra()
    x_axis_away = away_from_y_axis.underlying_space()(away_ring.ideal(away_ring(y)))

    assert pulled.parent().cycle_scheme() is away_from_y_axis
    assert pulled.parent().cycle_dimension() == 1
    pulled_coordinates = pulled.to_vector()
    assert pulled_coordinates.support().domain().cardinality() == 1
    assert pulled_coordinates(x_axis_away) == ZZ(2)
