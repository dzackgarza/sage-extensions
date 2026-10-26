r"""The theorem-backed localization/completion comparisons and their boundary."""

from sage_extensions.all import *


def test_maximal_adic_completion_agrees_before_and_after_localization() -> None:
    ring = QQ.polynomial_ring(("x", "y"))
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    maximal = ring.ideal(x, y)
    completion = ring.adic_completion(maximal, precision=6)
    comparison = completion.maximal_localization_comparison()
    local = comparison.local_ring()
    local_completion = comparison.local_completion()

    assert local.localized_prime() == maximal
    assert comparison.forward().domain() is completion
    assert comparison.forward().codomain() is local_completion
    assert comparison.inverse().domain() is local_completion
    assert comparison.inverse().codomain() is completion
    for generator in (x, y):
        source_image = completion.completion_map()(generator)
        local_image = local_completion.completion_map()(
            local.localization_map()(generator)
        )
        assert comparison.forward()(source_image) == local_image
        assert comparison.inverse()(local_image) == source_image


def test_inverting_the_adic_generator_before_completion_collapses_the_topology() -> None:
    ring = QQ.polynomial_ring(("t",))
    t = ring.algebra_generator("t")
    completion = ring.adic_completion(ring.ideal(t), precision=6)
    punctured = ring.localization(t)
    extended = ring.ideal(t).extension_to_localization(punctured)

    assert completion.zero() != completion.one()
    assert extended == punctured.ideal(punctured.one())
    collapsed = punctured.adic_completion(extended, precision=6)
    assert collapsed.zero() == collapsed.one()
    assert collapsed.completion_map_kernel() == extended


