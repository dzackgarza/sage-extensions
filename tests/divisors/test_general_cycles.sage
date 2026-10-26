r"""Fundamental cycles of nonreduced subschemes of the affine plane."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_double_line_has_fundamental_cycle_twice_the_line() -> None:
    r"""``[V(x^2)] = 2 [V(x)]`` in ``A^2``: ``Q[x, y]_{(x)} / (x^2)`` has length 2.

    Fulton, *Intersection Theory*, 1.5.
    """
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    double_line = plane.closed_subscheme(x**2)
    line = plane.closed_subscheme(x)
    support = plane.underlying_space()(ring.ideal(x))

    assert double_line.fundamental_cycle() == 2 * line.fundamental_cycle()
    assert support.generic_local_length(double_line.defining_ideal_owned()) == 2
    assert double_line.fundamental_cycle().cycle_dimension() == 1


def test_embedded_lower_dimensional_associated_prime_is_not_a_generic_component() -> None:
    r"""``[V(x^2, xy)] = [V(x)]``: the embedded origin is not a minimal prime.

    ``(x^2, xy) = (x) cap (x^2, y)``; localizing at ``(x)`` inverts ``y`` and
    leaves ``(x)``, of length 1.
    """
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    thickened = plane.closed_subscheme((x**2, x * y))
    line = plane.closed_subscheme(x)
    origin = plane.underlying_space()(ring.ideal(x, y))

    assert thickened.fundamental_cycle() == line.fundamental_cycle()
    assert origin in thickened.associated_primes()
    assert thickened.associated_primes().cardinality() == 2
