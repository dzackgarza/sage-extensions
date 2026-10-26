r"""The Hölder-graded Lebesgue algebra exposes its projections, integral form, pairing, and null quotient."""

from sage_extensions.all import *  # noqa: F401,F403


def test_degree_and_unit_piece_projections() -> None:
    algebra = GradedLebesgueAlgebra
    square_integrable = Lp(2, RR, RR)
    g(t) = exp(-t^2)
    gaussian = algebra(square_integrable(g))

    assert algebra.degree_projection(QQ(1) / 2)(gaussian)(0) == 1
    assert algebra.degree_projection(1)(gaussian) == Lp(1, RR, RR).zero()
    assert algebra.unit_piece_projection()(algebra.one())(5) == 1


def test_integral_form_and_pairing_on_gaussian() -> None:
    algebra = GradedLebesgueAlgebra
    square_integrable = Lp(2, RR, RR)
    g(t) = exp(-t^2)
    gaussian = algebra(square_integrable(g))
    pairing_morphism = algebra.integral_pairing_morphism()
    pairing = algebra.integral_pairing()

    assert algebra.integral_form()(gaussian * gaussian) == sqrt(pi / 2)
    assert algebra.integral_form()(gaussian) == 0
    tensor = algebra.tensor_square().pure_tensor(gaussian, gaussian)
    assert pairing_morphism(tensor) == sqrt(pi / 2)
    assert pairing(gaussian, gaussian) == sqrt(pi / 2)


def test_null_function_quotient_is_graded_by_quotient_lebesgue_spaces() -> None:
    quotient = GradedLebesgueAlgebra.quotient_by_null_functions()

    assert quotient in LebesgueGradedModules(RR)
    assert quotient.graded_piece(QQ(1) / 2) is Lp(2, RR, RR).quotient_by_null_functions()
    assert quotient.graded_piece(1) is Lp(1, RR, RR).quotient_by_null_functions()
