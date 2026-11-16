r"""The points of a finite orbit are the block of the partition the action retains.

A finite ``G``-set decides its orbits once, from the orbits of its chosen group
generators, and two points of ``X`` lie in one orbit exactly when they carry the
same label of that partition.  The points of one orbit are therefore a *block of
a partition the action already holds*: reading them is reading that partition.

They are not a scan of ``X`` that decides the two-point relation at each point,
which re-derives the partition the construction already retains.

The classes are pinned from the multiplication law alone: the class of ``x`` is
every conjugate ``g x g^{-1}``.  The classes of ``S(n)`` are the cycle types of
their representatives, one class per partition of $n$, so ``S(5)`` has classes of
sizes $1, 10, 15, 20, 20, 24, 30$ and ``S(6)`` of sizes
$1, 15, 15, 40, 40, 45, 90, 90, 120, 120, 144$, summing to $n!$.

The last test replaces the ``G``-set's own two-point decision with one that
refuses to answer: an enumeration that asks it cannot answer, and one that reads
the retained partition still can.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.group.g_sets import FiniteGSets


def _class_from_the_multiplication_law(group, representative):
    r"""The conjugacy class of ``representative``: every ``g x g^{-1}`` in ``G``."""
    return frozenset(g * representative * g.inverse() for g in group)


def test_the_conjugacy_classes_of_s5_are_the_cycle_types_of_five() -> None:
    r"""Five points have seven cycle types, and their sizes sum to $5! = 120$."""
    group = Groups.S(5)
    class_set = group.conjugacy_classes()
    classes = tuple(class_set)
    blocks = tuple(frozenset(orbit.points()) for orbit in classes)

    assert class_set.cardinality() == cardinal(7)
    assert sorted(int(orbit.cardinality().finite_value()) for orbit in classes) == [
        1, 10, 15, 20, 20, 24, 30,
    ]
    assert sum(int(orbit.cardinality().finite_value()) for orbit in classes) == int(group.order())
    assert blocks == tuple(
        _class_from_the_multiplication_law(group, orbit.representative())
        for orbit in classes
    )
    assert frozenset().union(*blocks) == frozenset(group)


def test_the_conjugacy_classes_of_s6_are_the_cycle_types_of_six() -> None:
    r"""Six points have eleven cycle types, and their sizes sum to $6! = 720$."""
    group = Groups.S(6)
    class_set = group.conjugacy_classes()
    classes = tuple(class_set)
    blocks = tuple(frozenset(orbit.points()) for orbit in classes)

    assert class_set.cardinality() == cardinal(11)
    assert sorted(int(orbit.cardinality().finite_value()) for orbit in classes) == [
        1, 15, 15, 40, 40, 45, 90, 90, 120, 120, 144,
    ]
    assert sum(int(orbit.cardinality().finite_value()) for orbit in classes) == int(group.order())
    assert blocks == tuple(
        _class_from_the_multiplication_law(group, orbit.representative())
        for orbit in classes
    )
    assert frozenset().union(*blocks) == frozenset(group)


def test_an_orbits_points_are_read_without_deciding_the_relation_at_each_point() -> None:
    r"""The block of the retained partition is read; the per-point decision is not asked.

    The two-point decision is the method the ``G``-set's parent class carries,
    and it is replaced here by one that refuses to answer.  The labels of the
    partition come from the orbits of the chosen group generators, so the points
    of each class and its cardinality are still read.  An enumeration that
    decided the relation at each point of ``X`` would have nothing to answer
    with, which is exactly what the partition replaces.
    """
    group = Groups.S(4)
    classes = tuple(group.conjugacy_classes())
    representatives = tuple(orbit.representative() for orbit in classes)
    g_set_class = FiniteGSets(group.conjugation_g_set().acting_group()).parent_class
    original = g_set_class._orbit_relation_decision

    def refused(self, source, target):
        raise AssertionError("the two-point orbit relation was decided at a point of X")

    g_set_class._orbit_relation_decision = refused
    try:
        blocks = tuple(frozenset(orbit.points()) for orbit in classes)
        sizes = tuple(int(orbit.cardinality().finite_value()) for orbit in classes)
    finally:
        g_set_class._orbit_relation_decision = original

    assert sorted(sizes) == [1, 3, 6, 6, 8]
    assert sum(sizes) == int(group.order())
    assert blocks == tuple(
        _class_from_the_multiplication_law(group, representative)
        for representative in representatives
    )
    assert frozenset().union(*blocks) == frozenset(group)
