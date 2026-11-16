r"""The empty subset of a set is a subset of it, with the set's inclusion and no points.

A subset of ``X`` is cut out of ``X``: it carries ``X``'s inclusion, and it admits the
points of ``X`` its predicate selects.  The empty one selects nothing, and the construction
states that, so its emptiness and its cardinality are decided by the construction rather
than by a search of ``X`` -- which for an infinite ``X`` need not finish and would find
nothing to report.  ``SET-05``: the empty subset is a set construction of the owner, and
every set has one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_empty_subset_of_an_infinite_set_admits_nothing() -> None:
    r"""``NN``'s empty subset has ``NN``'s inclusion, no points, and cardinality zero."""
    empty = NN.empty_subset()

    assert empty.universe() == NN
    assert empty.inclusion().codomain() == NN
    assert empty.is_empty() is True
    assert empty.is_parent_of(NN(0)) is False
    assert empty.cardinality() == cardinal(0)


def test_the_empty_subset_of_a_finite_set_admits_nothing() -> None:
    r"""A finite ``{"a", "b"}``'s empty subset is empty too, and counts zero."""
    points = FiniteOrderedSets()(("a", "b"))
    empty = points.empty_subset()

    assert empty.universe() == points
    assert empty.inclusion().codomain() == points
    assert empty.is_empty() is True
    assert empty.is_parent_of("a") is False
    assert empty.is_parent_of("b") is False
    assert empty.cardinality() == cardinal(0)
