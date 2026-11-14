"""Localization value keys respect equivalent fractions and killed elements."""

from sage_extensions.all import *


def test_equal_integer_localization_fractions_retrieve_the_same_value():
    ring = ZZ.localization(ZZ(2))
    half = ring.fraction(ZZ(1), ZZ(2))
    reconstructed = ring.fraction(ZZ(2), ZZ(4))
    zero = ring.fraction(ZZ(0), ZZ(2))

    assert half == reconstructed
    assert zero == ring.zero()
    values = {half: "half", ring.zero(): "zero"}
    assert values[reconstructed] == "half"
    assert values[zero] == "zero"


def test_localization_keys_identify_elements_killed_by_an_inverted_zero_divisor():
    source = ZZ.ideal(ZZ(6)).quotient_ring()
    ring = source.localization(source(2))
    killed = ring(source(3))
    unit = ring(source(2))

    assert killed == ring.zero()
    assert unit != ring.zero()
    values = {ring.zero(): "zero", unit: "unit"}
    assert values[killed] == "zero"
    assert values[ring.fraction(source(4), source(2))] == "unit"


def test_rational_function_keys_identify_equal_fraction_presentations():
    source = QQ.polynomial_ring("t")
    t = source.algebra_generator("t")
    ring = source.fraction_field()
    fraction = ring.fraction(t**2, t)
    polynomial = ring(t)

    assert fraction == polynomial
    values = {polynomial: "t", ring.one(): "one"}
    assert values[fraction] == "t"
    assert values[ring.fraction(t, t)] == "one"
