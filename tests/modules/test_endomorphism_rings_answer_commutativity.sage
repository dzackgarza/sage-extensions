r"""An endomorphism ring over any base decides whether it commutes.

\(\operatorname{End}_R(F)\cong M_n(R)\) for \(F\) free of rank \(n\), and the
answer depends on the ring and on the rank together once \(R\) is not assumed
commutative.  Rank zero is the zero ring and commutes whatever \(R\) is.  Rank
one is \(R\) acting on itself and commutes exactly when \(R\) does.  From rank
two the matrix units force \(1=0\), so only the zero ring commutes.

The specimen base is \(M_2(\mathbf Q)\), which is an owned ring and is not
commutative.  The rank-zero row is the one that separates the statement from
its base: the base does not commute and the endomorphism ring does.

A ring is asked this before it is placed among the commutative rings and among
the algebras over itself, so an endomorphism ring that cannot answer cannot
take that placement.
"""

from sage_extensions.all import *


def _noncommutative_base():
    r"""Return \(M_2(\mathbf Q)\), an owned ring that does not commute."""
    return QQ.matrix_space(2)


def test_a_square_endomorphism_ring_over_a_noncommutative_base_does_not_commute() -> None:
    base = _noncommutative_base()

    assert base.is_commutative() is False
    assert base.matrix_space(2).is_commutative() is False


def test_the_endomorphisms_of_the_zero_module_commute_over_any_base() -> None:
    base = _noncommutative_base()

    assert base.matrix_space(0).is_commutative() is True
