r"""Height of a prime, and the order of vanishing at a prime of height one.

The height of ``p`` is the codimension of the closed set it defines, so in the
plane the origin has height two while the line ``x = 0`` has height one.  At a
prime of height one the local ring is a discrete valuation ring, and the order
of vanishing of a function there is the multiplicity of the uniformizer in it:
``x^3(x-1)`` vanishes to order three along ``x = 0`` and not at all along
``x = 1``, and ``50`` vanishes to order two at the prime ``5`` of the integers.

These are the numbers a Weil divisor is written with, which is why they are
asked of the point rather than of the ring.
"""

from sage_extensions.all import *


def test_a_nonzero_prime_of_the_integers_has_height_one() -> None:
    spectrum = ZZ.spectrum()

    assert spectrum(ZZ.ideal(ZZ(5))).height() == 1
    assert spectrum(ZZ.ideal(ZZ.zero())).height() == 0


def test_the_origin_of_the_plane_has_height_two_and_a_line_has_height_one() -> None:
    plane = QQ.polynomial_ring("x,y")
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    spectrum = plane.spectrum()

    assert spectrum(plane.ideal(x, y)).height() == 2
    assert spectrum(plane.ideal(x)).height() == 1


def test_the_order_of_vanishing_counts_the_uniformizer() -> None:
    line = QQ.polynomial_ring("x")
    x = line.algebra_generator("x")
    origin = line.spectrum()(line.ideal(x))
    function = x**3 * (x - line.one())

    assert origin.order_of_vanishing(function) == 3


def test_a_function_that_is_a_unit_at_the_point_vanishes_to_order_zero() -> None:
    line = QQ.polynomial_ring("x")
    x = line.algebra_generator("x")
    origin = line.spectrum()(line.ideal(x))

    assert origin.order_of_vanishing(x - line.one()) == 0


def test_the_order_of_vanishing_at_a_prime_of_the_integers() -> None:
    five = ZZ.spectrum()(ZZ.ideal(ZZ(5)))

    assert five.order_of_vanishing(ZZ(50)) == 2
    assert five.order_of_vanishing(ZZ(3)) == 0
