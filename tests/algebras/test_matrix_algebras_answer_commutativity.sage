r"""A matrix algebra decides whether it commutes.

\(M_n(R)\) over a commutative \(R\) is commutative exactly for \(n\le 1\): rank
one is \(R\) itself, and from rank two the matrix units \(e_{12}\) and
\(e_{21}\) multiply to different idempotents in the two orders.

The predicate is what a ring is asked for when it is placed among commutative
rings and among the algebras over itself, so an endomorphism ring that cannot
answer it cannot take that placement.
"""

from sage_extensions.all import *


def test_the_two_by_two_matrix_algebra_does_not_commute() -> None:
    matrices = QQ.matrix_space(2)
    rows = matrices.row_index_set()
    first = matrices.matrix_unit(rows[0], rows[1])
    second = matrices.matrix_unit(rows[1], rows[0])

    assert first * second != second * first
    assert matrices.is_commutative() is False


