r"""Fixed-endpoint Mor categories as categories of represented arrows.

For the singleton set ``*``, ``Mor_Set(*,*)`` has one object, the identity
map.  Its represented 2-Mor is therefore the one-object discrete category:
the only 2-cell is the identity.  This terminal specimen fixes the values of
all finite universal constructions inherited from ``Cat`` without assuming
that every Mor category is discrete; functor categories, for example, have
natural transformations as their morphisms.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _singleton_end_category():
    point = Sets.Δ[0]
    return point, Sets().End(point)


def _identity_object():
    point, end = _singleton_end_category()
    identity = end.identity()
    return point, end, identity, end(identity)


def test_fixed_mor_category_retains_family_endpoints_and_underlying_mor() -> None:
    point, end, identity, arrow = _identity_object()

    assert end in MorCategories()
    assert end in Cat()
    assert end.base_category() is Sets()
    assert end.domain_object() is point
    assert end.codomain_object() is point
    assert end.arrow_set() is Sets().Mor(point, point)
    assert end.underlying_mor() is Sets().Mor(point, point)
    assert end.accepts(identity)
    assert end(identity) is arrow
    assert end.object_set() is end.arrow_set()
    assert end.objects().value(identity) is arrow
    assert end.arrows().cardinality() == cardinal(1)
    assert end.arrows().value(identity) == end.identity(arrow)
    assert end.end_family() is Sets().category_packet().Ends()
    assert end.identity_endomorphism() == identity
    assert end.one() == identity


def test_fixed_mor_objects_retain_their_arrow_and_own_endpoint_two_mor() -> None:
    _point, end, identity, arrow = _identity_object()
    two_mor = arrow.Mor(arrow)
    identity_2 = two_mor.identity()

    assert arrow.arrow() == identity
    assert arrow.source_object() is identity.domain()
    assert arrow.target_object() is identity.codomain()
    assert arrow.arrow_category() is Sets().ArrowCategory()
    assert two_mor is end.Mor(arrow, arrow)
    assert two_mor is end.two_mor(identity, identity)
    assert identity_2 == end.identity_2(identity)
    assert identity_2 == end.identity(arrow)
    assert identity_2(arrow) is arrow
    assert identity_2 * identity_2 == identity_2


def test_fixed_mor_category_packet_is_trivial_on_the_singleton_end_category() -> None:
    _point, end, _identity, arrow = _identity_object()
    packet = end.category_packet()

    assert packet.C() is end
    assert end.MorCategory().base_category() is end
    assert end.EndCategory().base_category() is end
    assert end.MonoCategory().base_category() is end
    assert end.EpiCategory().base_category() is end
    assert end.IsoCategory().base_category() is end
    assert end.AutCategory().base_category() is end
    assert end.Mor(arrow, arrow).identity() == end.identity(arrow)
    assert end.End(arrow).identity() == end.identity(arrow)
    assert end.Mono(arrow, arrow).identity() == end.identity(arrow)
    assert end.Epi(arrow, arrow).identity() == end.identity(arrow)
    assert end.Iso(arrow, arrow).identity() == end.identity(arrow)
    assert end.Aut(arrow).one() == end.identity(arrow)


def test_fixed_mor_arrow_core_and_structural_functors_fix_the_only_object() -> None:
    _point, end, _identity, arrow = _identity_object()
    two_identity = arrow.Mor(arrow).identity()
    arrows = end.ArrowCategory()
    two_arrow = arrows(two_identity)
    core = end.Core()
    domain = end.domain_functor()
    codomain = end.codomain_functor()
    diagonal = end.diagonal_functor()
    diagonal_arrow = diagonal(arrow)

    assert domain(two_arrow) is arrow
    assert codomain(two_arrow) is arrow
    assert diagonal_arrow.first() is arrow
    assert diagonal_arrow.second() is arrow
    assert core.Mor(arrow, arrow)(two_identity, two_identity) * core.Mor(
        arrow, arrow
    )(two_identity, two_identity) == core.identity(arrow)


def test_fixed_mor_identity_inclusion_product_and_coproduct_functors_fix_the_only_object() -> None:
    _point, end, _identity, arrow = _identity_object()
    inclusion = end.inclusion_into(end)
    product = end.product_functor()
    coproduct = end.coproduct_functor()
    pair = product.domain()(arrow, arrow)

    assert inclusion.domain() is end
    assert inclusion.codomain() is end
    assert inclusion(arrow) is arrow
    assert product(pair) is arrow
    assert coproduct(pair) is arrow


def test_fixed_mor_limit_and_colimit_categories_and_functors_fix_the_only_object() -> None:
    _point, end, _identity, arrow = _identity_object()
    diagrams = Cat().Mor(end, end)
    diagram = diagrams.constant_functor(arrow)
    diagram_object = diagrams(diagram)
    limits = end.Limits(end)
    colimits = end.Colimits(end)
    products = end.Products(end)
    coproducts = end.Coproducts(end)
    limit = end.limit_functor(end)
    colimit = end.colimit_functor(end)
    limit_construction = limits.construction(diagram)
    colimit_construction = colimits.construction(diagram)

    for constructions in (limits, colimits, products, coproducts):
        assert constructions.index_category() is end
        assert constructions.target_category() is end
    assert limit(diagram_object) is arrow
    assert colimit(diagram_object) is arrow
    for index in end.objects():
        assert limit_construction.structure_morphism(index) == end.identity(arrow)
        assert colimit_construction.costructure_morphism(index) == end.identity(arrow)


def test_fixed_mor_universal_constructions_return_the_only_object() -> None:
    _point, end, _identity, arrow = _identity_object()
    identity_2 = arrow.Mor(arrow).identity()
    product = end.product_construction((arrow, arrow))
    coproduct = end.coproduct_construction((arrow, arrow))
    equalizer = end.equalizer_construction(identity_2, identity_2)
    coequalizer = end.coequalizer_construction(identity_2, identity_2)

    assert isinstance(arrow, end.ObjectType)
    assert isinstance(end.ElementType, type)
    assert product.object() is arrow
    assert coproduct.object() is arrow
    assert end.product(()) is arrow
    assert end.coproduct(()) is arrow
    assert equalizer.object() is arrow
    assert coequalizer.object() is arrow
    assert end.equalizer(identity_2, identity_2) is arrow
    assert end.coequalizer(identity_2, identity_2) is arrow
    assert end.equalizer_of_family((identity_2, identity_2)) is arrow
    assert end.coequalizer_of_family((identity_2, identity_2)) is arrow
    assert end.fiber_product(identity_2, identity_2) is arrow
    assert end.pushout(identity_2, identity_2) is arrow
    assert end.ProductCones((arrow, arrow)) in Cat()
    assert end.CoproductCocones((arrow, arrow)) in Cat()
    span = end.span(identity_2, identity_2)
    assert span.apex() is arrow
    assert span.left_leg() == identity_2
    assert span.right_leg() == identity_2


def test_fixed_mor_universal_maps_are_the_forced_identity_two_morphisms() -> None:
    _point, end, _identity, arrow = _identity_object()
    identity_2 = arrow.Mor(arrow).identity()
    product = end.product_construction((arrow, arrow))
    coproduct = end.coproduct_construction((arrow, arrow))
    equalizer = end.equalizer_construction(identity_2, identity_2)
    coequalizer = end.coequalizer_construction(identity_2, identity_2)
    product_shape = product.diagram().domain()
    coproduct_shape = coproduct.diagram().domain()

    assert product.structure_morphism(product_shape(0)) == identity_2
    assert product.structure_morphism(product_shape(1)) == identity_2
    assert coproduct.costructure_morphism(coproduct_shape(0)) == identity_2
    assert coproduct.costructure_morphism(coproduct_shape(1)) == identity_2
    assert product.factor(product.cone()).apex_map() == identity_2
    assert coproduct.factor(coproduct.cocone()).apex_map() == identity_2
    assert equalizer.factor(equalizer.cone()).apex_map() == identity_2
    assert coequalizer.factor(coequalizer.cocone()).apex_map() == identity_2


def test_distinct_arrow_objects_of_a_fixed_mor_have_no_product_or_coproduct() -> None:
    two = Sets.Δ[1]
    end = two.End()
    identity = two.Mor(two).identity()
    constant = two.Mor(two)(lambda _point: two(0))
    identity_object = end(identity)
    constant_object = end(constant)

    assert identity_object is not constant_object
    with pytest.raises(ValueError, match="does not exist"):
        end.product((identity_object, constant_object))
    with pytest.raises(ValueError, match="does not exist"):
        end.coproduct((identity_object, constant_object))


def test_restricted_fixed_mor_object_set_is_the_admitted_arrow_subobject() -> None:
    two = Sets.Δ[1]
    identity = two.Mor(two).identity()
    constant = two.Mor(two)(lambda _point: two(0))
    monos = Sets().Mono(two, two)

    assert identity in monos.object_set()
    assert constant not in monos.object_set()


def test_functor_category_keeps_natural_transformations_as_two_morphisms() -> None:
    functor_category = Cat().Mor(Sets(), Sets())
    identity = Sets().identity_functor()
    identity_object = functor_category(identity)
    transformations = identity.natural_transformations_to(identity)
    three = Sets.Δ[2]

    assert identity_object.Mor(identity_object) is transformations
    assert transformations.identity().component(three) == Sets().Mor(three, three).identity()


def test_fixed_mor_opposite_presheaves_and_yoneda_have_the_standard_shapes() -> None:
    _point, end, _identity, arrow = _identity_object()
    opposite = end.opposite()
    presheaves = end.presheaves()
    yoneda = end.yoneda_embedding()

    assert opposite in Cat()
    assert presheaves is Cat().Mor(opposite, Sets())
    assert yoneda.domain() is end
    assert yoneda.codomain() is presheaves
    assert yoneda(arrow) in presheaves


def test_fixed_mor_arrow_subcategories_all_contain_the_unique_two_identity() -> None:
    _point, end, _identity, arrow = _identity_object()
    identity_2 = arrow.Mor(arrow).identity()
    arrows = end.ArrowCategory()
    two_arrow = arrows(identity_2)
    wide = end.WideSubcategory(end.MonomorphismArrowCategory())

    assert two_arrow in end.EndArrowCategory()
    assert two_arrow in end.IsoArrowCategory()
    assert two_arrow in end.AutomorphismArrowCategory()
    assert two_arrow in end.MonomorphismArrowCategory()
    assert two_arrow in end.EpimorphismArrowCategory()
    assert arrow in wide
    assert identity_2 in wide.Mor(arrow, arrow)


def test_fixed_mor_slice_like_categories_retain_the_only_base_object() -> None:
    _point, end, _identity, arrow = _identity_object()

    assert end.SliceOver(arrow).base_object() is arrow
    assert end.CosliceUnder(arrow).base_object() is arrow
    assert end.SubobjectCategory(arrow).base_object() is arrow
    assert end.SuperobjectCategory(arrow).base_object() is arrow
    assert end.CoveringObjectCategory(arrow).base_object() is arrow
    assert end.CoveredObjectCategory(arrow).base_object() is arrow
    assert end.Subobjects(arrow).base_object() is arrow
    assert end.Superobjects(arrow).base_object() is arrow
    assert end.CoveringObjects(arrow).base_object() is arrow
    assert end.CoveredObjects(arrow).base_object() is arrow
