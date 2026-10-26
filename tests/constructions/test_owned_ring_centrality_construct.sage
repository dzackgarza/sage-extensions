r"""Scalar matrices are central in a full matrix ring; matrix units need not be."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_by_two_matrix_ring_distinguishes_central_from_noncentral_elements() -> None:
    matrices = QQ.matrix_space(2)
    identity = matrices.identity_matrix()
    matrix_unit = matrices.matrix_unit(0, 1)

    assert matrices.is_central(identity)
    assert not matrices.is_central(matrix_unit)
