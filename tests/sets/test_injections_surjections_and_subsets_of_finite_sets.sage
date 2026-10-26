r"""Monomorphisms, epimorphisms, bijections and subsets in the category of finite sets.

In $\mathbf{Set}$ the monomorphisms are the injections and the epimorphisms
the surjections, and both classes are closed under composition.  A
bijection has an inverse.  The power set $P(X)$ is in bijection with the
characteristic maps $X \to \{0, 1\}$, so $|P(\{0, 1, 2, 3\})| = 2^4 = 16$;
the $2$-element subsets of a $4$-element set number $\binom{4}{2} = 6$; the
subset $\{x : x > 1\}$ of $\{0, 1, 2, 3\}$ has two points.  These are the
definitions.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_injections_compose_and_the_constant_map_is_not_one() -> None:
    r"""$x \mapsto 2x$ then $y \mapsto y + 1$ embeds $\{0, 1\}$ in $\{0, \dots, 4\}$ as $\{1, 3\}$."""
    two = Sets.Δ[1]
    four = Sets.Δ[3]
    five = Sets.Δ[4]
    doubling = Sets().Mono(two, four)(lambda x: four(2 * x))
    shift = Sets().Mono(four, five)(lambda x: five(x + 1))
    composite = shift * doubling

    assert doubling.is_injective()
    assert doubling.image().cardinality() == cardinal(2)
    assert composite.is_injective()
    assert composite(two(1)) == five(3)
    assert Sets().Mono(two, two).identity()(two(1)) == two(1)
    with pytest.raises(ValueError):
        Sets().Mono(two, four)(lambda _x: four(0))


def test_surjections_compose_and_parity_is_one() -> None:
    four = Sets.Δ[3]
    two = Sets.Δ[1]
    point = Sets.Δ[0]
    parity = Sets().Epi(four, two)(lambda x: two(x % 2))
    collapse = Sets().Epi(two, point)(lambda _x: point(0))

    assert parity.is_surjective()
    assert parity * Sets().Epi(four, four).identity() == parity
    assert (collapse * parity)(four(3)) == point(0)
    assert parity(four(3)) == two(1)


def test_a_rotation_of_three_points_has_the_inverse_rotation() -> None:
    three = Sets.Δ[2]
    rotation = Sets().Mor(three, three)(lambda x: three((x + 1) % 3))
    inverse = rotation.inverse()

    assert inverse(three(0)) == three(2)
    assert (inverse * rotation).is_identity()
    assert not rotation.is_identity()
    assert rotation.as_isomorphism()(three(2)) == three(0)


def test_finite_bijection_inverse_uses_codomain_positions() -> None:
    r"""A permutation with a nontrivial cycle has its exact inverse at every position."""
    five = Sets.Δ[4]
    permutation = (3, 4, 1, 0, 2)
    forward = Sets().Mor(five, five)(lambda x: five(permutation[int(x)]))
    backward = forward.inverse()

    for index in five:
        assert backward(forward(index)) == index
        assert forward(backward(index)) == index


def test_finite_image_cardinality_separates_injectivity_and_surjectivity() -> None:
    r"""Three points mapping onto two have a two-point image but no inverse."""
    domain = Sets.Δ[2]
    codomain = Sets.Δ[1]
    collapse = Sets().Mor(domain, codomain)(lambda point: codomain(int(point) % 2))

    assert collapse.image().cardinality() == cardinal(2)
    assert collapse.is_injective() is False
    assert collapse.is_surjective() is True
    with pytest.raises(AssertionError):
        collapse.inverse()


def test_injection_inverse_on_image_and_characteristic_are_compatible() -> None:
    r"""The inverse exists exactly on image points and characteristic values agree."""
    source = Sets.Δ[2]
    target = Sets.Δ[6]
    embedding = Sets().Mono(source, target)(lambda x: target(2 * x + 1))
    inverse = embedding.inverse_on_image()
    characteristic = embedding.characteristic_morphism()

    for point in source:
        assert inverse(embedding(point)) == point
    for point in target:
        assert characteristic(point) == Sets.Δ[1](int(int(point) in (1, 3, 5)))


def test_the_power_set_of_four_points_is_the_set_of_characteristic_maps() -> None:
    four = Sets.Δ[3]
    two = Sets.Δ[1]
    subsets = four.power_set()
    odd = Sets().Mor(four, two)(lambda x: two(x % 2))

    assert subsets.cardinality() == cardinal(16)
    assert subsets.from_characteristic_morphism(odd) == subsets({1, 3})
    assert subsets({1, 3}) in subsets
    assert four.finite_subsets().cardinality() == cardinal(16)


def test_the_two_element_subsets_of_four_points_number_six() -> None:
    pairs = Sets.Δ[3].subsets_of_size(2)

    assert pairs.cardinality() == cardinal(6)
    assert pairs({0, 1}) in pairs
    assert sum(1 for _pair in pairs) == 6


def test_the_points_of_zero_to_three_greater_than_one_are_two_and_three() -> None:
    four = Sets.Δ[3]
    large = Sets().condition_set(four, lambda x: x > 1)

    assert large.cardinality() == cardinal(2)
    assert set(large) == {four(2), four(3)}
