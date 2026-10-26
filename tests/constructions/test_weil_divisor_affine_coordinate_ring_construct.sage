r"""An affine full Weil divisor group retains the coordinate algebra of its scheme."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_a1_surface_weil_divisor_group_retains_coordinate_algebra() -> None:
    polynomial = QQ.polynomial_ring("x,y,z")
    x = polynomial.algebra_generator("x")
    y = polynomial.algebra_generator("y")
    z = polynomial.algebra_generator("z")
    ring = polynomial.quotient_ring(polynomial.ideal(x * y - z**2))
    scheme = ring.affine_spectrum(base_ring=QQ)
    divisors = scheme.full_weil_divisor_group()

    assert divisors.affine_divisor_coordinate_ring() is ring
