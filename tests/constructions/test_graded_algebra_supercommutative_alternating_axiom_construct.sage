r"""Exterior algebras are alternating as well as supercommutative."""

from sage_extensions.all import *  # noqa: F401,F403


def test_exterior_algebra_is_supercommutative_and_alternating() -> None:
    exterior = QQ.free_module(2).exterior_algebra()
    e0 = exterior.algebra_generator(0)

    assert exterior in GradedAlgebras(QQ).Supercommutative().Alternating()
    assert e0 * e0 == exterior.zero()

