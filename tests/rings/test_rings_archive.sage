r"""Centrality in the ring of two-by-two rational matrices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_central_two_by_two_rational_matrices_are_the_scalar_matrices() -> None:
    r"""``Z(M_2(QQ)) = QQ * I`` (Lang, *Algebra*, XVII §1): it is a rank-one
    ``QQ``-module spanned by the identity; a matrix unit or a non-scalar diagonal
    matrix is not central."""
    matrices = QQ.matrix_space(2)
    center = matrices.ring_center()
    e11 = matrices.matrix_unit(0, 0)
    e12 = matrices.matrix_unit(0, 1)

    assert center.module_rank() == 1
    assert center.inclusion()(center.one()) == matrices.one()
    assert matrices.is_central(5 * matrices.one())
    assert not matrices.is_central(e12)
    assert not matrices.is_central(e11)
    assert not matrices.is_central(e11 - matrices.one())
    assert e11 * e12 != e12 * e11
