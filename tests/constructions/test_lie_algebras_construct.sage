r"""The commutator algebra of 2×2 matrices is a Lie algebra."""

from sage_extensions.all import *  # noqa: F401,F403


def test_matrix_commutator_lie_algebra_exposes_its_bracket() -> None:
    matrices = QQ.matrix_space(2)
    lie = Algebras(QQ).Associative().commutator_lie_algebra()(matrices)
    module = lie.underlying_module()
    e = module(matrices.matrix_unit(0, 1))
    f = module(matrices.matrix_unit(1, 0))

    assert lie in LieAlgebras(QQ)
    assert lie.bracket(e, f) == module(
        matrices.matrix_unit(0, 0) - matrices.matrix_unit(1, 1)
    )
    assert lie.bracket(e, e) == module.zero()

