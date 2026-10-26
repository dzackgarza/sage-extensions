r"""Polynomial rings are commutative associative unital algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_ring_lies_in_the_commutative_unital_associative_refinement() -> None:
    algebra = QQ["x"]
    category = Algebras(QQ).Associative().Unital().Commutative()

    assert algebra in category
    assert algebra.is_commutative()
    assert algebra.one() * algebra.algebra_generator("x") == algebra.algebra_generator("x")
