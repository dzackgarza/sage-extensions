r"""Adic completions: separation, locality, finite length and induced maps."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_completion_of_the_dual_numbers_at_their_nilpotent_ideal_is_injective() -> None:
    r"""For A = Q[e]/(e^2) and I = (e), I^2 = 0, so A is I-adically complete: the
    completion map is injective, e-hat != 0 and e-hat^2 = 0."""
    line = QQ['e']
    e = line.algebra_generator("e")
    dual = line.quotient_by_relations((e**2,))
    ebar = dual.algebra_generator("e")
    completion = dual.adic_completion(dual.ideal(ebar), precision=3)
    e_hat = completion.completion_map()(ebar)

    assert completion.completion_map_kernel() == dual.ideal(dual.zero())
    assert completion.is_adically_separated()
    assert e_hat != completion.zero()
    assert e_hat**2 == completion.zero()


def test_completion_at_an_idempotent_ideal_is_the_quotient_and_is_not_separated() -> None:
    r"""For A = Q[e]/(e^2 - e) = Q x Q and I = (e), I^n = I for all n, so the I-adic
    completion is A/I = Q: its kernel is I (Krull's intersection theorem fails for a
    ring with idempotents), and it is a complete local ring."""
    line = QQ['e']
    e = line.algebra_generator("e")
    product = line.quotient_by_relations((e**2 - e,))
    ebar = product.algebra_generator("e")
    ideal = product.ideal(ebar)
    completion = product.adic_completion(ideal, precision=3)

    assert ideal.power(2) == ideal
    assert completion.completion_map_kernel() == ideal
    assert not completion.is_adically_separated()
    assert completion.completion_map()(ebar) == completion.zero()
    assert completion.completion_map()(1 - ebar) == completion.one()
    assert completion in CompleteLocalRings()


def test_nonmaximal_adic_completion_is_complete_but_not_declared_local() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    completion = plane.adic_completion(plane.ideal(x))

    assert completion not in CompleteLocalRings()
    assert completion not in LocalRings()
    assert completion.extended_ideal().ring() is completion


def test_artin_name_requires_finite_length() -> None:
    line = QQ.polynomial_ring(("x",))
    x = line.algebra_generator("x")
    line_completion = line.adic_completion(line.ideal(x))
    assert line_completion.adic_artin_truncation(3) in ArtinianRings()

    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    nonmaximal = plane.adic_completion(plane.ideal(x))
    with pytest.raises(ValueError):
        nonmaximal.adic_artin_truncation(3)


def test_a_ring_map_carrying_the_ideal_into_the_ideal_induces_a_map_of_completions() -> None:
    r"""f: Q[x] -> Q[x], x -> x^2 satisfies f((x)) in (x), so it induces
    Q[[x]] -> Q[[x]] with x -> x^2, and its square sends x to x^4; x -> 1 does not
    carry (x) into (x) and induces no continuous map (Atiyah-Macdonald ch. 10)."""
    line = QQ['x']
    x = line.algebra_generator("x")
    completion = line.adic_completion(line.ideal(x))
    x_hat = completion.completion_map()(x)

    induced = completion.induced_map(line.Mor(line)({"x": x**2}), completion)
    assert induced(x_hat) == x_hat**2
    assert induced(induced(x_hat)) == x_hat**4
    assert induced(1 - x_hat) * completion.completion_map()(1 + x**2) == completion.one() - x_hat**4
    assert completion.induced_map(line.Mor(line).identity(), completion).is_identity()

    with pytest.raises(ValueError):
        completion.induced_map(line.Mor(line)({"x": line.one()}), completion)
