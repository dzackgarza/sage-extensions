r"""The power set of a three-element set has eight subsets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_power_set_of_three_points() -> None:
    three = Set((1, 2, 3))
    power = three.power_set()

    assert power in PowerSets()
    assert power.base_set() is three
    assert power.cardinality() == cardinal(8)
    assert power.top().cardinality() == cardinal(3)
    assert power.bottom().cardinality() == cardinal(0)
