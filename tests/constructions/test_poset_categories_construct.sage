r"""Thin categories represented by owned partially ordered sets.

The chain ``0 < 1 < 2`` has exactly one arrow ``i -> j`` when ``i <= j`` and
none otherwise.  Composition is therefore forced by transitivity, while each
category object retains the underlying point of the ordered set.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _three_term_chain():
    labels = Sets.Δ[2]
    return PosetCategory(labels, le=lambda left, right: int(left) <= int(right))


def test_poset_category_objects_retain_their_values() -> None:
    category = _three_term_chain()
    zero, one, two = category(0), category(1), category(2)

    assert category in Cat()
    assert zero.value() == 0
    assert one.value() == 1
    assert two.value() == 2
    assert category.objects().cardinality() == cardinal(3)
    assert category.object_set().cardinality() == cardinal(3)


def test_poset_category_has_exactly_the_arrows_for_the_order_relation() -> None:
    category = _three_term_chain()
    zero, one, two = category(0), category(1), category(2)

    assert category.Mor(zero, zero).cardinality() == cardinal(1)
    assert category.Mor(zero, one).cardinality() == cardinal(1)
    assert category.Mor(zero, two).cardinality() == cardinal(1)
    assert category.Mor(one, two).cardinality() == cardinal(1)
    assert category.Mor(one, zero).cardinality() == cardinal(0)
    assert category.Mor(two, zero).cardinality() == cardinal(0)


def test_poset_category_identity_and_transitive_composition_are_the_unique_arrows() -> None:
    category = _three_term_chain()
    zero, one, two = category(0), category(1), category(2)
    zero_to_one = category.Mor(zero, one).an_element()
    one_to_two = category.Mor(one, two).an_element()
    zero_to_two = category.Mor(zero, two).an_element()
    identity = category.identity(zero)

    assert one_to_two * zero_to_one == zero_to_two
    assert zero_to_one * identity == zero_to_one
    assert identity * identity == identity
