r"""Symmetric algebras lie in the commutative-algebra refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_symmetric_algebra_is_commutative() -> None:
    algebra = QQ.free_module(2).symmetric_algebra()
    assert algebra in Algebras(QQ).Commutative()
    assert algebra.is_commutative()
