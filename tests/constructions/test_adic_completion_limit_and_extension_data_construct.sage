r"""An adic completion retains its inverse system, limit cone, precision, and ideal extensions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_origin_completion_retains_limit_and_precision_data() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    maximal = ring.ideal(x, y)
    completion = ring.adic_completion(maximal, precision=5)
    system = completion.adic_inverse_system()
    cone = completion.adic_limit_cone()
    limit = completion.adic_limit_construction()

    assert completion.computation_precision() == 5
    assert system.functor().completion() is completion
    assert cone.apex() is completion
    assert limit.object() is completion
    assert limit.factor(cone).apex_map() == completion.Mor(completion).identity()


def test_origin_completion_retains_ideal_extension_data() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    maximal = ring.ideal(x, y)
    completion = ring.adic_completion(maximal, precision=5)
    extension = completion.ideal_extension()
    truncation_extension = completion.truncation_ideal_extension(2)

    assert extension.source_ideal() is maximal
    assert extension.morphism() is completion.completion_map()
    assert extension.extended_ideal() == completion.extended_ideal()
    assert truncation_extension.source_ideal() is maximal
    assert truncation_extension.morphism().codomain() is completion.adic_truncation(2)


def test_completion_matches_completion_after_maximal_localization() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    completion = ring.adic_completion(ring.ideal(x, y), precision=6)
    comparison = completion.maximal_localization_comparison()

    assert comparison.forward().domain() is completion
    assert comparison.inverse().codomain() is completion
