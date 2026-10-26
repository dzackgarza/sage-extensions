r"""Weil divisors expose prime generators, multiplicities, and local Cartier behavior."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_singularity_prime_divisor_local_data() -> None:
    polynomial = QQ.polynomial_ring("x,y,z")
    x = polynomial.algebra_generator("x")
    y = polynomial.algebra_generator("y")
    z = polynomial.algebra_generator("z")
    ring = polynomial.quotient_ring(polynomial.ideal(x * y - z**2))
    x, y, z = ring(x), ring(y), ring(z)
    scheme = ring.affine_spectrum(base_ring=QQ)
    prime = ring.spectrum()(ring.ideal(x, z))
    vertex = ring.spectrum()(ring.ideal(x, y, z))
    outside_prime = ring.spectrum()(ring.ideal(y, z))
    divisors = scheme.full_weil_divisor_group()
    prime_divisor = divisors.prime_divisor(prime)
    divisor_of_x = divisors.principal_divisor(x)

    assert divisors.multiplicity(divisor_of_x, prime) == 2
    assert divisor_of_x == 2 * prime_divisor
    assert not divisors.prime_is_cartier_at(prime, vertex)
    assert divisors.prime_is_cartier_at(prime, prime)
    assert divisors.prime_is_cartier_at(prime, outside_prime)
