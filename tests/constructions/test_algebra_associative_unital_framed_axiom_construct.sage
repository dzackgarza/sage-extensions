r"""A symmetric algebra carries the framing inherited from its generators."""

from sage_extensions.all import *  # noqa: F401,F403


def test_symmetric_algebra_is_associative_unital_and_framed() -> None:
    module = QQ.free_module(("x", "y"))
    algebra = module.symmetric_algebra()

    assert algebra in Algebras(QQ).Associative().Unital().Framed()
    assert algebra in Modules(QQ).Framed()
    assert algebra.algebra_generator("x") == algebra(module.module_generator("x"))

