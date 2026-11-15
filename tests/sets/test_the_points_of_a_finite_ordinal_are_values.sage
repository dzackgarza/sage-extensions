r"""The points of a finite ordinal are values, and its point is the natural number.

An ordinal is fixed by its points, and a natural number is its value: two
constructions of one value are the one object while something references it, and
the set holds its points weakly -- so a natural that nothing references is not
kept, and a reader that builds many of them keeps no entry per value it has
finished with.  That is what an enumeration of the ordinal relies on -- the index
set of a span basis is an ordinal, and the plane row asks for one span basis, and
so for one ordinal, per plane it transports -- so an enumeration builds each of
its points once and not again on every pass.  Pickle and the two copy protocols
come back through the set applied to the value, so a natural read back is that
one point again.
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


def test_a_natural_number_is_held_only_while_something_references_it() -> None:
    r"""A natural has its reader's references and no others: a set keeps none of its points alive."""
    control = []
    holder = (control,)
    point = NN(70001)
    held = (point,)

    assert sys.getrefcount(point) == sys.getrefcount(control)
    assert held[0] is NN(70001)


def test_a_released_natural_number_leaves_no_entry_behind() -> None:
    r"""Released, a natural is not retained: asking for its value again builds it again."""
    control = []
    holder = (control,)
    point = NN(70002)
    value = int(point)
    del point

    rebuilt = NN(value)
    held = (rebuilt,)

    assert sys.getrefcount(rebuilt) == sys.getrefcount(control)
    assert rebuilt == value


def test_a_natural_number_read_back_is_the_one_point() -> None:
    r"""Pickled or copied, a natural names its value, so it comes back as this point."""
    point = NN(70003)

    assert loads(dumps(point)) is point
    assert copy(point) is point
    assert deepcopy(point) is point
