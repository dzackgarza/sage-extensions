r"""Tensor algebras are associative unital algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_tensor_algebra_is_associative_and_unital() -> None:
    algebra = QQ.free_module(2).tensor_algebra()
    category = Algebras(QQ).Associative().Unital()

    assert algebra in category
    assert algebra.associativity_decision() is True
    assert algebra.unit_laws_decision() is True
