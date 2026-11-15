r"""The points of a finite ordinal are values, and its point is the natural number.

An ordinal is fixed by its points, and a natural number is its value: two
constructions of one value are the one object.  That is what an enumeration of
the ordinal relies on -- the index set of a span basis is an ordinal, and the
plane row asks for one span basis, and so for one ordinal, per plane it
transports -- so an enumeration builds each of its points once and not again on
every pass.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_natural_number_is_one_object() -> None:
    r"""Two constructions of the same value are the one natural number."""
    assert NN(3) is NN(3)


def test_the_point_of_a_finite_ordinal_is_the_natural_number_at_it() -> None:
    r"""A position of an ordinal names one natural number, and the same one every time."""
    ordinal = Sets.Δ[3]

    assert ordinal(1) is ordinal(1)
    assert ordinal(1) is NN(1)
    assert int(ordinal(2)) == 2
