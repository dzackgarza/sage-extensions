r"""Finite subobject operations retain undecidable characteristic predicates."""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.logic import AtomicProposition


def test_finite_subobject_boolean_operations_retain_propositions() -> None:
    ambient = Sets.Δ[1]
    subsets = ambient.power_set()
    unknown = subsets.from_predicate(
        lambda member: AtomicProposition("unknown_subset_membership", member)
    )
    empty = subsets.from_predicate(lambda _member: False)
    full = subsets.from_predicate(lambda _member: True)

    assert unknown.intersection(full).is_parent_of(ambient(0)) is not False
    assert unknown.union(empty).is_parent_of(ambient(0)) is not False
    assert unknown.difference(empty).is_parent_of(ambient(0)) is not False
    assert unknown.complement().is_parent_of(ambient(0)) is not False
    assert unknown.symmetric_difference(empty).is_parent_of(ambient(0)) is not False
    assert (unknown <= full) is True
    assert (unknown <= unknown) is True
    assert (empty <= unknown) is True
    assert (unknown <= empty) is not True
    assert (unknown == full) is not True
    # Equalities and inclusions are characteristic propositions, not
    # Boolean coercions of a membership computation still undecided.
    assert (unknown == empty) is not True
    assert (full <= unknown) is not False
    assert (empty == full) is False


def test_characteristic_morphism_requires_actual_set_arrow_endpoints() -> None:
    ambient = Sets.Δ[1]
    subsets = ambient.power_set()
    truth = Sets.Δ[1]
    characteristic = Sets().Mor(ambient, truth)(lambda value: truth(int(value)))
    selected = subsets.from_characteristic_morphism(characteristic)
    assert selected.is_parent_of(ambient(0)) is False
    assert selected.is_parent_of(ambient(1)) is True
    wrong = Sets().Mor(Sets.Δ[0], truth)(lambda _value: truth(1))
    try:
        subsets.from_characteristic_morphism(wrong)
    except ValueError:
        pass
    else:
        raise AssertionError("characteristic map admitted with a different source set")
