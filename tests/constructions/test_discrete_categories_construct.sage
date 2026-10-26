r"""Represented discrete categories and the inherited category constructions.

The principal specimen is the discrete category on one object ``*``.  It has a
single morphism, the identity, and every finite diagram in it has the unique
possible limit and colimit.  That makes the inherited ``Cat`` operations
mathematically determined without adding any accidental structure.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _point_category():
    return DiscreteCategory(Sets()(("*",)))


def test_discrete_category_objects_retain_values_and_endpoint_mor() -> None:
    category = DiscreteCategory(Sets()(("p", "q")))
    p = category("p")
    q = category("q")

    assert category in DiscreteCategories()
    assert p.discrete_category() is category
    assert p.value() == "p"
    assert category.arrows().cardinality() == cardinal(2)
    assert category.arrows().value("p") == category.identity(p)
    assert category.arrows().value("q") == category.identity(q)
    assert p.Mor(p) is category.Mor(p, p)
    assert p.Mor(p).cardinality() == cardinal(1)
    assert p.Mor(q).cardinality() == cardinal(0)
    assert category.identity(p) * category.identity(p) == category.identity(p)


def test_discrete_category_morphism_packet_is_trivial_on_one_object() -> None:
    category = _point_category()
    star = category("*")
    packet = category.category_packet()

    assert packet.C() is category
    assert category.MorCategory().base_category() is category
    assert category.EndCategory().base_category() is category
    assert category.MonoCategory().base_category() is category
    assert category.EpiCategory().base_category() is category
    assert category.IsoCategory().base_category() is category
    assert category.AutCategory().base_category() is category
    assert category.Mor(star, star).cardinality() == cardinal(1)
    assert category.End(star).cardinality() == cardinal(1)
    assert category.Mono(star, star).cardinality() == cardinal(1)
    assert category.Epi(star, star).cardinality() == cardinal(1)
    assert category.Iso(star, star).cardinality() == cardinal(1)
    assert category.Aut(star).cardinality() == cardinal(1)


def test_discrete_category_arrow_core_and_structural_functors_are_trivial() -> None:
    category = _point_category()
    star = category("*")
    identity = star.Mor(star).identity()
    arrows = category.ArrowCategory()
    arrow = arrows(identity)
    core = category.Core()
    domain = category.domain_functor()
    codomain = category.codomain_functor()
    diagonal = category.diagonal_functor()
    diagonal_star = diagonal(star)

    assert arrow in arrows
    assert domain(arrow) is star
    assert codomain(arrow) is star
    assert diagonal_star.first() is star
    assert diagonal_star.second() is star
    assert core.Mor(star, star)(identity, identity) * core.Mor(star, star)(identity, identity) == core.identity(star)


def test_discrete_category_identity_inclusion_product_and_coproduct_functors_fix_the_only_object() -> None:
    category = _point_category()
    star = category("*")
    inclusion = category.inclusion_into(category)
    product = category.product_functor()
    coproduct = category.coproduct_functor()
    pair = product.domain()(star, star)

    assert inclusion.domain() is category
    assert inclusion.codomain() is category
    assert inclusion(star) is star
    assert product(pair) is star
    assert coproduct(pair) is star


def test_discrete_category_limit_and_colimit_categories_and_functors_fix_the_only_object() -> None:
    category = _point_category()
    star = category("*")
    diagrams = Cat().Mor(category, category)
    diagram = diagrams.constant_functor(star)
    diagram_object = diagrams(diagram)
    limits = category.Limits(category)
    colimits = category.Colimits(category)
    products = category.Products(category)
    coproducts = category.Coproducts(category)
    limit = category.limit_functor(category)
    colimit = category.colimit_functor(category)

    for constructions in (limits, colimits, products, coproducts):
        assert constructions.index_category() is category
        assert constructions.target_category() is category
    assert limit(diagram_object) is star
    assert colimit(diagram_object) is star


def test_discrete_category_universal_constructions_return_the_only_object() -> None:
    category = _point_category()
    star = category("*")
    identity = star.Mor(star).identity()
    product = category.product_construction((star, star))
    coproduct = category.coproduct_construction((star, star))
    equalizer = category.equalizer_construction(identity, identity)
    coequalizer = category.coequalizer_construction(identity, identity)

    assert isinstance(star, category.ObjectType)
    assert isinstance(category.ElementType, type)
    assert product.object() is star
    assert coproduct.object() is star
    assert equalizer.object() is star
    assert coequalizer.object() is star
    assert category.equalizer(identity, identity) is star
    assert category.coequalizer(identity, identity) is star
    assert category.equalizer_of_family((identity, identity)) is star
    assert category.coequalizer_of_family((identity, identity)) is star
    assert category.fiber_product(identity, identity) is star
    assert category.pushout(identity, identity) is star
    assert category.ProductCones((star, star)) in Cat()
    assert category.CoproductCocones((star, star)) in Cat()
    span = category.span(identity, identity)
    assert span.apex() is star
    assert span.left_leg() == identity
    assert span.right_leg() == identity


def test_discrete_category_universal_maps_are_the_forced_identities() -> None:
    category = _point_category()
    star = category("*")
    identity = star.Mor(star).identity()
    product = category.product_construction((star, star))
    coproduct = category.coproduct_construction((star, star))
    equalizer = category.equalizer_construction(identity, identity)
    coequalizer = category.coequalizer_construction(identity, identity)
    product_shape = product.diagram().domain()
    coproduct_shape = coproduct.diagram().domain()

    assert product.structure_morphism(product_shape(0)) == identity
    assert product.structure_morphism(product_shape(1)) == identity
    assert coproduct.costructure_morphism(coproduct_shape(0)) == identity
    assert coproduct.costructure_morphism(coproduct_shape(1)) == identity
    assert product.factor(product.cone()).apex_map() == identity
    assert coproduct.factor(coproduct.cocone()).apex_map() == identity
    assert equalizer.factor(equalizer.cone()).apex_map() == identity
    assert coequalizer.factor(coequalizer.cocone()).apex_map() == identity


def test_two_distinct_objects_of_a_discrete_category_have_no_product_or_coproduct() -> None:
    category = DiscreteCategory(Sets()(("p", "q")))
    p = category("p")
    q = category("q")

    with pytest.raises(ValueError, match="does not exist"):
        category.product((p, q))
    with pytest.raises(ValueError, match="does not exist"):
        category.coproduct((p, q))


def test_finite_constant_diagram_in_the_point_category_has_forced_limit_and_colimit() -> None:
    category = _point_category()
    star = category("*")
    identity = star.Mor(star).identity()
    shape = DiscreteCategory(Sets()(("i", "j")))
    diagrams = Cat().Mor(shape, category)
    diagram = diagrams.constant_functor(star)
    limit = category.Limits(shape).construction(diagram)
    colimit = category.Colimits(shape).construction(diagram)

    assert limit.object() is star
    assert colimit.object() is star
    for index in shape.objects():
        assert limit.structure_morphism(index) == identity
        assert colimit.costructure_morphism(index) == identity


def test_discrete_category_opposite_presheaves_and_yoneda_have_the_standard_shapes() -> None:
    category = _point_category()
    star = category("*")
    opposite = category.opposite()
    presheaves = category.presheaves()
    yoneda = category.yoneda_embedding()

    assert opposite in Cat()
    assert presheaves is Cat().Mor(opposite, Sets())
    assert yoneda.domain() is category
    assert yoneda.codomain() is presheaves
    assert yoneda(star) in presheaves


def test_discrete_category_arrow_subcategories_all_contain_the_unique_identity() -> None:
    category = _point_category()
    star = category("*")
    identity = star.Mor(star).identity()
    arrows = category.ArrowCategory()
    arrow = arrows(identity)
    wide = category.WideSubcategory(category.MonomorphismArrowCategory())

    assert arrow in category.EndArrowCategory()
    assert arrow in category.IsoArrowCategory()
    assert arrow in category.AutomorphismArrowCategory()
    assert arrow in category.MonomorphismArrowCategory()
    assert arrow in category.EpimorphismArrowCategory()
    assert arrow in wide


def test_discrete_category_slice_like_categories_retain_the_only_base_object() -> None:
    category = _point_category()
    star = category("*")

    assert category.SliceOver(star).base_object() is star
    assert category.CosliceUnder(star).base_object() is star
    assert category.SubobjectCategory(star).base_object() is star
    assert category.SuperobjectCategory(star).base_object() is star
    assert category.CoveringObjectCategory(star).base_object() is star
    assert category.CoveredObjectCategory(star).base_object() is star
    assert category.Subobjects(star).base_object() is star
    assert category.Superobjects(star).base_object() is star
    assert category.CoveringObjects(star).base_object() is star
    assert category.CoveredObjects(star).base_object() is star
