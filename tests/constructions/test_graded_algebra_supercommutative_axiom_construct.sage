r"""Exterior algebras satisfy the graded supercommutativity sign rule."""

from sage_extensions.all import *  # noqa: F401,F403


def test_exterior_algebra_is_supercommutative() -> None:
    exterior = QQ.free_module(2).exterior_algebra()
    e0 = exterior.algebra_generator(0)
    e1 = exterior.algebra_generator(1)

    assert exterior in GradedAlgebras(QQ).Supercommutative()
    assert e0 * e1 == -(e1 * e0)

