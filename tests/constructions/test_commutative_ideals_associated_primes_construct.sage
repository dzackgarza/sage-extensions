r"""The associated primes of the zero ideal on the coordinate axes are the two axes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_zero_ideal_on_coordinate_axes_has_two_associated_primes() -> None:
    polynomials = QQ["x,y"]
    x = polynomials.algebra_generator("x")
    y = polynomials.algebra_generator("y")
    ring = polynomials.quotient_by_relations((x * y,))
    x_bar = ring.algebra_generator("x")
    y_bar = ring.algebra_generator("y")
    primes = ring.ideal(ring.zero()).associated_primes()

    assert ring.ideal(x_bar) in primes
    assert ring.ideal(y_bar) in primes
