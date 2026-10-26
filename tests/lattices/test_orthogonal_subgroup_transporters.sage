r"""Vector equivalence under special orthogonal groups, with transporters."""

from sage_extensions.all import *


def test_a_root_of_a2_and_its_negative_are_equivalent_under_so() -> None:
    r"""\(-\mathrm{id}\) has determinant \((-1)^2=1\) on the rank-2 lattice \(A_2\), so
    \(r\) and \(-r\) lie in one \(SO(A_2)\)-orbit; \(|SO(A_2)|=|O(A_2)|/2=12/2=6\)
    (\(O(A_2)=W(A_2)\times\{\pm1\}\), Conway--Sloane, *SPLAG*, ch. 4 §6.1).
    """
    lattice = Lattices(ZZ)("A2")
    special = lattice.SO()
    root = lattice.basis_vector(0)

    assert special.order() == 6
    assert special.vectors_are_equivalent(root, -root)
    witness = special.vector_equivalence_witness(root, -root)
    assert witness in special
    assert witness(root) == -root


def test_two_basis_vectors_of_the_cubic_lattice_are_equivalent_under_so() -> None:
    r"""On \(\mathbb Z^3\), \(e_1\mapsto e_2\mapsto -e_1\), \(e_3\mapsto e_3\) is an
    isometry of determinant 1 carrying \(e_1\) to \(e_2\)."""
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    first, second, _third = lattice.module_generators()
    special = lattice.SO()

    assert special.vectors_are_equivalent(first, second)
    witness = special.vector_equivalence_witness(first, second)
    assert witness in special
    assert witness.determinant() == 1
    assert witness(first) == second
