r"""A polynomial algebra on one variable is finitely generated as an algebra."""

from sage_extensions.all import *  # noqa: F401,F403


def test_one_variable_polynomial_algebra_is_finitely_generated_as_an_algebra() -> None:
    category = Algebras(QQ).Associative().Unital().FinitelyGeneratedAsAlgebra()
    algebra = QQ.polynomial_ring("x")
    resolutions = category.resolution_category()
    classifier = category.resolution_classifier()

    assert algebra in category
    assert algebra.is_finitely_generated_as_algebra()
    assert algebra.number_of_algebra_generators() == cardinal(1)
    assert classifier.domain() is resolutions
    assert classifier.codomain() is Algebras(QQ).Associative().Unital()
