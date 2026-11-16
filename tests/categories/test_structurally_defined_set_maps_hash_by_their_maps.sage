r"""A map that carries structure hashes the set map it retains.

A monotone map of partial orders, a continuous map, a graph morphism and a
chamber-system morphism are each a map of the underlying sets that preserves
the structure the two objects carry (a partial order; the open sets; the
adjacency relation; the type-preserving adjacencies).  Equality of two such
maps of one set of morphisms is equality of their underlying set maps, and a
set map's hash reads its values on its domain, so equal morphisms hash alike
and a finite ordered set holds them.  This is the rule of :class:`Sets` applied
at each of the four owners.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_monotone_maps_are_one_point_and_maps_of_two_orders_are_two() -> None:
    r"""The diamond ``{0, 1, 2, 3}`` with ``0`` below everything and ``3`` above it.

    The identity of the diamond is one monotone map, and the collapse onto the
    chain ``0 < 1`` is a monotone map out of it: two morphisms of two different
    sets of morphisms, which the same finite ordered set holds.
    """
    diamond_points = Sets.Δ[3]
    chain_points = Sets.Δ[1]
    diamond = PartiallyOrderedSets()(
        diamond_points,
        lambda left, right: left == right or int(left) == 0 or int(right) == 3,
    )
    chain = PartiallyOrderedSets()(chain_points, lambda left, right: int(left) <= int(right))
    identity = PartiallyOrderedSets().Mor(diamond, diamond).identity()
    collapse = PartiallyOrderedSets().Mor(diamond, chain)(
        lambda point: chain(0 if int(point) == 0 else 1), check=True
    )

    assert hash(identity) == hash(PartiallyOrderedSets().Mor(diamond, diamond).identity())
    assert FiniteOrderedSets()((identity,)).cardinality() == 1
    assert FiniteOrderedSets()((identity, collapse)).cardinality() == 2


def test_two_continuous_maps_with_the_same_values_are_one_point() -> None:
    r"""The identity function on two points is one continuous map of the two topologies.

    Both maps send the point at ``s`` of the indiscrete space to the point at
    ``s`` of the Sierpinski space, so they are one map and one point of a finite
    ordered set.
    """
    points = Sets.Δ[1]
    spaces = TopologicalSpaces()
    indiscrete = spaces(points, ((), points))
    sierpinski = spaces(points, ((), (points(1),), points))
    toward = spaces.Mor(indiscrete, sierpinski)(
        lambda point: sierpinski(0) if point == indiscrete(0) else sierpinski(1)
    )
    rebuilt = spaces.Mor(indiscrete, sierpinski)(
        lambda point: sierpinski(0) if point == indiscrete(0) else sierpinski(1)
    )

    assert toward == rebuilt
    assert hash(toward) == hash(rebuilt)
    assert FiniteOrderedSets()((toward, rebuilt)).cardinality() == 1


def test_a_graph_morphism_hashes_its_vertex_map() -> None:
    r"""The swap of the two vertices of an edge is one graph automorphism.

    The graph is symmetric, so the swap of ``0`` and ``1`` preserves the single
    adjacency ``(0, 1)``; the identity is another, and the two are distinct
    morphisms of the one set of endomorphisms.
    """
    edge = Graphs().from_edges((0, 1), ((0, 1),))
    swap = Graphs().Mor(edge, edge)(lambda vertex: edge(1 - int(vertex)))
    identity = Graphs().Mor(edge, edge).identity()

    assert hash(swap) == hash(Graphs().Mor(edge, edge)(lambda vertex: edge(1 - int(vertex))))
    assert FiniteOrderedSets()((identity,)).cardinality() == 1
    assert swap(edge(0)) == edge(1)


def test_a_chamber_system_morphism_hashes_its_chamber_map() -> None:
    r"""One chamber and its single type: the identity of the system is a morphism.

    The system has the chambers ``{0, 1}`` and the adjacency relation of type
    ``s`` that holds of every ordered pair, so every map of the chambers
    preserves it.
    """
    system = ChamberSystems().from_adjacencies(
        (0, 1), ("s",), {"s": ((0, 0), (0, 1), (1, 0), (1, 1))}
    )
    identity = ChamberSystems().Mor(system, system).identity()
    swap = ChamberSystems().Mor(system, system)(lambda chamber: system(1 - int(chamber)))

    assert hash(identity) == hash(ChamberSystems().Mor(system, system).identity())
    assert FiniteOrderedSets()((identity,)).cardinality() == 1
    assert swap(system(0)) == system(1)
