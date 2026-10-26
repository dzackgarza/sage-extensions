r"""Algebra Mor objects contain the multiplication-preserving identity."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_algebra_mor_identity_preserves_product_and_unit() -> None:
    algebra = QQ.polynomial_ring("x")
    x = algebra.algebra_generator("x")
    identity = algebra.Mor(algebra).identity()

    assert identity.domain() is algebra
    assert identity.codomain() is algebra
    assert identity(x * x) == x * x
    assert identity(algebra.one()) == algebra.one()
    assert identity * identity == identity

