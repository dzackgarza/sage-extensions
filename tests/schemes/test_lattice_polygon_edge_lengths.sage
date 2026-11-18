r"""The cone of admissible edge lengths of a lattice polygon with prescribed primitive
edge directions.

A lattice polygon's edges, taken in cyclic order, have primitive lattice directions
``v_1, ..., v_n`` and nonnegative lattice lengths ``l_1, ..., l_n``; the polygon closes
exactly when ``sum_i l_i v_i = 0``.  So the lengths of the polygons with those directions
are the lattice points of the cone ``{ l in Z_{>=0}^n : sum_i l_i v_i = 0 }``, whose
dimension is the number of free parameters, whose primitive rays are the extremal closed
polygons, and whose Hilbert basis the indecomposable ones.

The specimens are moment polygons that Alexeev--Engel--Garza--Schaffler print for the
cusps of ``F(2,2,0)`` (*Compact moduli of Enriques surfaces of degree 2*, Nagoya Math. J.
259 (2025)).  Example 4.13 (p. 606) puts the vectors ``(3,-3), (2,2), (-3,3), (-2,-2)``
successively end-to-end, Example 4.14 (p. 608) the vectors ``(2,0), (-1,1), (-1,0),
(0,-1)``, and Example 4.15 (p. 608) the vectors ``(0,1), (-2,0), (0,-1)`` with the base
closed by a horizontal line.  A family of directions with no positive relation closes no
polygon: its cone is the origin.
"""

from sage_extensions.all import *


def test_the_polygon_of_example_4_13_closes_with_two_free_edge_lengths() -> None:
    r"""The printed vectors ``(3,-3), (2,2), (-3,3), (-2,-2)`` sum to zero, so their
    primitive directions ``(1,-1), (1,1), (-1,1), (-1,-1)`` have the length vector
    ``(3,2,3,2)`` in the closure cone.  The two opposite pairs move independently, so the
    cone is two-dimensional, spanned by ``(1,0,1,0)`` and ``(0,1,0,1)``; those two
    generators are unimodular, so they are already the Hilbert basis, and the printed
    lengths are ``3`` and ``2`` of them."""
    plane = ZZ.free_module(2)
    weights = ZZ.free_module(4)
    edge_directions = weights.Mor(plane)(
        {
            0: plane((1, -1)),
            1: plane((1, 1)),
            2: plane((-1, 1)),
            3: plane((-1, -1)),
        }
    )
    lengths = RationalPolyhedralCones(weights).from_nonnegative_solutions(edge_directions)

    assert plane((3, -3)) + plane((2, 2)) + plane((-3, 3)) + plane((-2, -2)) == plane.zero()
    assert lengths.dimension() == 2
    assert lengths.is_pointed()
    assert lengths.primitive_rays().cardinality() == 2
    assert weights((1, 0, 1, 0)) in lengths.primitive_rays()
    assert weights((0, 1, 0, 1)) in lengths.primitive_rays()
    assert lengths.hilbert_basis().cardinality() == 2
    assert weights((1, 0, 1, 0)) in lengths.hilbert_basis()
    assert weights((0, 1, 0, 1)) in lengths.hilbert_basis()
    assert lengths.contains(weights((3, 2, 3, 2)))
    assert weights((3, 2, 3, 2)) == 3 * weights((1, 0, 1, 0)) + 2 * weights((0, 1, 0, 1))


def test_the_polygon_of_example_4_14_closes_with_two_free_edge_lengths() -> None:
    r"""The printed vectors ``(2,0), (-1,1), (-1,0), (0,-1)`` sum to zero, with primitive
    directions ``(1,0), (-1,1), (-1,0), (0,-1)`` and lengths ``(2,1,1,1)``.  Writing the
    first and third lengths as the excess of ``l_1`` over ``l_2 = l_4``, the cone is
    two-dimensional and spanned by ``(1,0,1,0)`` and ``(1,1,0,1)``, which are unimodular:
    the printed lengths are their sum."""
    plane = ZZ.free_module(2)
    weights = ZZ.free_module(4)
    edge_directions = weights.Mor(plane)(
        {
            0: plane((1, 0)),
            1: plane((-1, 1)),
            2: plane((-1, 0)),
            3: plane((0, -1)),
        }
    )
    lengths = RationalPolyhedralCones(weights).from_nonnegative_solutions(edge_directions)

    assert plane((2, 0)) + plane((-1, 1)) + plane((-1, 0)) + plane((0, -1)) == plane.zero()
    assert lengths.dimension() == 2
    assert lengths.primitive_rays().cardinality() == 2
    assert weights((1, 0, 1, 0)) in lengths.primitive_rays()
    assert weights((1, 1, 0, 1)) in lengths.primitive_rays()
    assert lengths.hilbert_basis().cardinality() == 2
    assert lengths.contains(weights((2, 1, 1, 1)))
    assert weights((2, 1, 1, 1)) == weights((1, 0, 1, 0)) + weights((1, 1, 0, 1))


