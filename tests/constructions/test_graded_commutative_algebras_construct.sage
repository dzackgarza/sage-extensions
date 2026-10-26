r"""Exterior algebras satisfy graded commutativity."""

from sage_extensions.all import *  # noqa: F401,F403


def test_exterior_algebra_is_graded_commutative() -> None:
    exterior = QQ.free_module(2).exterior_algebra()
    e0 = exterior.algebra_generator(0)
    e1 = exterior.algebra_generator(1)

    assert exterior in GradedCommutativeAlgebras(QQ)
    assert e0 * e1 == -(e1 * e0)

