r"""Closed embeddings expose ideals, complements, fundamental cycles, pushforwards, and local intersections."""

from sage_extensions.all import *  # noqa: F401,F403


def test_double_line_retains_defining_ideal_and_fundamental_cycle() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    double_line = plane.closed_subscheme(x**2)
    line = plane.closed_subscheme(x)

    assert double_line.defining_ideal_owned() == ring.ideal(x**2)
    assert double_line.fundamental_cycle() == 2 * line.fundamental_cycle()
    assert double_line.open_complement().inclusion().codomain() is plane


def test_closed_immersion_pushes_prime_cycle_with_same_multiplicity() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    axis = plane.closed_subscheme(x)
    axis_ring = axis.coordinate_algebra()
    generic = axis.underlying_space()(axis_ring.ideal(axis_ring.zero()))
    cycle = ZZ(3) * axis.cycle_group(1).prime_cycle(generic)
    pushed = axis.proper_pushforward_cycle(cycle)
    ambient_generic = plane.underlying_space()(ring.ideal(x))

    assert pushed.to_vector()(ambient_generic) == ZZ(3)


def test_tangent_parabola_intersection_has_multiplicity_two() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    tangent = plane.closed_subscheme(y)
    parabola = plane.closed_subscheme(y - x**2)
    point = plane.underlying_space()(ring.ideal(x, y))
    intersection = tangent.serre_intersection(parabola, point)

    assert intersection.multiplicity() == ZZ(2)
    assert tangent.serre_intersection_multiplicity(parabola, point) == ZZ(2)
    assert tangent.intersection_multiplicity(parabola, point) == ZZ(2)
