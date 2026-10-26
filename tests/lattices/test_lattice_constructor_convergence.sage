r"""Isotropic reduction of an orthogonal sum with a hyperbolic plane."""

from sage_extensions.all import *


def test_the_isotropic_reduction_of_U_plus_A2_along_e_is_A2() -> None:
    r"""With \(U = \langle e, f\rangle\), \(e^\perp = \mathbb Z e \oplus A_2\) in
    \(U \oplus A_2\), so \(e^\perp/\mathbb Z e \cong A_2\), of determinant \(3\)."""
    root_lattice = Lattices(ZZ)("A2")
    lattice = Lattices(ZZ)("U") + root_lattice
    e = lattice.basis_vector(0)

    reduced = e.isotropic_reduction().quotient_lattice()

    assert reduced.rank() == 2
    assert reduced.determinant() == 3
    assert reduced.is_even()
    assert reduced.is_isometric_to(root_lattice)
