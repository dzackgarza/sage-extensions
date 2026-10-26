r"""Tensor algebras lie in the unital-algebra refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_tensor_algebra_is_unital() -> None:
    algebra = QQ.free_module(2).tensor_algebra()
    assert algebra in Algebras(QQ).Unital()
    assert algebra.unit_laws_decision() is True
    assert algebra.one() * algebra.algebra_generator(0) == algebra.algebra_generator(0)
