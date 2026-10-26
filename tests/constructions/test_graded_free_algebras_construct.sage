r"""A polynomial algebra is free and graded by total degree."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_polynomial_algebra_has_the_expected_free_grading() -> None:
    module = QQ.free_module(("x", "y"))
    algebra = module.symmetric_algebra()
    x = algebra.algebra_generator("x")

    assert algebra in GradedFreeAlgebras(QQ)
    assert algebra.degree_on_module_generator(module.module_generator("x")) == 1
    assert algebra.from_graded_piece(1, module.module_generator("x")) == x
    assert algebra.graded_piece(2).module_rank() == 3
    assert algebra.graded_piece_monomials(2).cardinality() == cardinal(3)
    assert algebra.ideal_generators_in_degree((x,), 2).cardinality() == cardinal(2)

