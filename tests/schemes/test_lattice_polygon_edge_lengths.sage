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

    Coble cell 59 lists nineteen vectors labelled ``Sterk2Vectors``; Sterk cells 7--8 give
    them two roles.  ``v_1 = (-1,2)`` and ``v_19 = (1,2)`` are the side directions of the
    surgery triangles, and ``v_2`` through ``v_18`` are the seventeen steps of a boundary
    path walked from the origin.  Each step has a nonpositive x-coordinate, so the path
    does not close on itself.  Read with the source's own coefficients (``M_18_0_0``
    halves the odd-labelled lengths and adds ``l_1/2`` to ``v_4`` and ``l_19/2`` to
    ``v_16``), it ends on the x-axis at negative x, and the plotter's convex hull supplies
    one closing side running back along ``(1,0)``.  The polygon's edge directions are
    therefore ``v_2`` through ``v_18`` followed by ``(1,0)``, and the surgery directions
    are not edges of it even though ``v_1`` and ``v_6`` are the same vector.

    The dimension and the rays are read off that construction, not from a saved output.
    The eighteen directions span the plane, so the relations among them form an
    ``18 - 2`` dimensional space; multiplying the unit length vector by two makes every
    source coefficient a positive integer and the path still ends on the x-axis, so the
    closure cone meets the open positive orthant and fills that space.  An extreme ray of
    ``{l >= 0 : sum_i l_i v_i = 0}`` has minimal support, and a positive dependence on a
    set of directions says those directions are not contained in an open half-plane;
    triangulating their convex hull then exhibits a smaller such set unless only two
    directions (an antipodal pair) or three are involved.  Enumerating the antipodal pairs
    and the positively dependent triples of the recovered directions, and clearing each
    dependence's common factor, gives exactly the primitive rays of the cone.
    """
    plane = ZZ.free_module(2)
    weights = ZZ.free_module(18)
    edge_count = int(weights.module_rank())
    boundary = Sterk.sterk2_boundary_directions()
    surgery = Sterk.sterk2_surgery_directions()
    labels = tuple(boundary)
    steps = tuple(boundary[label] for label in labels)

    assert tuple(surgery) == ("v_1", "v_19")
    assert surgery["v_1"] == boundary["v_6"]
    assert surgery["v_19"] not in steps

    doubled = tuple(2 for _ in range(19))
    path = Sterk.sterk2_boundary_path(doubled)
    points = tuple(path[f"p_{index}"] for index in range(edge_count))
    walks = tuple(
        (
            points[index + 1][0] - points[index][0],
            points[index + 1][1] - points[index][1],
        )
        for index in range(edge_count - 1)
    )
    for index, direction in enumerate(steps):
        assert walks[index][0] <= 0
        assert walks[index][0].denominator() == 1
        assert walks[index][1].denominator() == 1
        assert walks[index][0] * direction[1] == walks[index][1] * direction[0]
        assert walks[index][0] * direction[0] + walks[index][1] * direction[1] > 0
    end = points[edge_count - 1]
    assert end[1] == 0
    assert end[0] < 0
    closing_length = -end[0]

    directions = steps + ((1, 0),)
    assert (
        sum(
            plane((walk[0].numerator(), walk[1].numerator())) for walk in walks
        )
        + closing_length.numerator() * plane((1, 0))
        == plane.zero()
    )

    edge_directions = weights.Mor(plane)(
        {index: plane(direction) for index, direction in enumerate(directions)}
    )
    lengths = RationalPolyhedralCones(weights).from_nonnegative_solutions(edge_directions)

    coefficients = Sterk.sterk2_direction_coefficients(doubled)
    assert all(coefficients[label].denominator() == 1 for label in labels)
    strictly_positive = weights(
        tuple(coefficients[label].numerator() for label in labels)
        + (closing_length.numerator(),)
    )
    assert all(coordinate > 0 for coordinate in strictly_positive.to_vector())
    assert lengths.contains(strictly_positive)

    assert lengths.dimension() == edge_count - int(plane.module_rank())
    assert lengths.is_pointed()

    def primitive_dependence(entries):
        divisor = ZZ(0)
        for entry in entries:
            divisor = ZZ(entry).gcd(divisor)
        return tuple(int(entry // divisor) for entry in entries)

    computed = set()
    for first in range(edge_count):
        for second in range(first + 1, edge_count):
            if directions[second] == tuple(-coordinate for coordinate in directions[first]):
                entries = [0] * edge_count
                entries[first] = 1
                entries[second] = 1
                computed.add(tuple(entries))
    for first in range(edge_count):
        for second in range(first + 1, edge_count):
            for third in range(second + 1, edge_count):
                left, middle, right = (
                    directions[first], directions[second], directions[third],
                )
                opposite_left = middle[0] * right[1] - middle[1] * right[0]
                opposite_middle = right[0] * left[1] - right[1] * left[0]
                opposite_right = left[0] * middle[1] - left[1] * middle[0]
                if (
                    opposite_left > 0
                    and opposite_middle > 0
                    and opposite_right > 0
                ):
                    entries = [0] * edge_count
                    entries[first] = opposite_left
                    entries[second] = opposite_middle
                    entries[third] = opposite_right
                    computed.add(primitive_dependence(entries))
                elif (
                    opposite_left < 0
                    and opposite_middle < 0
                    and opposite_right < 0
                ):
                    entries = [0] * edge_count
                    entries[first] = -opposite_left
                    entries[second] = -opposite_middle
                    entries[third] = -opposite_right
                    computed.add(primitive_dependence(entries))

    library_rays = sorted(
        tuple(int(coordinate) for coordinate in ray.to_vector())
        for ray in lengths.primitive_rays()
    )
    assert sorted(computed) == library_rays

    stored = Sterk.sterk2_stored_lengths()
    stored_coefficients = Sterk.sterk2_direction_coefficients(stored)
    stored_path = Sterk.sterk2_boundary_path(stored)
    assert all(stored_coefficients[label].denominator() == 1 for label in labels)
    assert stored_path["p_17"][1] == 0
    assert lengths.contains(
        weights(
            tuple(stored_coefficients[label].numerator() for label in labels)
            + ((-stored_path["p_17"][0]).numerator(),)
        )
    )
