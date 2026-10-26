r"""Direct and inverse images of subsets along maps of sets."""

from sage_extensions.all import *
from sage_extensions.categories.sets.set_categories import (
    FinitePowerSets, FixedCardinalitySubsetSets,
)


def test_powerset_of_the_naturals_is_uncountable_but_finite_subsets_are_countable() -> None:
    powerset = NN.power_set()
    finite_subsets = NN.finite_subsets()

    assert powerset in UncountableSets()
    assert powerset not in EnumeratedSets()
    assert powerset not in FiniteSets()
    assert finite_subsets in CountablyInfiniteSets()
    assert finite_subsets in EnumeratedSets()
    assert finite_subsets.cardinality() == aleph0
    for size in (1, 2, 3):
        subsets = NN.subsets_of_size(size)
        assert subsets in CountablyInfiniteSets()
        assert subsets in EnumeratedSets()
        assert subsets.cardinality() == aleph0


def test_subset_family_constructors_require_a_set_source() -> None:
    source = Sets.Δ[2]
    assert FinitePowerSets()(source) in Sets()
    assert FixedCardinalitySubsetSets()(source, 0) in Sets()
    nonset = object()
    for constructor in (
        lambda: FinitePowerSets()(nonset),
        lambda: FixedCardinalitySubsetSets()(nonset, 0),
    ):
        try:
            constructor()
        except ValueError:
            pass
        else:
            raise AssertionError("subset family constructed on a non-set source")


def test_finite_subobject_boolean_operations_retain_the_ambient_inclusion() -> None:
    r"""Union, meet and complement are subobjects of the same three-point set."""
    ambient = Sets.Δ[2]
    subsets = ambient.power_set()
    left = subsets((ambient(0),))
    right = subsets((ambient(1),))
    results = (
        (left.union(right), 2),
        (left.intersection(right), 0),
        (left.difference(right), 1),
        (left.symmetric_difference(right), 2),
        (left.complement(), 2),
    )
    for result, size in results:
        assert result.cardinality() == size
        assert result.inclusion().codomain() is ambient
        assert result in Sets().Finite()
    assert ambient.intersection(ambient).cardinality() == 3


def test_inverse_and_direct_image_form_the_set_subobject_galois_connection() -> None:
    source = Sets.Δ[5]
    target = Sets.Δ[2]
    residue = Sets().Mor(source, target)(lambda n: target(int(n) % 3))
    source_subsets = source.power_set()
    target_subsets = target.power_set()
    selected = source_subsets({0, 1, 3, 4})
    upper_bound = target_subsets({0, 1})

    direct = source_subsets.direct_image_morphism(residue)
    inverse = target_subsets.inverse_image_morphism(residue)
    assert direct(selected) == target_subsets({0, 1})
    assert direct(selected) <= upper_bound
    assert selected <= inverse(upper_bound)








def test_power_set_functors_transport_a_nonidentity_injection_both_ways() -> None:
    source = Sets.Δ[1]
    target = Sets.Δ[2]
    injection = Sets().Mor(source, target)(
        lambda point: target(0) if point == source(0) else target(2)
    )

    direct = Sets().power_set_functor()(injection)
    selected = source.finite_subsets()({source(0), source(1)})
    assert direct(selected) == target.finite_subsets()({target(0), target(2)})

    inverse_functor = Sets().inverse_image_power_set_functor()
    opposite = inverse_functor.opposite_morphism(injection)
    inverse = inverse_functor(opposite)
    assert inverse(target.power_set()({target(2)})) == source.power_set()({source(1)})
