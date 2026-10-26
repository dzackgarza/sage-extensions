r"""Tor and Ext over the integers and over a polynomial ring, from free resolutions.

``Tor_1(Z/6, Z/4) = Z/2``, ``Ext^1(Z/6, Z) = Z/6``, and both vanish beyond
the length of the resolution; over ``QQ[x]`` the annihilators say which
cyclic module came out.
"""

from sage_extensions.all import *


def _cyclic(ring, generator):
    r"""The cyclic module ``R / (generator)`` presented by one relation on one generator."""
    line = ring.free_module(1)
    relations = ring.free_module(1)
    return relations.Mor(line)({0: ring(generator) * line.module_generator(0)}).cokernel()


def test_tor_over_the_integers_is_the_gcd_and_vanishes_above_the_resolution() -> None:
    six, four, integers = _cyclic(ZZ, 6), _cyclic(ZZ, 4), ZZ.regular_module()
    assert six.tor(four, degree=0).cardinality() == 2
    assert six.tor(four, degree=1).cardinality() == 2
    assert six.tor(four, degree=2).cardinality() == 1
    assert six.tor(integers, degree=0).cardinality() == 6
    assert six.tor(integers, degree=1).cardinality() == 1
    assert integers.tor(six, degree=1).cardinality() == 1


def test_ext_over_the_integers() -> None:
    six, four, integers = _cyclic(ZZ, 6), _cyclic(ZZ, 4), ZZ.regular_module()
    assert six.ext(integers, degree=0).cardinality() == 1
    assert six.ext(integers, degree=1).cardinality() == 6
    assert six.ext(four, degree=0).cardinality() == 2
    assert six.ext(four, degree=1).cardinality() == 2
    assert six.ext(four, degree=2).cardinality() == 1
    assert integers.ext(six, degree=0).cardinality() == 6
    assert integers.ext(six, degree=1).cardinality() == 1


def test_tor_and_ext_of_cyclic_modules_over_a_polynomial_ring() -> None:
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    square, line = _cyclic(ring, x**2), _cyclic(ring, x)
    assert tuple(square.tor(line, degree=1).invariant_factors()) == (x,)
    assert tuple(square.tor(line, degree=0).invariant_factors()) == (x,)
    assert tuple(square.ext(ring.regular_module(), degree=1).invariant_factors()) == (x**2,)
    assert square.ext(ring.regular_module(), degree=0).invariant_factors().cardinality() == 0
    assert square.ext(ring.regular_module(), degree=0).module_rank() == 0


def test_ext_one_into_the_integers_turns_the_quotient_z_mod_6_to_z_mod_3_into_an_injection() -> None:
    r"""``Ext^1(Z/n, Z) = Hom(Z/n, Q/Z)``, so ``Z/6 -> Z/3`` induces the injection ``Z/3 -> Z/6``.

    Source: Weibel, An Introduction to Homological Algebra, 3.3.2 and 3.6 (Pontryagin duality);
    the induced map is precomposition with the quotient.
    """
    six = _cyclic(ZZ, 6)
    three = _cyclic(ZZ, 3)
    quotient = six.Mor(three)({0: three.module_generator(0)})
    induced = quotient.ext_map(ZZ.regular_module(), degree=1)
    assert induced.domain().cardinality() == 3
    assert induced.codomain().cardinality() == 6
    assert induced.is_injective()
    assert not induced.is_surjective()
    assert induced.image().cardinality() == 3
