r"""Associative algebras become Lie algebras under the commutator bracket.

For ``M_2(QQ)``, the matrix units ``E01,E10`` have bracket
``E00-E11`` and generate the standard ``sl_2`` commutator relations.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_matrix_commutator_lie_algebra_has_standard_brackets() -> None:
    matrices = QQ.matrix_space(2)
    lie = Algebras(QQ).Associative().commutator_lie_algebra()(matrices)
    module = lie.underlying_module()
    e = module(matrices.matrix_unit(0, 1))
    f = module(matrices.matrix_unit(1, 0))
    h = lie.bracket(e, f)

    assert lie in CommutatorLieAlgebras(QQ)
    assert lie in LieAlgebras(QQ)
    assert isinstance(e, lie.ElementType)
    assert lie.bracket(e, e) == module.zero()
    assert lie.bracket(h, e) == 2 * e
    assert lie.bracket(h, f) == -2 * f

