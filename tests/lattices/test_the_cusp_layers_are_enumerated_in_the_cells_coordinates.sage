r"""The cusp walk enumerates each layer in the coordinates of the cell at its point.

E. B. Vinberg, *On the groups of unit elements of certain quadratic forms*, Math.
USSR Sb. 16 (1972), §3.2, rule 1 with (39) (p. 27): before the sequence (38)
starts, the normals are the roots whose mirrors pass through the point \(p_0\),
and the cell \(P_0\) at that point is their intersection.  §4.1, the equation
(57) with the conditions (58) (p. 30): a layer of the walk is enumerated in the
coordinates of that cell, the vectors of the layer whose coordinates along the
normals are nonpositive.

The cell is therefore the walk's own object.  A walk whose roots through the
point cut no cell has no coordinates to enumerate in, and its layers are the
whole lattice's, so a record of that state carries no normals and no duals and
its two candidate lists are the one whole-lattice search.  A walk that cuts a
cell enumerates in its normals, and the record carries them with the adjugate
duals of their Gram, so that a candidate can be tested against the cell without
a coordinate computation: \(b(x,\tilde w_i)=\det(G)\,u_i(x)\) for the
coordinates \(u(x)\) along the normals, which is what makes "pairs nonpositively
with every dual" the cone condition (58).  The normals are read from the walk
that cuts the cell, so their orientation is the chamber's and not its
negation's: each of them is a wall of the chamber at the same point, with that
sign, and the walls through the point are exactly them.

Both lattices are read at their first isotropic basis vector, and the point of
the hyperbolic space is named as a class of the reduction, lifted to
\(v^\perp\) by the reduction's own frame: \(U\oplus U\oplus A_1\) reduces to
\(U\oplus A_1\) of rank three and signature (1, 2), and
\(U\oplus U\oplus A_1\oplus A_1\) to \(U\oplus A_1\oplus A_1\) of rank four and
signature (1, 3).  Both are small enough to run whole.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _reduction_image(*names):
    r"""Return the reduction image of the lattice named by ``names`` at its first isotropic vector.

    The vector is a primitive isotropic basis vector and the group is the stable
    orthogonal group of the lattice, so the reduction is \(v^\perp/\mathbf Z v\)
    and every reflection of the lattice lies in the group: the cell the walk cuts
    is the full reflection arrangement's.
    """
    lattice = Lattices(ZZ)(names[0])
    for name in names[1:]:
        lattice = lattice + Lattices(ZZ)(name)
    return lattice.stable_orthogonal_group().isotropic_vector_reduction_image(
        lattice.basis_vector(0)
    )


def _class(reduction, *coordinates):
    r"""Return the class of the reduction with the given coordinates in its frame."""
    return reduction(coordinates)


def _coordinates(element):
    r"""Return the coordinate tuple of a lattice element."""
    return tuple(int(entry) for entry in element.to_vector())


def _coordinates_of(family):
    r"""Return the coordinate tuples of a family of lattice elements, in order."""
    return tuple(_coordinates(element) for element in family)


def _pairing_matrix(reduction, family):
    r"""Return the matrix of the form on the family, as one contraction.

    ``gram_matrix`` is the lattice's own pairing of a finite family; the entries
    below are read off that matrix and never re-derived pairing by pairing.
    """
    return reduction.gram_matrix(basis=tuple(family))


def _count(family):
    r"""Return the cardinality of a finite family, as the index arithmetic below needs it."""
    return int(cardinal(sum(1 for _ in family)))


def test_a_walk_that_cuts_no_cell_reports_the_whole_lattice_layers() -> None:
    r"""A point whose roots cut no cell has no cell coordinates, and its layers are the lattice's.

    The point is the class \((-3,-3,-1,-1)\) of \(U\oplus A_1\oplus A_1\), of
    square \(14\), and the walk's cone at it is the single normal
    \((-1,1,0,0)\) in the reduction's frame: one independent root in a
    \(v_0^\perp\) of rank three.  Vinberg's cell (1972, §3.2, rule 1 and (39),
    p. 27) is cut by the roots through the point, and one normal spans no
    coordinate system of the rank-three perpendicular, so the walk has none to
    enumerate the layer (57) in and enumerates it over the whole lattice
    (§4.1, p. 30).  The record then states that: no normals, no duals, and
    both of its candidate lists are the one whole-lattice search.
    """
    image = _reduction_image("U", "U", "A1", "A1")
    reduction = image.reduction()
    controlling_vector = image.class_lift(_class(reduction, -3, -3, -1, -1))
    records = image.cusp_layer_enumerations(controlling_vector=controlling_vector, layers=1)

    assert records
    for record in records:
        assert _coordinates_of(record.cell_normals()) == ()
        assert _coordinates_of(record.cell_dual_normals()) == ()
        assert sorted(_coordinates_of(record.cell_candidates())) == sorted(
            _coordinates_of(record.whole_lattice_candidates())
        )


def _walls_through_the_point(reduction, point, wall_roots):
    r"""Return the walls of ``wall_roots`` that pass through ``point``, in order.

    The pairing of the point with the walls is one contraction of the family; the
    walls through the point are the entries of its row that vanish.
    """
    pairings = _pairing_matrix(reduction, (point,) + tuple(wall_roots))
    return tuple(
        wall
        for index, wall in enumerate(wall_roots)
        if pairings[0, index + 1] == ZZ.zero()
    )


def test_the_cell_normals_are_the_chambers_walls_through_the_point() -> None:
    r"""The normals the record carries are the walls through the point, with their orientation.

    The point is the class \((1,1,0)\) of \(U\oplus A_1\), of square \(2\), and
    the walls are the ones the same call computes there
    (:meth:`IsotropicVectorReductionImage.cusp_chamber`).  A root and its
    negative span one mirror, so the pairing with the point alone does not say
    which of them cuts the cell: the two are distinguished by which half-spaces
    bound the chamber, and the walk reads the cone it wrote down rather than a
    family it reoriented.  Asserted: the normals of the record are exactly the
    chamber's walls that pass through the point, as vectors and not as rays.

    The prefix of the sequence is asserted first, because the search at a cell
    oriented the other way accepts no wall of the chamber -- every candidate it
    enumerates pairs positively with the initial cone -- so the result of that
    defect is a walk that never closes, and the complete chamber below would not
    return at all.  The prefix is cut by that same initial cone, so it carries
    the same walls through the point and it reddens at once.
    """
    image = _reduction_image("U", "U", "A1")
    reduction = image.reduction()
    point = _class(reduction, 1, 1, 0)
    controlling_vector = image.class_lift(point)
    records = image.cusp_layer_enumerations(controlling_vector=controlling_vector, layers=2)
    prefix = image.cusp_chamber(controlling_vector, max_decompositions=1)
    prefix_through_the_point = _walls_through_the_point(
        reduction, point, tuple(prefix.wall_roots())
    )

    assert records
    assert prefix_through_the_point
    for record in records:
        assert sorted(_coordinates_of(record.cell_normals())) == sorted(
            _coordinates_of(prefix_through_the_point)
        )
    chamber = image.cusp_chamber(controlling_vector)
    through_the_point = _walls_through_the_point(
        reduction, point, tuple(chamber.wall_roots())
    )
    assert through_the_point
    for record in records:
        assert sorted(_coordinates_of(record.cell_normals())) == sorted(
            _coordinates_of(through_the_point)
        )


def test_the_dual_normals_are_the_adjugate_duals_of_the_cell_normals() -> None:
    r"""Each dual pairs with the normals as \(\det(G)\) on one and zero elsewhere.

    \(b(x,\tilde w_i)=\det(G)\,u_i(x)\) is the identity that makes the duals a
    test for the cone (58): the coordinates of \(x\) along the normals are
    nonpositive exactly when every pairing with a dual is.  A dual that fails
    the identity is not \(\det(G)\) times a dual basis vector, and the test it
    gives is then some other cone.
    """
    image = _reduction_image("U", "U", "A1")
    reduction = image.reduction()
    records = image.cusp_layer_enumerations(
        controlling_vector=image.class_lift(_class(reduction, 1, 1, 0)), layers=2
    )

    assert records
    for record in records:
        normals = tuple(record.cell_normals())
        duals = tuple(record.cell_dual_normals())
        assert normals
        assert _count(duals) == _count(normals)
        determinant = _pairing_matrix(reduction, normals).determinant()
        assert determinant != ZZ.zero()
        pairings = _pairing_matrix(reduction, normals + duals)
        size = _count(normals)
        expected = tuple(
            tuple(determinant if i == j else ZZ.zero() for j in range(size))
            for i in range(size)
        )
        actual = tuple(
            tuple(pairings[i, size + j] for j in range(size)) for i in range(size)
        )
        assert actual == expected, (
            f"the duals of layer {record.layer_number()} pair with the normals as {actual}, "
            f"not {expected}"
        )


def test_each_layers_cell_enumeration_is_its_whole_lattice_solutions_in_the_cell() -> None:
    r"""The walk's candidates are the layer's whole-lattice solutions in the cell.

    The walk enumerates the layer (57) in the nonpositive orthant of the cell's
    normals (58), and the engine enumerates the same equation with no condition
    at all; the two agree on the cell, which is the statement #400 asks of the
    coordinate enumeration.  The cell is proper at these layers -- some
    whole-lattice candidate pairs positively with a dual and so lies outside it
    -- so the agreement is not the equality of two identical searches.  The
    pairings of the candidates with the duals are one contraction of the family,
    read as the block the duals' rows have against the candidates' columns.
    """
    image = _reduction_image("U", "U", "A1")
    reduction = image.reduction()
    records = image.cusp_layer_enumerations(
        controlling_vector=image.class_lift(_class(reduction, 1, 1, 0)), layers=2
    )

    assert records
    for record in records:
        duals = tuple(record.cell_dual_normals())
        whole_lattice = tuple(record.whole_lattice_candidates())
        size = _count(duals)
        pairings = _pairing_matrix(reduction, duals + whole_lattice)

        def inside(index):
            return all(
                pairings[row, size + index] <= ZZ.zero() for row in range(size)
            )

        in_the_cell = tuple(
            candidate for index, candidate in enumerate(whole_lattice) if inside(index)
        )
        outside = tuple(
            candidate for index, candidate in enumerate(whole_lattice) if not inside(index)
        )
        assert sorted(_coordinates_of(in_the_cell)) == sorted(
            _coordinates_of(record.cell_candidates())
        ), (
            f"layer {record.layer_number()} of square {record.square()} at offset {record.offset()} "
            f"is not the layer's whole-lattice solutions in the cell"
        )
        assert outside, (
            f"layer {record.layer_number()} of square {record.square()} is cut by no wall of the cell: "
            f"every one of its whole-lattice solutions already lies inside it"
        )
