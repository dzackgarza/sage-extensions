import pytest

from sage_extensions.all import *


def three():
    return Sets.Δ[2]


def power():
    return three().power_set()


def test_every_subset_of_a_finite_set_is_finite() -> None:
    assert three().finite_subsets() == power()


def test_the_subobjects_of_a_finite_set_are_its_subsets() -> None:
    assert Sets().Subobjects(three()).cardinality() == power().cardinality()


def test_subsets_are_characteristic_maps() -> None:
    r"""$\mathcal P(X) \cong \operatorname{Hom}(X, \{0, 1\})$."""
    assert Sets.Δ[1].exponential(three()).cardinality() == power().cardinality()


def test_the_categories_of_the_power_set() -> None:
    assert power() in Sets()
    assert power() in FiniteSets()
    unrefined = Sets().condition_set(three(), lambda point: True)
    assert unrefined.is_finite() is True
    assert unrefined.power_set() in FiniteSets()


def test_the_power_set_has_two_to_the_three_elements() -> None:
    assert power().cardinality() == 8
    assert power().power_set().cardinality() == 256


def test_the_boolean_operations() -> None:
    subsets = power()
    points = three()
    pair = subsets((points(0), points(1)))
    assert pair in subsets
    assert pair.cardinality() == 2
    assert pair.complement().cardinality() == 1
    assert pair.union(pair.complement()) == subsets.top()
    assert pair.intersection(pair.complement()) == subsets.bottom()
    assert subsets.top().cardinality() == 3
    assert subsets.bottom().cardinality() == 0


def test_the_subsets_of_a_given_size() -> None:
    r"""$\binom{3}{0} = 1$, $\binom{3}{2} = 3$, $\binom{3}{3} = 1$."""
    points = three()
    assert points.subsets_of_size(0).cardinality() == 1
    assert points.subsets_of_size(2).cardinality() == 3
    assert points.subsets_of_size(3).cardinality() == 1


def test_subset_cardinality_must_be_a_natural_number() -> None:
    points = three()
    for invalid in (-1, QQ(3) / QQ(2)):
        with pytest.raises(ValueError):
            points.subsets_of_size(invalid)


def test_the_power_set_has_one_endomorphism_category() -> None:
    subsets = power()
    endomorphisms = subsets.Mor(subsets)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert subsets.Mor(subsets) is endomorphisms
    assert identity * identity == identity


def test_empty_codomain_exponential_needs_known_nonempty_domain() -> None:
    empty = Sets.Δ[-1]
    assert empty.exponential(empty).cardinality() == 1
    assert empty.exponential(Sets.Δ[0]).cardinality() == 0
    unknown = Sets().condition_set(NN, lambda point: True)
    assert unknown not in Sets().Finite()
    assert unknown not in Sets().Infinite()
    undecided = empty.exponential(unknown)
    assert undecided in Sets()
    assert undecided in Sets().Finite()
    assert undecided not in Sets().Infinite()
    with pytest.raises(AssertionError):
        undecided.cardinality()
