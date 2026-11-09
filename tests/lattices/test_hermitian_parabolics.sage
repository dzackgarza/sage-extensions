r"""The Gaussian unipotent group of J = antidiag(1,1,1).

On Z[i]^3 with the standard frame, n(Z,T) is integral iff Z and T - N(Z)/2 lie
in Z[i]. T is purely imaginary, so N(Z) is even: Z lies in (1+i)Z[i], and the
centre is Zi. In the frame diag(1/2,1,2), the same conjugation by the frame
gives Z in 2(1+i)Z[i] and centre 4Zi, and n(1+i,i) is rejected.
"""

from sage_extensions.all import *
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.number_field.number_field import CyclotomicField as SageCyclotomicField
from sage_extensions.categories.hermitian_lattices import HermitianLattice, HermitianWittFrame
from sage.rings.integer_ring import ZZ as SZZ
from sage.rings.rational_field import QQ as SQQ
from sage.rings.integer_ring import ZZ as SZZ
from sage.rings.rational_field import QQ as SQQ


def _gaussian():
    field = SageCyclotomicField(4)
    i = field.gen()
    one, zero = field.one(), field.zero()
    gram = sage_matrix(field, 3, 3, [zero, zero, one, zero, one, zero, one, zero, zero])
    return field, i, HermitianLattice((one, i), gram), sage_matrix(field, 1, 1, [one])


def _frame(field, lattice, middle, first, last):
    half = sage_matrix(field, 3, 3, [first, field.zero(), field.zero(), field.zero(), field.one(), field.zero(), field.zero(), field.zero(), last])
    return HermitianWittFrame(lattice, half, middle, int(1))


def _parameters(field, Z, T):
    return sage_matrix(field, 1, 1, [Z]), sage_matrix(field, 1, 1, [T])


def test_source_gaussian_unipotent_has_the_stated_matrix_and_law():
    field, i, lattice, middle = _gaussian()
    frame = _frame(field, lattice, middle, field.one(), field.one())
    one = field.one()
    first = _parameters(field, one + i, i)
    second = _parameters(field, one - i, field.zero())
    n = frame.unipotent(*first)
    assert n == sage_matrix(field, 3, 3, [one, -(one - i), -one + i, field.zero(), one, one + i, field.zero(), field.zero(), one])
    assert n.conjugate_transpose() * frame.j() * n == frame.j()
    assert n.det() == one
    product = frame.compose(first, second)
    assert frame.unipotent(*product) == n * frame.unipotent(*second)
    assert product[1] != first[1] + second[1]


def test_levi_conjugation_matches_matrices():
    field, i, lattice, middle = _gaussian()
    frame = _frame(field, lattice, middle, field.one(), field.one())
    A = sage_matrix(field, 1, 1, [i])
    U = sage_matrix(field, 1, 1, [-field.one()])
    parameters = _parameters(field, field.one() + i, i)
    levi = frame.levi(A, U)
    assert levi * frame.unipotent(*parameters) * ~levi == frame.unipotent(*frame.conjugate(A, U, parameters))


def _z_lattice(field, generators):
    rows = [list(pair[0][0, 0].vector()) for pair in generators]
    return sage_matrix(SQQ, rows)


def test_integral_kernel_of_the_standard_frame():
    field, i, lattice, middle = _gaussian()
    frame = _frame(field, lattice, middle, field.one(), field.one())
    generators, centre = frame.integral_unipotent_kernel()
    assert all(frame.preserves_lattice(frame.unipotent(*pair)) for pair in generators + centre)
    assert len(centre) == int(1) and centre[0][1][0, 0] in (i, -i)
    rows = _z_lattice(field, generators)
    assert int(rows.change_ring(SZZ).echelon_form()[:2].det().abs()) == int(2)
    assert frame.preserves_lattice(frame.unipotent(*_parameters(field, field.one() + i, i)))
    assert not frame.preserves_lattice(frame.unipotent(*_parameters(field, field.one(), field.zero())))


def test_nonstandard_frame_rejects_the_rational_unitary():
    field, i, lattice, middle = _gaussian()
    half = field.one() / field(int(2))
    frame = _frame(field, lattice, middle, half, field(int(2)))
    candidate = frame.unipotent(*_parameters(field, field.one() + i, i))
    assert candidate.conjugate_transpose() * frame.j() * candidate == frame.j()
    assert not frame.preserves_lattice(candidate)
    generators, centre = frame.integral_unipotent_kernel()
    assert int(_z_lattice(field, generators).change_ring(SZZ).echelon_form()[:2].det().abs()) == int(8)
    assert centre[0][1][0, 0] in (field(int(4)) * i, field(int(-4)) * i)


def test_levi_image_of_the_standard_frame_is_all_sixteen_pairs():
    field, i, lattice, middle = _gaussian()
    frame = _frame(field, lattice, middle, field.one(), field.one())
    units = [i**k for k in range(4)]
    pairs = [(sage_matrix(field, 1, 1, [a]), sage_matrix(field, 1, 1, [b])) for a in units for b in units]
    assert len(frame.liftable_levi_image(pairs)) == int(16)


def test_witt_frame_of_a_null_vector_in_the_odd_lattice_has_centre_zi():
    r"""On diag(1,1,-1) with v = (1,0,1), n(0,T) is y -> y + T B(v,y) v with B(v,y) = y_1 - y_3, integral iff T lies in Z[i]; T is skew, so T in Zi."""
    field = SageCyclotomicField(4)
    i = field.gen()
    one, zero = field.one(), field.zero()
    lattice = HermitianLattice((one, i), sage_matrix(field, 3, 3, [one, zero, zero, zero, one, zero, zero, zero, -one]))
    frame = lattice.witt_frame([[one, zero, one]])
    generators, centre = frame.integral_unipotent_kernel()
    assert len(centre) == int(1)
    assert centre[0][1][0, 0] in (i, -i)
    assert all(frame.preserves_lattice(frame.unipotent(*pair)) for pair in generators + centre)


def test_rank_two_isotropic_frame_has_rank_four_centre():
    r"""Skew T in M_2(Z[i]): diagonal in Zi, off-diagonal b in Z[i]. The frame has no middle."""
    field = SageCyclotomicField(4)
    i = field.gen()
    one, zero = field.one(), field.zero()
    gram = sage_matrix(field, 4, 4, [zero, zero, one, zero, zero, zero, zero, one, one, zero, zero, zero, zero, one, zero, zero])
    lattice = HermitianLattice((one, i), gram)
    frame = lattice.witt_frame([[one, zero, zero, zero], [zero, one, zero, zero]])
    generators, centre = frame.integral_unipotent_kernel()
    assert len(centre) == int(4)
    assert all(frame.preserves_lattice(frame.unipotent(*pair)) for pair in centre)
    half = _skew(field, i / field(int(2)))
    assert not frame.preserves_lattice(frame.unipotent(sage_matrix(field, 0, 2), half))


def _skew(field, value):
    return sage_matrix(field, 2, 2, [value, field.zero(), field.zero(), field.zero()])
