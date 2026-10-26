r"""Stabilizers in the orthogonal group of the hyperbolic plane."""

from sage_extensions.all import *


def test_e8_with_a_norm_eighteen_line_has_the_product_orthogonal_group() -> None:
    r"""The norm-two vectors span E8, so every isometry preserves that summand.

    Its perpendicular line permits two signs.  The E8 Dynkin diagram has
    no symmetry, and its Weyl group has order 2*8*12*14*18*20*24*30.
    Thus O(<18> + E8) has order 1393459200.
    """
    from sage.all import CartanMatrix, ZZ as SageZZ, block_diagonal_matrix, matrix

    gram = block_diagonal_matrix(matrix(SageZZ, [[18]]), matrix(SageZZ, CartanMatrix("E8")))
    lattice = Lattices(ZZ)([list(row) for row in gram.rows()])
    group = lattice.O()
    basis = tuple(lattice.module_generators().values())

    assert group.cardinality() == 1393459200
    for generator in group.group_generators():
        assert generator(basis[0]) in (basis[0], -basis[0])
        assert all(lattice.b(generator(x), generator(y)) == lattice.b(x, y)
                   for x in basis for y in basis)


def test_in_o_u_the_vector_e_has_trivial_stabilizer_and_its_line_a_stabilizer_of_order_two() -> None:
    r"""\(O(U)=\{\pm1,\pm\sigma\}\) with \(\sigma\) the swap \(e\leftrightarrow f\): an
    isometry fixes the isotropic vectors \(\{\pm e,\pm f\}\) setwise and is determined
    by the image of \(e\).  Only \(1\) fixes \(e\); \(\pm1\) carry \(\mathbb Ze\) onto
    itself, \(\pm\sigma\) send it to \(\mathbb Zf\).
    """
    lattice = Lattices(ZZ)("U")
    group = lattice.O()
    e = lattice.basis_vector(0)
    line = e.sublattice().inclusion()

    assert group.order() == 4
    assert group.stabilizer(e).order() == 1
    assert group.setwise_stabilizer(line).order() == 2
    assert group.pointwise_stabilizer(line).order() == 1