def test_the_polygon_of_example_4_15_closes_with_the_alternating_lengths() -> None:
    r"""Example 4.15 puts ``(0,1), (-2,0), (0,-1)`` end-to-end and closes the base by a
    horizontal line, so the primitive directions are ``(0,1), (-1,0), (0,-1), (1,0)`` and
    the printed lengths are ``(1,2,1,2)``: opposite edges have equal lengths, and the
    lengths alternate.  The cone is the two-dimensional cone spanned by ``(1,0,1,0)`` and
    ``(0,1,0,1)``, and the printed lengths are ``1`` and ``2`` of them.

    The paper keeps Sterk's numbering for the 0-cusps (§3.8, p. 590), so this is Sterk's
    second cusp, whose monodromy coordinates are the ``19`` roots of the ``(18,0,0)_1``
    diagram (§4.1, p. 599); the edge lengths of the printed closed polygon are the four
    that the diagonal folding leaves free."""
    plane = ZZ.free_module(2)
    weights = ZZ.free_module(4)
    edge_directions = weights.Mor(plane)(
        {
            0: plane((0, 1)),
            1: plane((-1, 0)),
            2: plane((0, -1)),
            3: plane((1, 0)),
        }
    )
    lengths = RationalPolyhedralCones(weights).from_nonnegative_solutions(edge_directions)

    assert plane((0, 1)) + plane((-2, 0)) + plane((0, -1)) + plane((2, 0)) == plane.zero()
    assert lengths.dimension() == 2
    assert lengths.primitive_rays().cardinality() == 2
    assert weights((1, 0, 1, 0)) in lengths.primitive_rays()
    assert weights((0, 1, 0, 1)) in lengths.primitive_rays()
    assert lengths.contains(weights((1, 2, 1, 2)))
    assert weights((1, 2, 1, 2)) == weights((1, 0, 1, 0)) + 2 * weights((0, 1, 0, 1))


def test_edge_directions_with_no_positive_relation_close_no_polygon() -> None:
    r"""Two independent directions in the plane are linearly independent, so the only
    nonnegative solution of ``l_1 (1,0) + l_2 (0,1) = 0`` is zero: the closure cone is the
    origin, with no rays and no Hilbert basis."""
    plane = ZZ.free_module(2)
    weights = ZZ.free_module(2)
    edge_directions = weights.Mor(plane)({0: plane((1, 0)), 1: plane((0, 1))})
    lengths = RationalPolyhedralCones(weights).from_nonnegative_solutions(edge_directions)

    assert lengths.dimension() == 0
    assert lengths.primitive_rays().cardinality() == 0
    assert lengths.hilbert_basis().cardinality() == 0
    assert lengths.contains(weights((0, 0)))
    assert not lengths.contains(weights((1, 0)))
    assert not lengths.contains(weights((0, 1)))


def test_the_sterk2_boundary_path_closes_with_the_horizontal_side() -> None:
    r"""The Sterk2 cusp's polygon has eighteen cyclic edges, not nineteen.

    Coble cell 59 lists nineteen vectors labelled ``Sterk2Vectors``, and Sterk cells 7--8
    give the two roles they have: ``v_1 = (-1,2)`` and ``v_19 = (1,2)`` are the surgery
    triangles' side directions, and ``v_2`` through ``v_18`` are the seventeen steps of a
    boundary path walked from the origin.  Every one of those seventeen has a nonpositive
    x-coordinate, so the path cannot close on itself: it ends at ``(-24, 0)`` for the
    stored lengths, and the closing side runs back along ``(1,0)``, which is the side the
    plotter's convex hull supplies.  The polygon's edge directions are therefore ``v_2``
    through ``v_18`` followed by ``(1,0)``.

    The stored lengths are not the lattice lengths: the source's ``M_18_0_0`` halves the
    odd-labelled ones and adds ``l_1/2`` to ``v_4`` and ``l_19/2`` to ``v_16``.  Read
    through that matrix the seventeen boundary coefficients are
    ``1, 1, 3, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 3, 1, 1``, so one prescribed direction has
    length zero in this specimen and the closing side has length ``24``.  The closure cone
    of the eighteen directions is sixteen-dimensional with sixty-five primitive rays, and
    exactly two of those rays have a two-element support: the two antipodal pairs
    ``{(0,1), (0,-1)}`` and ``{(-1,0), (1,0)}``.
    """
    plane = ZZ.free_module(2)
    directions = (
        (0, 1), (-1, 4), (-1, 3), (-2, 5), (-1, 2), (-2, 3), (-1, 1), (-2, 1), (-1, 0),
        (-2, -1), (-1, -1), (-2, -3), (-1, -2), (-2, -5), (-1, -3), (-1, -4), (0, -1),
        (1, 0),
    )
    weights = ZZ.free_module(18)
    edge_directions = weights.Mor(plane)(
        {index: plane(direction) for index, direction in enumerate(directions)}
    )
    lengths = RationalPolyhedralCones(weights).from_nonnegative_solutions(edge_directions)

    boundary_coefficients = (1, 1, 3, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 3, 1, 1)
    closing_length = 24
    closure = sum(
        coefficient * plane(direction)
        for coefficient, direction in zip(boundary_coefficients, directions[:-1])
    ) + closing_length * plane((1, 0))
    assert closure == plane.zero()

    assert lengths.dimension() == 16
    assert lengths.is_pointed()
    assert lengths.primitive_rays().cardinality() == 65
    assert lengths.has_a_nonzero_point()
    assert lengths.has_a_strictly_positive_point()

    stored = weights(boundary_coefficients + (closing_length,))
    assert lengths.contains(stored)

    two_element_rays = tuple(
        tuple(int(coordinate) for coordinate in ray.to_vector())
        for ray in lengths.primitive_rays()
        if sum(1 for coordinate in ray.to_vector() if coordinate != 0) == 2
    )
    assert two_element_rays == (
        (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0),
    )
