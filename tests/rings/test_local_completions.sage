r"""Adic completions as limits of their finite truncations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_multivariable_origin_completion_is_not_truncated_by_computation_precision() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    completion = plane.adic_completion(plane.ideal(x, y), precision=4)

    xhat = completion.completion_map()(x)
    yhat = completion.completion_map()(y)
    assert xhat**4 != completion.zero()
    assert yhat**4 != completion.zero()
    fourth = completion.adic_projection(4)
    fifth = completion.adic_projection(5)
    assert fourth(xhat**4) == fourth.codomain().zero()
    assert fifth(xhat**4) != fifth.codomain().zero()
    assert completion.computation_precision() == 4


def test_completion_is_the_limit_of_the_truncations_by_powers_of_the_maximal_ideal() -> None:
    r"""R-hat = lim R/m^n for R = Q[x,y], m = (x,y): the transition R/m^4 -> R/m^2 keeps
    x and kills x^2 and xy, pi_2 = t_{4,2} pi_4, and the limit of the projections is
    the completion itself (Atiyah-Macdonald ch. 10)."""
    plane = QQ['x,y']
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    completion = plane.adic_completion(plane.ideal(x, y), precision=5)
    fourth = completion.adic_truncation(4)
    second = completion.adic_truncation(2)
    transition = completion.adic_transition_map(4, 2)

    assert transition(fourth.quotient_map()(x)) == second.quotient_map()(x)
    assert transition(fourth.quotient_map()(x)) != second.zero()
    assert transition(fourth.quotient_map()(x**2)) == second.zero()
    assert transition(fourth.quotient_map()(x * y)) == second.zero()
    assert fourth.quotient_map()(x**3) != fourth.zero()
    assert transition * completion.adic_projection(4) == completion.adic_projection(2)

    limit = completion.adic_limit_construction()
    assert limit.object() is completion
    assert limit.factor(limit.cone()).apex_map() == completion.Mor(completion).identity()
