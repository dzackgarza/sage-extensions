r"""The orders a Coxeter diagram answers are objects of ``PartiallyOrderedSets()``.

A partial order is a finite set together with its order relation, and
``PartiallyOrderedSets()(X, le)`` is its owner: the object retains ``X`` and
``le`` and answers ``le``, ``cardinality``, iteration, ``maximum`` and
``minimum``.  A Coxeter diagram's induced subdiagrams, and the orbits of its
automorphism group on them, are two such orders, so the six queries that ask
for them answer objects of that category rather than a Sage ``Poset``.

An induced subdiagram is a slice over its diagram, so its vertex inclusion is
carried with it, and an orbit is the orbit: a point of an orbit set is named by
one of its points and holds every one of them.
"""

from sage_extensions.all import *  # noqa: F401,F403


def a2():
    return CoxeterDiagrams().from_cartan_type(["A", 2])


def d4():
    r"""The star \(D_4\): centre \(0\) joined by bonds \(3\) to the outer nodes \(1,2,3\)."""
    return CoxeterDiagrams()(
        [[1, 3, 3, 3], [3, 1, 2, 2], [3, 2, 1, 2], [3, 2, 2, 1]]
    )


def test_the_a2_subdiagram_poset_is_the_four_point_order_of_inclusion() -> None:
    r"""\(A_2\) has four induced subdiagrams: \(A_2\), two \(A_1\), and the empty one.

    The order is inclusion of vertex sets, so the diagram is above everything
    and the subdiagram on no vertices is below everything.  The two singletons
    are incomparable, which no total order would be.
    """
    diagram = a2()
    poset = diagram.subdiagram_poset()

    assert poset in PartiallyOrderedSets()
    assert poset.cardinality() == 4

    top = poset.maximum()
    bottom = poset.minimum()

    # The maximum is the diagram itself: the subdiagram on every vertex.
    assert top.arrow().domain() == diagram
    assert top.arrow().codomain() is diagram
    # The minimum is the subdiagram on no vertices.
    assert bottom.arrow().domain().cardinality() == 0
    assert poset.le(bottom, top)
    assert not poset.le(top, bottom)

    singletons = tuple(
        point for point in poset if point.arrow().domain().cardinality() == 1
    )
    assert all(poset.le(singleton, top) for singleton in singletons)
    assert not poset.le(singletons[0], singletons[1])
    assert not poset.le(singletons[1], singletons[0])

    # Each member carries its vertex inclusion, which is the identity on its
    # own vertices read in the diagram.
    assert all(
        point.arrow()(vertex) == vertex
        for point in poset
        for vertex in point.arrow().domain().index_set()
    )


def test_a_partial_order_retains_its_set_and_its_relation() -> None:
    r"""The four point chain \(0<1<2<3\): ``le``, cardinality, iteration, max and min.

    ``PartiallyOrderedSets()(X, le)`` is constructed from the set and the
    relation and answers both, so the five readings are of the data the caller
    supplied and not of a fresh enumeration.
    """
    points = Sets.Δ[3]
    poset = PartiallyOrderedSets()(points, lambda left, right: int(left) <= int(right))

    assert poset in PartiallyOrderedSets()
    assert poset.underlying_set() is points
    assert poset.cardinality() == points.cardinality()
    assert tuple(poset) == tuple(points)

    assert poset.le(points(1), points(2))
    assert not poset.le(points(2), points(1))
    assert poset.maximum() == points(3)
    assert poset.minimum() == points(0)


def test_the_six_subdiagram_orders_of_d4_are_owned_partial_orders() -> None:
    r"""\(D_4\): \(2^4\) induced subdiagrams, all elliptic, in eight \(\operatorname{Aut}\)-orbits.

    The parabolic family is empty, so its two orders are the empty order and
    the empty orbit order, and neither has a maximum.
    """
    diagram = d4()
    poset = diagram.subdiagram_poset()
    elliptic = diagram.elliptic_subdiagram_poset()
    parabolic = diagram.parabolic_subdiagram_poset()
    orbit_poset = diagram.subdiagram_orbit_poset(diagram.subdiagram_orbits())
    elliptic_orbits = diagram.elliptic_subdiagram_orbit_poset()
    parabolic_orbits = diagram.parabolic_subdiagram_orbit_poset()

    assert all(
        order in PartiallyOrderedSets()
        for order in (poset, elliptic, parabolic, orbit_poset, elliptic_orbits, parabolic_orbits)
    )
    assert poset.cardinality() == 16
    assert elliptic.cardinality() == 16
    assert parabolic.cardinality() == 0
    assert orbit_poset.cardinality() == 8
    assert elliptic_orbits.cardinality() == 8
    assert parabolic_orbits.cardinality() == 0

    # Every member of these orders keeps its vertex inclusion into D_4.
    assert all(point.arrow().codomain() is diagram for point in poset)
    assert all(point.arrow().codomain() is diagram for point in elliptic)


def test_an_outer_vertex_orbit_of_d4_is_the_orbit_not_its_representative() -> None:
    r"""Triality carries the three outer singletons to one another, so they are one orbit.

    The orbit set is that of the owned action of \(\operatorname{Aut}(D_4)\) on
    the ranks of the induced subdiagrams: the three ranks name one point of it,
    and that point holds all three.  The centre is fixed, so its orbit is a
    different point holding one.
    """
    diagram = d4()
    orbits = diagram.elliptic_subdiagram_orbits()
    vertices = diagram.index_set()
    centre = vertices[0]
    outer = (vertices[1], vertices[2], vertices[3])

    centre_orbit = orbits.orbit_of(diagram.subdiagram_rank((centre,)))
    outer_orbit = orbits.orbit_of(diagram.subdiagram_rank((outer[0],)))

    assert all(
        orbits.orbit_of(diagram.subdiagram_rank((vertex,))) == outer_orbit
        for vertex in outer
    )
    assert outer_orbit.points().cardinality() == 3
    assert centre_orbit.points().cardinality() == 1
    assert centre_orbit != outer_orbit
    assert outer_orbit.acting_group() is diagram.Aut()

    poset = diagram.elliptic_subdiagram_orbit_poset()
    assert poset.le(centre_orbit, outer_orbit) is False
