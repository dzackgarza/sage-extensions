r"""A commutator Lie algebra lies in the Lie-algebra refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_matrix_commutator_algebra_is_lie() -> None:
    matrices = QQ.matrix_space(2)
    lie = Algebras(QQ).Associative().commutator_lie_algebra()(matrices)

    assert lie in Algebras(QQ).Lie()
    assert lie.alternation_decision() is True
    assert lie.jacobi_decision() is True
