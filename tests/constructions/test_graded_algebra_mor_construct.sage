r"""Graded algebra Mor objects contain degree-preserving identities."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_graded_algebra_identity_preserves_degree() -> None:
    algebra = QQ.free_module(("x", "y")).symmetric_algebra()
    identity = GradedAlgebras(QQ).Mor(algebra, algebra).identity()
    x = algebra.algebra_generator("x")

    assert identity.domain() is algebra
    assert identity.codomain() is algebra
    assert identity(x) == x
    assert identity(x).degree() == x.degree()
    assert identity * identity == identity

