r"""The cusp walk enumerates each layer in the coordinates of the cell at its point.

E. B. Vinberg, *On the groups of unit elements of certain quadratic forms*, Math.
USSR Sb. 16 (1972), §3.2, rule 1 with (39) (p. 27): before the sequence (38)
starts, the normals are the roots whose mirrors pass through the point \(p_0\),
and the cell \(P_0\) at that point is their intersection.  §4.1, the equation
(57) with the conditions (58) (p. 30): a layer of the walk is enumerated in the
coordinates of that cell, the vectors of the layer whose coordinates along the
normals are nonpositive.

The cell is therefore the walk's own object, and the layers a call reports are
only that call's when the walk has one: a walk that cut no cell has no
coordinates to enumerate in, and its layers are the whole lattice's.  The
records below carry the cell's normals and the adjugate duals of their Gram, so
that a candidate can be tested against the cell without a coordinate
computation: \(b(x,\tilde w_i)=\det(G)\,u_i(x)\) for the coordinates \(u(x)\)
along the normals, which is what makes "pairs nonpositively with every dual"
the cone condition (58).

The lattice is \(U\oplus U\oplus A_1\) at its first isotropic basis vector: the
reduction is \(U\oplus A_1\), of rank three and signature (1, 2), at the point
\(e_2+f_2\) of its hyperbolic space.  It is small enough to run whole: two
layers, each enumerated both ways.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _cusp_image():
    r"""Return \(U\oplus U\oplus A_1\) and its reduction image at the isotropic \(e_0\).

    The vector \(e_0\) is primitive and isotropic and the group is the stable
    orthogonal group of the lattice, so the reduction \(e_0^\perp/\mathbf Z e_0\)
    is \(U\oplus A_1\) and every reflection of the lattice lies in the group: the
    cell the walk cuts is the full reflection arrangement's.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)("A1")
    return lattice, lattice.stable_orthogonal_group().isotropic_vector_reduction_image(
        lattice.basis_vector(0)
    )


def _point_on_a_mirror(lattice):
    r"""Return \(e_2+f_2\), a point of the hyperbolic space of the reduction.

    It pairs zero with the isotropic vector \(e_0\) and has square \(2\), so it
    spans a timelike class in \(e_0^\perp/\mathbf Z e_0\) and is a point of that
    hyperbolic space: the point \(p_0\) of Vinberg 1972, §3.2.
    """
    return lattice.basis_vector(2) + lattice.basis_vector(3)


def _gram_determinant(reduction, normals):
    r"""Return \(\det G\) for the Gram \(G=(b(w_i,w_j))\) of ``normals``."""
    return Lattices(ZZ)(
        [[reduction.b(left, right) for right in normals] for left in normals]
    ).determinant()


def test_the_dual_normals_are_the_adjugate_duals_of_the_cell_normals() -> None:
    r"""Each dual pairs with the normals as \(\det(G)\) on one and zero elsewhere.

    \(b(x,\tilde w_i)=\det(G)\,u_i(x)\) is the identity that makes the duals a
    test for the cone (58): the coordinates of \(x\) along the normals are
    nonpositive exactly when every pairing with a dual is.  A dual that fails
    the identity is not \(\det(G)\) times a dual basis vector, and the test it
    gives is then some other cone.
    """
    lattice, image = _cusp_image()
    reduction = image.reduction()
    records = image.cusp_layer_enumerations(controlling_vector=_point_on_a_mirror(lattice), layers=2)

    assert records
    for record in records:
        normals = record.cell_normals()
        duals = record.cell_dual_normals()
        assert normals
        assert cardinal(sum(1 for _ in duals)) == cardinal(sum(1 for _ in normals))
        determinant = _gram_determinant(reduction, normals)
        assert determinant != 0
        pairings = tuple(
            tuple(reduction.b(normal, dual) for dual in duals) for normal in normals
        )
        expected = tuple(
            tuple(determinant if i == j else ZZ.zero() for j, _ in enumerate(duals))
            for i, _ in enumerate(normals)
        )
        assert pairings == expected, (
            f"the duals of layer {record.layer_number()} pair with the normals as {pairings}, "
            f"not {expected}"
        )


def test_each_layers_cell_enumeration_is_its_whole_lattice_solutions_in_the_cell() -> None:
    r"""The walk's candidates are the layer's whole-lattice solutions in the cell.

    The walk enumerates the layer (57) in the nonpositive orthant of the cell's
    normals (58), and the engine enumerates the same equation with no condition
    at all; the two agree on the cell, which is the statement #400 asks of the
    coordinate enumeration.  The cell is proper at these layers -- some
    whole-lattice candidate pairs positively with a dual and so lies outside it
    -- so the agreement is not the equality of two identical searches.
    """
    lattice, image = _cusp_image()
    reduction = image.reduction()
    records = image.cusp_layer_enumerations(controlling_vector=_point_on_a_mirror(lattice), layers=2)

    assert records
    for record in records:
        duals = record.cell_dual_normals()
        whole_lattice = tuple(record.whole_lattice_candidates())
        in_the_cell = tuple(
            candidate
            for candidate in whole_lattice
            if all(reduction.b(candidate, dual) <= 0 for dual in duals)
        )
        outside = tuple(
            candidate
            for candidate in whole_lattice
            if any(reduction.b(candidate, dual) > 0 for dual in duals)
        )
        assert sorted(tuple(int(entry) for entry in candidate.to_vector()) for candidate in in_the_cell) == sorted(
            tuple(int(entry) for entry in candidate.to_vector()) for candidate in record.cell_candidates()
        ), (
            f"layer {record.layer_number()} of square {record.square()} at offset {record.offset()} "
            f"is not the layer's whole-lattice solutions in the cell"
        )
        assert outside, (
            f"layer {record.layer_number()} of square {record.square()} is cut by no wall of the cell: "
            f"every one of its whole-lattice solutions already lies inside it"
        )
