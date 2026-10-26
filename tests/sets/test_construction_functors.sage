import pytest

from sage_extensions.all import *


def test_exponential_functor_is_contravariant_in_source_and_covariant_in_target() -> None:
    x = Sets.Δ[2]
    x_small = Sets.Δ[1]
    y = Sets.Δ[1]
    y_large = Sets.Δ[2]
    pre = Sets().Mono(x_small, x)(lambda value: x(value))
    post = Sets().Mono(y, y_large)(lambda value: y_large(value + 1))

    exponential = Sets().exponential_functor()
    source_pair = exponential.pair(x, y)
    target_pair = exponential.pair(x_small, y_large)
    map_pair = exponential.morphism(pre, post)
    source = exponential(source_pair)
    target = exponential(target_pair)
    carried = exponential(map_pair)

    f = source(lambda value: y(int(value) % 2))
    image = carried(f)
    assert image(x_small(0)) == y_large(1)
    assert image(x_small(1)) == y_large(2)
    assert carried.domain() is source
    assert carried.codomain() is target


def test_power_set_and_finite_power_set_functors_act_by_inverse_and_direct_image() -> None:
    source = Sets.Δ[3]
    target = Sets.Δ[1]
    quotient = Sets().Mor(source, target)(lambda value: target(int(value) % 2))

    inverse_power = Sets().inverse_image_power_set_functor()
    opposite = inverse_power.opposite_morphism(quotient)
    carried_inverse = inverse_power(opposite)
    odd = inverse_power(opposite.domain())({1})
    assert carried_inverse(odd) == inverse_power(opposite.codomain())({1, 3})

    finite_power = Sets().power_set_functor()
    carried_direct = finite_power(quotient)
    subset = finite_power(source)({0, 1, 2})
    assert carried_direct(subset) == finite_power(target)({0, 1})


def test_fixed_cardinality_subset_functor_is_defined_exactly_on_injections() -> None:
    source = Sets.Δ[2]
    target = Sets.Δ[4]
    inclusion = Sets().Mono(source, target)(lambda value: target(value + 1))
    pairs = Sets().fixed_cardinality_subset_functor(2)
    carried = pairs(inclusion)
    assert carried(pairs(source)({0, 2})) == pairs(target)({1, 3})

    noninjective = Sets().Mor(source, Sets.Δ[1])(lambda value: Sets.Δ[1](int(value) % 2))
    with pytest.raises(TypeError):
        pairs(noninjective)
