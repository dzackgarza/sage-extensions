r"""Eisenstein Hermitian lattices.

Tr(x conj y) on Z[w] is A2 (positive), so h=diag(1,1) has trace lattice of rank
4 and determinant 9. Its unitary group is mu_6 wr S_2, of order 6*6*2=72.
h=diag(1,-1) has trace signature (2,2). h=diag(1,1) and its image under a unit
change of basis have an order-linear isometry.
"""

from sage_extensions.all import *
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.number_field.number_field import CyclotomicField as SageCyclotomicField
from sage_extensions.categories.hermitian_lattices import HermitianLattice


def _diagonal(field, first, second):
    zero = field.zero()
    return sage_matrix(field, 2, 2, [field(int(first)), zero, zero, field(int(second))])


def _field():
    field = SageCyclotomicField(3)
    return field, field.gen()


def test_eisenstein_rank_two_trace_lattice_and_unitary_group():
    field, w = _field()
    lattice = HermitianLattice((field.one(), w), _diagonal(field, 1, 1))
    trace = lattice.trace_lattice()
    assert trace.module_rank() == 4
    assert trace.determinant() == 9
    isometry = lattice.unit_isometry(-w)
    assert lattice.is_order_linear(isometry)
    assert len(lattice.unitary_group_elements()) == 72


def test_indefinite_form_has_split_trace_signature():
    field, w = _field()
    lattice = HermitianLattice((field.one(), w), _diagonal(field, 1, -1))
    assert tuple(int(x) for x in lattice.trace_lattice().signature_pair()) == (2, 2)
    assert lattice.is_order_linear(lattice.unit_isometry(w))


def test_unit_scaled_basis_is_isometric():
    field, w = _field()
    first = HermitianLattice((field.one(), w), _diagonal(field, 1, 2))
    second = HermitianLattice((field.one(), w), _diagonal(field, 2, 1))
    witness = first.isometry_to(second)
    assert witness is not None


def test_mixed_sign_rank_two_form_over_zeta_five_has_unitary_order_200():
    r"""h=sqrt5*I is definite of opposite signs at the two places. U(h)=U(I) is mu_10 wr S_2, order 200."""
    field = SageCyclotomicField(5)
    z = field.gen()
    two = field(int(2))
    root = two*z*z + two*z*z*z + field.one()
    assert root*root == field(int(5))
    basis = (field.one(), z, z*z, z*z*z)
    zero = field.zero()
    lattice = HermitianLattice(basis, sage_matrix(field, 2, 2, [root, zero, zero, root]))
    generators = lattice.definite_unitary_group_generators()
    scaled = generators[0].domain()
    assert scaled.O().subgroup(generators).cardinality() == cardinal(200)
