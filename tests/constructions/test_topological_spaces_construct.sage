r"""Finite topological spaces and continuous maps.

The Sierpiński space on ``{0,1}`` has opens ``∅``, ``{1}``, and the whole
space.  Swapping ``0`` and ``1`` is therefore a map of the underlying set but
is not continuous, since the inverse image of the open singleton ``{1}`` is
the non-open singleton ``{0}``.  This separates the topological Mor from its
explicit underlying-set Mor.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _sierpinski_space():
    points = Sets.Δ[1]
    return TopologicalSpaces()(points, ((), (points(1),), points))


def test_sierpinski_space_retains_its_underlying_set_and_topology() -> None:
    space = _sierpinski_space()
    power = space.power_set()
    empty = power(())
    zero = power((space(0),))
    one = power((space(1),))
    whole = power((space(0), space(1)))

    assert space in TopologicalSpaces()
    assert space in Sets()
    assert space.unstructured_set() is space.underlying_set()
    assert space.unstructured_set().cardinality() == cardinal(2)
    assert space.open_subsets().cardinality() == cardinal(3)
    assert space.topology() == space.open_subsets()
    assert space.is_open_subset(empty)
    assert not space.is_open_subset(zero)
    assert space.is_open_subset(one)
    assert space.is_open_subset(whole)
    assert isinstance(space(0), space.ElementType)


def test_topological_space_inherits_set_constructions_on_its_points() -> None:
    space = _sierpinski_space()
    two = Sets.Δ[1]
    point = Sets.Δ[0]

    assert space.cardinality() == cardinal(2)
    assert space.counting_well_order().cardinality() == cardinal(2)
    assert space.condition_set(lambda x: x == space(1)).cardinality() == cardinal(1)
    assert space.power_set().cardinality() == cardinal(4)
    assert space.exponential(point).cardinality() == cardinal(2)
    assert space.product_with(two).cardinality() == cardinal(4)
    assert space.coproduct_with(two).cardinality() == cardinal(4)
    assert space.subsets_of_size(1).cardinality() == cardinal(2)
    assert space.finite_subsets().cardinality() == cardinal(4)
    assert space.finite_words().cardinality() == aleph0
    assert space.finite_multisets().cardinality() == aleph0


def test_topological_image_set_uses_an_explicit_underlying_set_map() -> None:
    space = _sierpinski_space()
    underlying = space.Mor(space, category=Sets())(lambda _x: space(1))
    image = space.image_set(underlying)

    assert underlying in Sets().Mor(space, space)
    assert image.cardinality() == cardinal(1)
    assert space(1) in image


def test_topological_endpoint_mor_preserves_continuity_unless_sets_are_requested() -> None:
    space = _sierpinski_space()
    continuous = space.Mor(space)
    coarse = space.Mor(space, category=Sets())
    constant = space.continuous_map(space, lambda _x: space(1))
    swap = lambda x: space(1) if x == space(0) else space(0)

    assert continuous is TopologicalSpaces().Mor(space, space)
    assert coarse is Sets().Mor(space, space)
    assert constant in continuous
    assert constant.underlying_set_morphism().domain() is space
    assert constant.underlying_set_morphism().codomain() is space
    assert constant(space(0)) == space(1)
    assert coarse(swap)(space(0)) == space(1)
    with pytest.raises(ValueError):
        continuous(swap)


def test_continuous_maps_have_identity_equality_and_composition() -> None:
    space = _sierpinski_space()
    mor = space.Mor(space)
    identity = mor.identity()
    constant = mor(lambda _x: space(1))
    same_constant = mor(lambda _x: space(1))

    assert identity(space(0)) == space(0)
    assert identity * identity == identity
    assert identity * constant == constant
    assert constant * identity == constant
    assert constant == same_constant
    assert constant != identity
