r"""The identity of a commutator Lie algebra preserves its bracket."""

from sage_extensions.all import *  # noqa: F401,F403


def _matrix_commutator_lie_identity():
    matrices = QQ.matrix_space(2)
    lie = Algebras(QQ).Associative().commutator_lie_algebra()(matrices)
    identity = lie.Mor(lie).identity()
    return matrices, lie, identity


def test_lie_algebra_identity_has_the_expected_endpoints_and_action() -> None:
    matrices, lie, identity = _matrix_commutator_lie_identity()
    module = lie.underlying_module()
    e = module(matrices.matrix_unit(0, 1))

    assert identity.domain() is lie
    assert identity.codomain() is lie
    assert identity(e) == e


def test_lie_algebra_identity_preserves_the_commutator_bracket() -> None:
    matrices, lie, identity = _matrix_commutator_lie_identity()
    module = lie.underlying_module()
    e = module(matrices.matrix_unit(0, 1))
    f = module(matrices.matrix_unit(1, 0))

    assert identity(lie.bracket(e, f)) == lie.bracket(identity(e), identity(f))
    assert identity * identity == identity
