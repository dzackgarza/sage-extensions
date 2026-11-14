r"""A finite literal set is read as a subset through its own elements.

``Set((1, 2))`` is the session's finite literal set: provably finite, with its
points presented, but carrying no owned ranking onto the standard well-order, so
it is not an object of ``EnumeratedSets()``.  Reading it as a subset of
``Set((1, 2, 3))`` therefore goes through its points — the same route a tuple of
members already took.  The constructor used to demand ``EnumeratedSets()`` and so
rejected the very points it accepts from a tuple, which is the research suite's
``power(Set((1, 2)))`` failure.
"""

from sage_extensions.all import EnumeratedSets, Set, Sets, cardinal


def _three():
    return Set((1, 2, 3))


def test_a_finite_literal_set_reads_as_a_subset_of_another() -> None:
    three = _three()
    two = Set((1, 2))
    power = three.power_set()
    element = power(two)

    assert element in power
    assert element.cardinality() == cardinal(2)
    assert element.complement().cardinality() == cardinal(1)
    assert element.union(element.complement()).cardinality() == cardinal(3)
    assert element.intersection(element.complement()).cardinality() == cardinal(0)


def test_the_full_set_and_the_empty_subset_are_unchanged() -> None:
    three = _three()
    power = three.power_set()

    assert power(three).cardinality() == cardinal(3)
    assert power.top().cardinality() == cardinal(3)
    assert power.bottom().cardinality() == cardinal(0)


def test_the_read_uses_the_points_not_an_owned_ranking() -> None:
    r"""The candidate is a set, is provably finite, and is not in ``EnumeratedSets()``.

    That combination is exactly what the constructor's assertion separated: the
    first two clauses hold and the third does not, so the read must go through
    the points rather than through a ranking that does not exist.
    """
    two = Set((1, 2))

    assert two in Sets()
    assert Sets().is_provably_finite(two)
    assert two not in EnumeratedSets()
