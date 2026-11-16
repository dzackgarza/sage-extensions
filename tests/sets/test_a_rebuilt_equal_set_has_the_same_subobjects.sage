r"""A set's subobject category is a question about the set, not about a copy of it.

Two sets built separately from the same points are one set: they are equal, and
``P(X)`` of either is one parent, whose points are the subsets of that one set.
``Sets().Subobjects(X)`` is the category of exactly those points, so a subset of
``X`` lies in it whichever equal copy of ``X`` asks --- the subobject is
membership in the set, not in the object that happens to hold its power set.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_rebuilt_equal_set_carries_the_subobjects_of_its_power_set() -> None:
    r"""A subset of ``{a, b}`` is a subobject of every equal copy of it."""
    points = FiniteOrderedSets()(("a", "b"))
    rebuilt = FiniteOrderedSets()(("a", "b"))
    subset = points.power_set().from_predicate(lambda point: point == "a")

    assert points == rebuilt and points is not rebuilt
    assert points.power_set() is rebuilt.power_set()
    assert subset in points.power_set()
    assert subset.inclusion().codomain() == rebuilt
    assert subset in Sets().Subobjects(points)
    assert subset in Sets().Subobjects(rebuilt)
