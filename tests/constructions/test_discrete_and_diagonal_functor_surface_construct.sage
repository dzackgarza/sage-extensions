r"""Discrete, constant, and diagonal functors retain their defining data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_discrete_functor_retains_its_object_map() -> None:
    source = DiscreteCategory(Sets.Δ[1])
    target = DiscreteCategory(Sets.Δ[1])
    swap = Sets().Mor(source.object_set(), target.object_set())(
        lambda point: target.object_set()(1 - int(point))
    )
    functor = Cat().Mor(source, target).from_object_map(swap)

    assert functor.object_map() is swap
    assert functor(source(0)) is target(1)


def test_constant_functor_retains_its_constant_value() -> None:
    index = DiscreteCategory(Sets.Δ[1])
    value = Sets.Δ[0]
    functor = Cat().Mor(index, Sets()).constant_functor(value)

    assert functor.constant_value() is value
    assert functor(index(0)) is value


def test_diagonal_functor_retains_its_product_category() -> None:
    diagonal = Sets().diagonal_functor()
    points = Sets.Δ[1]

    assert diagonal.product_category() is diagonal.codomain()
    assert diagonal(points).first() is points
    assert diagonal(points).second() is points
