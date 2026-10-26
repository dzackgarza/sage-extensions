from sage_extensions.all import *


def three():
    return cardinal(3)


def test_the_cardinality_of_a_three_element_set_is_three() -> None:
    assert Sets.Δ[2].cardinality() == three()


def test_the_category_applied_to_the_number_agrees() -> None:
    assert Cardinalities()(3) == three()


def test_the_categories_of_three() -> None:
    assert three() in Cardinalities()


def test_three_is_a_finite_cardinal() -> None:
    assert three() == 3
    assert three().is_finite()
    assert three().is_countable()
    assert not three().is_infinite()
    assert three().finite_value() == 3
    assert Cardinalities().le(three(), aleph0)
    assert Cardinalities().lt(three(), aleph0)


def test_cardinal_arithmetic_with_three() -> None:
    r"""$3 + 4 = 7$, $3 \cdot 4 = 12$, $2^3 = 8$, $3 + \aleph_0 = \aleph_0$, $3^{\aleph_0} = 2^{\aleph_0}$."""
    assert three() + cardinal(4) == cardinal(7)
    assert three() * cardinal(4) == cardinal(12)
    assert cardinal(2) ^ three() == cardinal(8)
    assert three() + aleph0 == aleph0
    assert three() ^ aleph0 == continuum
