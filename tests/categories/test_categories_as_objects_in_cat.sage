r"""A category is an object of Cat, with functors as its arrows."""

from sage_extensions.all import *


def test_a_category_answers_its_own_endomorphisms_as_an_object_of_cat():
    category = Sets()
    endomorphisms = category.End()
    identity = endomorphisms.identity()

    assert endomorphisms is Cat().Mor(category, category)
    assert identity.domain() is category
    assert identity.codomain() is category
    assert endomorphisms(identity) is identity


def test_cat_keeps_the_object_and_category_readings_of_mor():
    categories = Cat()
    target = Sets()

    assert categories.Mor(target) is Cat().Mor(categories, target)


def test_cat_contains_specialized_subcategories_of_functor_categories():
    r"""A specialized diagram category is a subcategory, hence an object, of Cat."""
    from sage_extensions.categories.group.groups import OwnedGroups

    index = PosetCategory(Sets.Δ[1])
    groups = OwnedGroups()
    directed = groups.DirectedSystem(index)
    inverse = groups.InverseSystem(index)

    assert Cat().Mor(index, groups) in Cat()
    assert directed.super_categories()[0] in MorCategories()
    assert directed in Cat()
    assert inverse in Cat()


def test_a_category_with_a_chosen_functor_retains_its_category_operations():
    r"""The two-object chain equipped with its identity functor is an object of Cat/I."""
    chain = PosetCategory(Sets.Δ[1])
    over = Cat().SliceOver(chain)
    selected = over(Cat().identity(chain))

    assert selected in over
    assert over.arrow(selected).domain() is chain
    assert over.arrow(selected).codomain() is chain
    assert selected.object_set().cardinality() == cardinal(2)
    first = selected(0)
    identity = selected.Mor(first, first).identity()
    assert identity.domain() is first
    assert identity.codomain() is first
    assert identity * identity == identity


def test_repeated_category_slice_enrichment_retains_each_functor_and_composition():
    r"""Each slice level retains its own chosen functor on the same category datum."""
    chain = PosetCategory(Sets.Δ[1])
    first_slice = Cat().SliceOver(chain)
    first_functor = Cat().identity(chain)
    once = first_slice(first_functor)

    second_slice = Cat().SliceOver(once)
    second_functor = Cat().identity(once)
    twice = second_slice(second_functor)

    assert twice in first_slice
    assert twice in second_slice
    assert first_slice.arrow(twice) is first_functor
    assert second_slice.arrow(twice) is second_functor
    first = twice(0)
    identity = twice.Mor(first, first).identity()
    assert identity * identity == identity
