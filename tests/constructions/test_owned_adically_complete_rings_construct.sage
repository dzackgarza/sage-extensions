r"""Chosen adic completeness remembers the ideal of definition."""

from sage_extensions.all import *  # noqa: F401,F403


def test_three_adic_integers_remember_the_three_adic_ideal() -> None:
    integers = Zp(3)
    ideal = integers.ideal(integers(3))

    assert integers.is_adically_complete()
    assert integers.ideal_of_definition() == ideal
    assert integers.residue_field().cardinality() == cardinal(3)

