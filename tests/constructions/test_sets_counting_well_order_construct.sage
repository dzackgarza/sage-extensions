r"""A finite or countably infinite set exposes its standard counting well-order."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_set_counting_well_order_has_the_same_cardinality() -> None:
    three = Set((1, 2, 3))

    assert three.counting_well_order().cardinality() == cardinal(3)


def test_naturals_counting_well_order_is_the_natural_numbers() -> None:
    assert NN.counting_well_order() is NN
