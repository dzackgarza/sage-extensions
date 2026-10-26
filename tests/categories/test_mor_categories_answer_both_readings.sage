r"""An object that is also a category answers the Mor packet in two readings.

Owner ruling 2026-10-16 (``ARC-07``): asked of a Mor category as an object,
``Mor``, ``End``, ``Aut`` and ``identity`` are those of its nearest ambient
category; asked of it as a category, they take its objects (arrows) as
arguments and are 2-arrows.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _singleton_end():
    point = Sets.Δ[0]
    end = Sets().End(point)
    arrow = end.identity()
    return end, arrow, end(arrow)


def test_the_two_arrows_of_the_unique_endomorphism_of_a_point() -> None:
    r"""``End(*)`` has one object, ``id_*``; its 2-arrow set at that object is
    the one-object discrete Mor, whose identity is ``End(*).identity(id_*)``."""
    end, arrow, arrow_object = _singleton_end()
    two_arrows = end.Mor(arrow, arrow)

    assert two_arrows is end.two_mor(arrow, arrow)
    assert two_arrows is end.Mor(arrow_object, arrow_object)
    assert two_arrows.cardinality() == cardinal(1)
    assert two_arrows.identity() == end.identity(arrow)
    assert end.identity(arrow) == end.identity_2(arrow)
    assert end.End(arrow).identity() == end.identity(arrow)
    assert end.Aut(arrow).one() == end.identity(arrow)
    assert end.identity(arrow) == end.Aut(arrow).one()


def test_the_object_readings_of_the_endomorphism_monoid_of_a_point() -> None:
    r"""With no argument, ``End(*).identity()`` is the identity map of ``*``,
    the unit of the monoid ``End(*)``; it is not a 2-arrow."""
    end, arrow, _arrow_object = _singleton_end()

    assert end.identity() is arrow
    assert end.one() == arrow
    assert arrow(Sets.Δ[0](0)) == Sets.Δ[0](0)


def test_the_orthogonal_group_of_a2_asks_the_group_readings() -> None:
    r"""``O(A2)`` is a group of order 12: ``O(A2).Mor(O(A2))`` is the group
    homomorphisms, containing the identity homomorphism, and ``O(A2).identity()``
    is the group identity, the identity isometry."""
    group = Lattices(ZZ)("A2").O()
    homomorphisms = group.Mor(group)
    unit = group.identity()

    assert homomorphisms.identity() in homomorphisms
    assert homomorphisms.identity()(unit) == unit
    assert unit == group.one()
    assert unit * unit == unit
