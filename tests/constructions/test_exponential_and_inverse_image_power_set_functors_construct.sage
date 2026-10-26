r"""Set exponentials and power sets have their standard functorial actions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_exponential_bifunctor_on_two_and_three_points_has_nine_functions() -> None:
    exponentials = Sets().exponential_functor()
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    pair = exponentials.pair(two, three)

    assert exponentials(pair) is three.exponential(two)
    assert exponentials(pair).cardinality() == cardinal(9)


def test_inverse_image_power_set_functor_pulls_a_subset_back_along_an_injection() -> None:
    power = Sets().inverse_image_power_set_functor()
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    inclusion = Sets().Mor(two, three)(lambda point: three(int(point)))
    inverse_image = power(power.opposite_morphism(inclusion))
    chosen = three.power_set()((three(0), three(2)))
    pulled_back = inverse_image(chosen)

    assert pulled_back.cardinality() == cardinal(1)
    assert two(0) in pulled_back
    assert two(1) not in pulled_back
