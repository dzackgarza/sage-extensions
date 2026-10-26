r"""The class set of a small category is the quotient of source and target.

In a groupoid it is the isomorphism-class set. These specimens retain the
selected quotient projection and factorization instead of counting classes
from an unrelated chosen list of representatives.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.abstract_categories.products import PosetCategory
from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set


def test_poset_category_has_two_components_with_their_quotient_projection() -> None:
    poset = PosetCategory(
        finite_ordered_set((0, 1, 2)),
        le=lambda source, target: source == target or (source == 0 and target == 1),
    )
    construction = poset.class_set_construction()
    classes = construction.object()
    diagram = construction.diagram()
    projection = construction.costructure_morphism(diagram.domain().target())

    assert classes in FiniteSets()
    assert classes.cardinality() == cardinal(2)
    assert poset.class_set() is classes
    assert projection.domain().cardinality() == cardinal(3)
    assert projection(poset(0)) == projection(poset(1))
    assert projection(poset(0)) != projection(poset(2))

    binary = Sets.Δ[1]
    classifier = Sets().Mor(projection.domain(), binary)(
        lambda obj: binary(0 if obj is poset(0) or obj is poset(1) else 1)
    )
    cocone = diagram.Cocones().cocone(
        binary,
        lambda vertex: classifier * diagram.left()
        if vertex is diagram.domain().source() else classifier,
    )
    factor = construction.factor(cocone).apex_map()
    assert all(factor(projection(obj)) == classifier(obj) for obj in projection.domain())


def test_discrete_category_components_are_the_objects() -> None:
    category = DiscreteCategory(finite_ordered_set(("a", "b")))
    classes = category.class_set()
    construction = category.class_set_construction()
    projection = construction.costructure_morphism(
        construction.diagram().domain().target()
    )

    assert classes is construction.object()
    assert classes.cardinality() == cardinal(2)
    assert projection(category("a")) != projection(category("b"))


def test_classifying_groupoid_has_one_class_even_for_an_infinite_group() -> None:
    group = Groups.Free(1)
    groupoid = group.classifying_category()
    construction = groupoid.class_set_construction()
    classes = construction.object()
    diagram = construction.diagram()
    projection = construction.costructure_morphism(diagram.domain().target())

    assert diagram.left().domain() is groupoid.arrows()
    assert classes.cardinality() == cardinal(1)
    assert projection(groupoid.object()) == classes.an_element()
    assert groupoid.object() in groupoid.object_set()
