r"""The empty subset of a set is the least point of its power set.

A subset of ``X`` is a subobject of ``X`` -- it carries ``X``'s inclusion -- and the
subsets of ``X`` are the points of ``P(X)``.  The empty one is the least of those points:
``P(X).bottom()``, ``P(X)``'s own "empty subset, the least point of P(X)".  ``SET-05``:
one construction, so an empty subset of ``X`` is that point and not a second object beside
it.

The construction supplies no point, so emptiness and cardinality zero are decided from it
-- it enumerates nothing -- and not by a search of ``X``.  That is what makes the empty
subset answerable when ``X`` is infinite, as ``NN`` is.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_empty_subset_of_an_infinite_set_is_the_least_point_of_its_power_set() -> None:
    r"""``NN``'s empty subset is ``P(NN)``'s bottom, with ``NN``'s inclusion and no points."""
    power = NN.power_set()
    empty = power.bottom()

    assert power.is_parent_of(empty) is True
    assert empty.inclusion().codomain() == NN
    assert empty.is_empty() is True
    assert empty.is_parent_of(NN(0)) is False
    assert empty.cardinality() == cardinal(0)
    assert tuple(empty) == ()


def test_the_empty_subset_of_a_finite_set_is_the_least_point_of_its_power_set() -> None:
    r"""A finite ``{"a", "b"}``'s empty subset is its power set's bottom, and counts zero."""
    points = FiniteOrderedSets()(("a", "b"))
    power = points.power_set()
    empty = power.bottom()

    assert power.is_parent_of(empty) is True
    assert empty.inclusion().codomain() == points
    assert empty.is_empty() is True
    assert empty.is_parent_of("a") is False
    assert empty.is_parent_of("b") is False
    assert empty.cardinality() == cardinal(0)
    assert tuple(empty) == ()
