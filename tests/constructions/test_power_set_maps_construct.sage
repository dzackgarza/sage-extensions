r"""Power sets classify subsets and carry direct and inverse image maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_predicates_and_characteristic_maps_classify_subsets() -> None:
    three = Set((1, 2, 3))
    power = three.power_set()
    selected = power.from_predicate(lambda value: value > 1)
    truth = power.truth_values()
    characteristic = power.characteristic_mor()(
        lambda value: truth(1) if value > 1 else truth(0)
    )
    classified = power.from_characteristic_morphism(characteristic)

    assert selected.cardinality() == cardinal(2)
    assert classified.cardinality() == cardinal(2)
    assert three(2) in classified
    assert three(3) in classified
    assert three(1) not in classified
    comparison = power.cardinality_comparison()
    assert comparison.domain() == cardinal(8)
    assert comparison.codomain() == cardinal(8)


def test_direct_and_inverse_images_of_subsets() -> None:
    three = Set((1, 2, 3))
    two = Sets.Δ[1]
    morphism = Sets().Mor(three, two)(
        lambda value: two(0) if value in (three(1), three(2)) else two(1)
    )
    source_power = three.power_set()
    target_power = two.power_set()
    source_subset = source_power((three(1), three(3)))
    target_singleton = target_power((two(1),))

    direct = source_power.direct_image_morphism(morphism)(source_subset)
    inverse = target_power.inverse_image_morphism(morphism)(target_singleton)

    assert direct.cardinality() == cardinal(2)
    assert inverse.cardinality() == cardinal(1)
    assert three(3) in inverse
