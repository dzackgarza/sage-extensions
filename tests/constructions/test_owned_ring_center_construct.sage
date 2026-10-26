r"""The center of a matrix ring is the scalar-matrix subring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_by_two_matrix_ring_center_contains_scalars_not_matrix_units() -> None:
    matrices = QQ.matrix_space(2)
    center = matrices.ring_center()
    identity = matrices.identity_matrix()
    matrix_unit = matrices.matrix_unit(0, 1)

    assert center.ambient_ring() is matrices
    assert identity in center
    assert matrix_unit not in center
