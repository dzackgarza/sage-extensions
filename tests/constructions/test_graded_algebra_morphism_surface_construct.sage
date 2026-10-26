r"""A graded-algebra identity retains its underlying algebra map and grading law."""

from sage_extensions.all import *  # noqa: F401,F403


def _symmetric_algebra_identity():
    algebra = QQ.free_module(("x", "y")).symmetric_algebra()
    identity = GradedAlgebras(QQ).Mor(algebra, algebra).identity()
    return algebra, identity


def test_graded_algebra_identity_retains_underlying_algebra_morphism() -> None:
    algebra, identity = _symmetric_algebra_identity()
    underlying = identity.underlying_algebra_morphism()
    x = algebra.algebra_generator("x")

    assert underlying.domain() is algebra
    assert underlying.codomain() is algebra
    assert underlying(x) == x
    assert identity.degree_preservation_decision() is True


def test_graded_algebra_identity_composition_retains_degree_preservation() -> None:
    algebra, identity = _symmetric_algebra_identity()
    composite = identity * identity
    x = algebra.algebra_generator("x")

    assert composite.domain() is algebra
    assert composite.codomain() is algebra
    assert composite(x) == x
    assert composite.degree_preservation_decision() is True
    assert composite.underlying_algebra_morphism()(x) == x
