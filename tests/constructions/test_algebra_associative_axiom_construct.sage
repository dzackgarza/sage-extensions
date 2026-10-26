r"""Tensor algebras lie in the associative-algebra refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_tensor_algebra_is_associative() -> None:
    algebra = QQ.free_module(2).tensor_algebra()
    assert algebra in Algebras(QQ).Associative()
    assert algebra.associativity_decision() is True
