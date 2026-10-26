r"""Polynomial algebras are free commutative algebras on their chosen generators."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_algebra_is_free_on_its_generating_module() -> None:
    module = QQ.free_module(("x", "y"))
    algebra = module.symmetric_algebra()
    x = algebra.algebra_generator("x")

    assert algebra in FreeAlgebras(QQ)
    assert algebra.is_free()
    assert algebra.generating_module() is module
    assert isinstance(x, algebra.ElementType)


def test_free_algebra_morphisms_have_identity() -> None:
    algebra = QQ.free_module(("x", "y")).symmetric_algebra()
    identity = algebra.Mor(algebra).identity()

    assert identity(algebra.algebra_generator("x")) == algebra.algebra_generator("x")
    assert identity * identity == identity

