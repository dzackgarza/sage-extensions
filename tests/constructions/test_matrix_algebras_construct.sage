r"""Matrix endomorphism spaces carry their canonical associative unital algebra structure."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_by_two_rational_matrices_form_a_noncommutative_matrix_algebra() -> None:
    matrices = QQ.matrix_space(2)
    e01 = matrices.matrix_unit(0, 1)
    e10 = matrices.matrix_unit(1, 0)

    assert matrices in MatrixAlgebras(QQ)
    assert matrices.algebra_base_ring() is QQ
    assert not matrices.is_commutative()
    assert matrices.one() * e01 == e01
    assert e01 * matrices.one() == e01
    assert e01 * e10 != e10 * e01
    assert isinstance(matrices.one(), matrices.ElementType)


def test_one_by_one_rational_matrices_are_commutative() -> None:
    matrices = QQ.matrix_space(1)

    assert matrices in MatrixAlgebras(QQ)
    assert matrices.is_commutative()

