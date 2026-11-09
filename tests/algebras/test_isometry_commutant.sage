r"""Commutants checked by hand.

B = diag(1, 2) and no isometries: A = M_2(Q), O = M_2(Z), and E_12 has adjoint E_21 / 2.

U + U with basis e1, f1, e2, f2 and the Eichler transvection F = 1 + N, N f1 = e2,
N f2 = -e1. N^2 = 0 with rank 2, so Q^4 is free of rank two over Q[t]/(t^2) and the
commutant is M_2(Q[t]/(t^2)): dimension 8, radical tM_2 of dimension 4.

B = diag(1, 1, -1), F1 swaps the first two coordinates, F2 negates the first. They
do not commute and generate the dihedral group of order 8, absolutely irreducible on
the first two coordinates and trivial on the third, so A = {diag(a, a, b)}, O = Z x Z,
and the centralizer in O(L) is the four matrices diag(+-1, +-1, -+1) with equal first two.
"""

from sage_extensions.all import *
from sage.matrix.constructor import matrix as sage_matrix
from sage.matrix.special import diagonal_matrix, identity_matrix
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage_extensions.algebras.isometry_commutant import IsometryCommutant

U2 = sage_matrix(SageZZ, 4, 4, [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0])
EICHLER = sage_matrix(SageZZ, 4, 4, [1, 0, 0, -1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1])


def test_empty_commutant_is_not_adjoint_stable_on_nonunimodular_lattice():
    commutant = IsometryCommutant(diagonal_matrix(SageZZ, [int(1), int(2)]), [])
    assert commutant.dimension() == 4
    assert commutant.is_semisimple()
    assert not commutant.order_is_adjoint_stable()
    unit = sage_matrix(SageZZ, 2, 2, [0, 1, 0, 0])
    assert commutant.adjoint(unit) == sage_matrix(SageQQ, int(2), int(2), [SageQQ(int(0)), SageQQ(int(0)), SageQQ(int(1)) / SageQQ(int(2)), SageQQ(int(0))])


def test_nonsemisimple_commutant_of_eichler_transvection():
    commutant = IsometryCommutant(U2, [EICHLER])
    assert commutant.dimension() == 8
    assert len(commutant.radical_basis()) == 4
    assert not commutant.is_semisimple()
    assert commutant.order_is_adjoint_stable()
    assert all(commutant.contains(commutant.adjoint(m)) for m in commutant.order_basis)
    for power in (EICHLER, EICHLER**5, EICHLER**-3):
        assert commutant.is_centralizer_element(power)
    assert EICHLER**5 != identity_matrix(SageZZ, 4)
    table = commutant.multiplication_table()
    for i, left in enumerate(commutant.order_basis):
        for j, right in enumerate(commutant.order_basis):
            assert sum(c * m for c, m in zip(table[i][j], commutant.order_basis)) == left * right


def test_unipotent_kernel_of_eichler_transvection_is_generated_by_it():
    r"""rad = N M_2(Z), and N m is skew exactly for m symmetric under the symplectic involution of M_2, the scalars."""
    commutant = IsometryCommutant(U2, [EICHLER])
    generators = commutant.unipotent_kernel_generators()
    assert len(generators) == int(1)
    assert generators[0] in (EICHLER, EICHLER.inverse())
    assert commutant.is_centralizer_element(generators[0])


def test_noncommuting_isometries_have_simultaneous_commutant():
    swap = sage_matrix(SageZZ, 3, 3, [0, 1, 0, 1, 0, 0, 0, 0, 1])
    negate = diagonal_matrix(SageZZ, [SageZZ(-1), SageZZ(1), SageZZ(1)])
    assert swap * negate != negate * swap
    commutant = IsometryCommutant(diagonal_matrix(SageZZ, [SageZZ(1), SageZZ(1), SageZZ(-1)]), [swap, negate])
    assert commutant.dimension() == 2
    expected = [diagonal_matrix(SageZZ, [SageZZ(a), SageZZ(a), SageZZ(b)]) for a in (1, -1) for b in (1, -1)]
    assert all(commutant.is_centralizer_element(u) for u in expected)
    assert not commutant.is_centralizer_element(diagonal_matrix(SageZZ, [SageZZ(1), SageZZ(-1), SageZZ(1)]))
    assert not commutant.is_centralizer_element(diagonal_matrix(SageZZ, [SageZZ(2), SageZZ(2), SageZZ(1)]))
