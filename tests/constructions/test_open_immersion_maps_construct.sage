r"""Open immersions recognize images, corestrict maps, and pull back cycles flatly."""

from sage_extensions.all import *  # noqa: F401,F403


def test_distinguished_open_recognizes_and_corestricts_a_map() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    plane = AffineSchemes(QQ)(ring)
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    line = AffineSchemes(QQ)(line_ring)
    open_set = plane.distinguished_open(x)
    vertical = line.Mor(plane)(
        ring.Mor(line_ring)({"x": line_ring.one(), "y": t})
    )

    assert open_set.contains_image_of(vertical)
    assert open_set.inclusion() * open_set.corestriction(vertical) == vertical


def test_distinguished_open_flat_pullback_preserves_the_meeting_cycle() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    cycles = plane.cycle_group(1)
    x_axis = plane.underlying_space()(ring.ideal(y))
    y_axis = plane.underlying_space()(ring.ideal(x))
    cycle = ZZ(2) * cycles.prime_cycle(x_axis) + ZZ(5) * cycles.prime_cycle(y_axis)
    open_set = plane.distinguished_open(x)
    pulled = DistinguishedOpenImmersions(plane)(open_set).flat_pullback_cycle(cycle)
    open_ring = open_set.coordinate_algebra()
    x_axis_open = open_set.underlying_space()(open_ring.ideal(open_ring(y)))

    assert pulled.parent().cycle_scheme() is open_set
    assert pulled.parent().cycle_dimension() == 1
    coordinates = pulled.to_vector()
    assert coordinates.support().domain().cardinality() == 1
    assert coordinates(x_axis_open) == ZZ(2)
