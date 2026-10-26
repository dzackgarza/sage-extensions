r"""Square matrix spaces realize endomorphism rings of framed free modules.

In ``M_2(ZZ)``, diagonal and identity matrices are canonical, trace is the sum
of diagonal entries, units are exactly the invertible endomorphisms, and the
ring is noncommutative.  In rank one the matrix endomorphism ring is commutative.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_matrix_endomorphism_space_has_diagonal_identity_and_noncommutativity() -> None:
    matrices = ZZ.matrix_space(2, 2)
    diagonal = matrices.diagonal([2, 3])
    identity = matrices.identity_matrix()

    assert matrices in MatrixEndomorphismSpaces(ZZ)
    assert diagonal == matrices.from_rows([[2, 0], [0, 3]])
    assert identity == matrices.from_rows([[1, 0], [0, 1]])
    assert not matrices.is_commutative()
    assert ZZ.matrix_space(1, 1).is_commutative()
    assert isinstance(identity, matrices.ElementType)


def test_matrix_endomorphisms_expose_trace_and_unit_predicate() -> None:
    matrices = ZZ.matrix_space(2, 2)
    unit = matrices.from_rows([[2, 1], [1, 1]])
    nonunit = matrices.diagonal([2, 1])

    assert unit.trace() == 3
    assert unit.is_unit()
    assert not nonunit.is_unit()


def test_matrix_endomorphism_space_morphisms_have_identity() -> None:
    matrices = ZZ.matrix_space(2, 2)
    identity = Modules(ZZ).Mor(matrices, matrices).identity()

    assert identity(matrices.zero()) == matrices.zero()
    assert identity * identity == identity
