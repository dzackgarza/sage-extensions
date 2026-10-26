r"""Ideals of a prime local ring are ideals like any other.

An ideal of ``R_p`` is the extension of an ideal of ``R``, so it is a submodule
of the regular module of ``R_p`` and carries the ideal operations.  Two things
follow that a generating set alone does not give.  A generator whose numerator
lies outside ``p`` is a unit, so the ideal it generates is everything, and the
maximal ideal is distinguished from every other ideal by containment rather
than by the name it was built under.
"""

from sage_extensions.all import *


def test_a_unit_generates_the_whole_prime_local_ring() -> None:
    local = ZZ.localize_at_prime(2)

    assert local(3).is_unit()
    assert local.ideal(local(3)).contains_ambient_element(local.one())
    assert local.ideal(local(3)) == local.ideal(local.one())
    assert local.ideal(local(3)) != local.maximal_ideal()


def test_the_maximal_ideal_is_the_non_units() -> None:
    local = ZZ.localize_at_prime(2)

    assert local.maximal_ideal() == local.ideal(local(2))
    assert local.maximal_ideal().contains_ambient_element(local(2))
    assert local.maximal_ideal().contains_ambient_element(local(4))
    assert not local.maximal_ideal().contains_ambient_element(local.one())
    assert not local.maximal_ideal().contains_ambient_element(local(3))


def test_a_prime_local_principal_quotient_has_residue_size_to_valuation() -> None:
    local = ZZ.localize_at_prime(2)
    quotient = local.quotient_ring(local.ideal(local(8)))

    assert quotient.cardinality() == 8
def test_localization_of_a_polynomial_pid_remains_a_pid() -> None:
    polynomial = QQ.polynomial_ring("x")
    x = polynomial.algebra_generator("x")
    local = polynomial.localize_at_prime(polynomial.ideal(x))

    assert polynomial in PrincipalIdealDomains()
    assert local in PrincipalIdealDomains()
    assert local.cardinality() == aleph0
    assert not local(x).is_unit()
    assert local(6).is_unit()
