r"""The points of a finite ordinal are values, and its point is the natural number.

An ordinal is fixed by its points, and a natural number is its value: two
constructions of one value are the one object while something references it, and
no longer -- the set holds each point weakly, so a natural lives exactly while it
is referenced.  A value read back through pickle or a copy is that one point.
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


def test_a_released_natural_number_is_not_retained() -> None:
    r"""Released, a natural is collected: nothing in the set holds it alive."""
    point = NN(70002)
    reference = weakref.ref(point)
    value = int(point)
    del point

    gc.collect()

    assert reference() is None
    assert NN(value) == value


def test_a_natural_number_read_back_is_the_one_point() -> None:
    r"""Pickled or copied, a natural names its value, so it comes back as this point."""
    point = NN(70003)

    assert loads(dumps(point)) is point
    assert copy(point) is point
    assert deepcopy(point) is point
