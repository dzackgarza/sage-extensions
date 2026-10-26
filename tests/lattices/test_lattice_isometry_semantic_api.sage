r"""Isometry of lattices presented in different bases."""

from sage_extensions.all import *


def test_e8_with_a_norm_eighteen_line_has_integral_change_of_basis_witnesses() -> None:
    r"""An integral shear gives isometric presentations of either sign of <18> + E8."""
    from sage.all import CartanMatrix, ZZ as SageZZ, block_diagonal_matrix, identity_matrix, matrix

    gram = block_diagonal_matrix(matrix(SageZZ, [[18]]), matrix(SageZZ, CartanMatrix("E8")))
    change = identity_matrix(SageZZ, 9)
    change[0, 1] = 1
    changed = change * gram * change.transpose()
    for sign in (SageZZ.one(), -SageZZ.one()):
        source = Lattices(ZZ)([list(row) for row in (sign * gram).rows()])
        target = Lattices(ZZ)([list(row) for row in (sign * changed).rows()])
        coordinates = source.Isom(target)._witness_matrix()
        assert coordinates.transpose() * (sign * changed) * coordinates == sign * gram
        assert source.is_isometric(target)
        witness = source.Isom(target).an_element()
        basis = tuple(source.module_generators().values())
        assert all(witness.inverse()(witness(v)) == v for v in basis)
        assert all(target.b(witness(v), witness(w)) == source.b(v, w)
                   for v in basis for w in basis)


def test_binary_definite_forms_with_different_minima_are_not_isometric() -> None:
    r"""x^2+23y^2 represents 1, but 3x^2+2xy+8y^2 has minimum 3.

    The latter is 3(x+y/3)^2 + 23y^2/3: y != 0 gives a value above 3,
    and y=0 gives 3x^2. Both forms have determinant 23.
    """
    source = Lattices(ZZ)([[1, 0], [0, 23]])
    target = Lattices(ZZ)([[3, 1], [1, 8]])
    assert source.Isom(target).is_empty()


def test_a_change_of_basis_of_the_odd_unimodular_plane_is_isometric_to_it() -> None:
    r"""In \(\langle 1\rangle\oplus\langle -1\rangle\) the basis \((e, 2e + f)\) has Gram
    \(\begin{pmatrix}1&2\\2&3\end{pmatrix}\); an isometry to it preserves norms."""
    source = Lattices(ZZ)([[1, 0], [0, -1]])
    target = Lattices(ZZ)([[1, 2], [2, 3]])

    assert source.is_isometric_to(target)
    isometry = source.isometry_to(target)
    first, second = source.module_generators()
    for vector in (first, second, first + second):
        assert isometry(vector).q() == vector.q()
    assert isometry(first).b(isometry(second)) == 0
