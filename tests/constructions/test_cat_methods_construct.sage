r"""The public category-object operations supplied by :math:`\mathbf{Cat}`.

Every owned category is an object of ``Cat``.  Its common operations therefore
state ordinary categorical constructions: morphism classes, arrow categories,
the core, structural functors, (co)limits, slice-like categories, opposites and
presheaves.  Finite sets supply small objects on which those constructions have
elementary cardinalities and maps, so the expectations below depend only on the
definitions of the constructions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _collapse_three_to_two():
    three = Sets.Δ[2]
    two = Sets.Δ[1]
    return Sets().Mor(three, two)(lambda x: two(0) if x == 0 else two(1))


def _transposition_of_two():
    two = Sets.Δ[1]
    return Sets().Mor(two, two)(lambda x: two(1) if x == 0 else two(0))


def _two_discrete_objects():
    labels = Sets()(("a", "b"))
    return PosetCategory(labels, le=lambda left, right: left == right)


def test_cat_places_categories_and_coordinates_their_morphism_families() -> None:
    r"""For finite sets, ``Mor``, ``End``, ``Mono``, ``Epi``, ``Iso`` and ``Aut`` have their elementary sizes."""
    sets = Sets()
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    packet = sets.category_packet()

    assert sets in Cat()
    assert Cat() in Cat()
    assert packet.C() is sets
    assert sets.MorCategory().base_category() is sets
    assert sets.EndCategory().base_category() is sets
    assert sets.MonoCategory().base_category() is sets
    assert sets.EpiCategory().base_category() is sets
    assert sets.IsoCategory().base_category() is sets
    assert sets.AutCategory().base_category() is sets
    assert sets.Mor(two, three).cardinality() == cardinal(9)
    assert sets.End(two).cardinality() == cardinal(4)
    assert sets.Mono(two, three).cardinality() == cardinal(6)
    assert sets.Epi(three, two).cardinality() == cardinal(6)
    assert sets.Iso(two, two).cardinality() == cardinal(2)
    assert sets.Aut(two).order() == 2


def test_cat_object_and_element_types_match_objects_and_points() -> None:
    r"""The object and element types supplied by a category contain its represented objects and their points."""
    sets = Sets()
    two = Sets.Δ[1]

    assert isinstance(two, sets.ObjectType)
    assert isinstance(two(0), sets.ElementType)


def test_cat_arrow_category_core_and_structural_functors_have_the_defining_maps() -> None:
    r"""Domain, codomain and diagonal are the evident functors, and the core keeps precisely isomorphisms."""
    sets = Sets()
    collapse = _collapse_three_to_two()
    swap = _transposition_of_two()
    arrows = sets.ArrowCategory()
    collapse_object = arrows(collapse)
    domain = sets.domain_functor()
    codomain = sets.codomain_functor()
    diagonal = sets.diagonal_functor()
    two = Sets.Δ[1]
    diagonal_two = diagonal(two)
    core = sets.Core()
    swap_in_core = core.Mor(two, two)(swap, swap)

    assert arrows in Cat()
    assert domain.domain() is arrows
    assert domain.codomain() is sets
    assert codomain.domain() is arrows
    assert codomain.codomain() is sets
    assert domain(collapse_object) is collapse.domain()
    assert codomain(collapse_object) is collapse.codomain()
    assert diagonal.domain() is sets
    assert diagonal_two.first() is two
    assert diagonal_two.second() is two
    assert swap_in_core * swap_in_core == core.identity(two)


def test_cat_inclusion_product_and_coproduct_functors_preserve_the_expected_data() -> None:
    r"""Finite sets include into sets, while binary product and coproduct have sizes ``2*3`` and ``2+3``."""
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    inclusion = FiniteSets().inclusion_into(Sets())
    product = Sets().product_functor()
    coproduct = Sets().coproduct_functor()
    pair = product.domain()(two, three)

    assert inclusion.domain() is FiniteSets()
    assert inclusion.codomain() is Sets()
    assert inclusion(two) is two
    assert product.domain() is coproduct.domain()
    assert product.codomain() is Sets()
    assert coproduct.codomain() is Sets()
    assert product(pair).cardinality() == cardinal(6)
    assert coproduct(pair).cardinality() == cardinal(5)


def test_cat_limit_colimit_product_and_coproduct_categories_retain_index_and_target() -> None:
    r"""The selected construction categories remember exactly the diagram shape and target category."""
    shape = _two_discrete_objects()
    sets = Sets()
    limits = sets.Limits(shape)
    colimits = sets.Colimits(shape)
    products = sets.Products(shape)
    coproducts = sets.Coproducts(shape)

    for constructions in (limits, colimits, products, coproducts):
        assert constructions in Cat()
        assert constructions.index_category() is shape
        assert constructions.target_category() is sets


def test_cat_limit_and_colimit_functors_send_a_constant_two_point_diagram_to_four_points() -> None:
    r"""Over two discrete objects, a constant two-point diagram has product and coproduct of cardinality four."""
    shape = _two_discrete_objects()
    sets = Sets()
    diagrams = Cat().Mor(shape, sets)
    diagram = diagrams.constant_functor(Sets.Δ[1])
    diagram_object = diagrams(diagram)
    limit = sets.limit_functor(shape)
    colimit = sets.colimit_functor(shape)

    assert limit.domain() is diagrams
    assert limit.codomain() is sets
    assert colimit.domain() is diagrams
    assert colimit.codomain() is sets
    assert limit(diagram_object).cardinality() == cardinal(4)
    assert colimit(diagram_object).cardinality() == cardinal(4)


def test_cat_product_and_coproduct_constructions_retain_their_universal_objects() -> None:
    r"""The selected product of two and three points has six points; their coproduct has five."""
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    product = Sets().product_construction((two, three))
    coproduct = Sets().coproduct_construction((two, three))

    assert product.object().cardinality() == cardinal(6)
    assert coproduct.object().cardinality() == cardinal(5)
    assert Sets().ProductCones((two, three)) in Cat()
    assert Sets().CoproductCocones((two, three)) in Cat()


def test_cat_equalizer_and_coequalizer_constructions_retain_objects_and_universal_maps() -> None:
    r"""Equalizing residue mod three with zero gives ``{0,3}``; coequalizing adjacent pairs gives two classes."""
    source = Sets.Δ[5]
    residues = Sets.Δ[2]
    residue = Sets().Mor(source, residues)(lambda n: residues(n % 3))
    zero = Sets().Mor(source, residues)(lambda _n: residues(0))
    equalizer = Sets().equalizer_construction(residue, zero)
    equalizer_shape = equalizer.diagram().domain()
    inclusion = equalizer.structure_morphism(equalizer_shape.source())

    co_source = Sets.Δ[1]
    co_target = Sets.Δ[3]
    initial = Sets().Mor(co_source, co_target)(lambda n: co_target(n))
    successor = Sets().Mor(co_source, co_target)(lambda n: co_target(n + 1))
    coequalizer = Sets().coequalizer_construction(initial, successor)
    coequalizer_shape = coequalizer.diagram().domain()
    projection = coequalizer.costructure_morphism(coequalizer_shape.target())

    assert equalizer.object().cardinality() == cardinal(2)
    assert {inclusion(x) for x in equalizer.object()} == {source(0), source(3)}
    assert Sets().equalizer(residue, zero).cardinality() == cardinal(2)
    assert Sets().equalizer_of_family((residue, zero)).cardinality() == cardinal(2)
    assert coequalizer.object().cardinality() == cardinal(2)
    assert projection(co_target(0)) == projection(co_target(2))
    assert projection(co_target(0)) != projection(co_target(3))
    assert Sets().coequalizer(initial, successor).cardinality() == cardinal(2)
    assert Sets().coequalizer_of_family((initial, successor)).cardinality() == cardinal(2)


def test_cat_span_pushout_and_fiber_product_have_the_defining_finite_set_values() -> None:
    r"""Two two-point sets over a point pull back to four points; gluing their chosen points gives three."""
    point = Sets.Δ[0]
    two = Sets.Δ[1]
    to_point = Sets().Mor(two, point)(lambda _x: point(0))
    at_zero = Sets().Mor(point, two)(lambda _p: two(0))
    span = Sets().span(at_zero, at_zero)

    assert Sets().fiber_product(to_point, to_point).cardinality() == cardinal(4)
    assert span.apex() is point
    assert span.left_leg() == at_zero
    assert span.right_leg() == at_zero
    assert Sets().pushout(at_zero, at_zero).cardinality() == cardinal(3)


def test_cat_opposite_presheaves_and_yoneda_have_the_standard_domains_and_codomains() -> None:
    r"""Presheaves are ``[C^op, Set]`` and Yoneda maps ``C`` into that functor category."""
    sets = Sets()
    opposite = sets.opposite()
    presheaves = sets.presheaves()
    yoneda = sets.yoneda_embedding()
    two = Sets.Δ[1]

    assert opposite in Cat()
    assert presheaves in Cat()
    assert presheaves is Cat().Mor(opposite, Sets())
    assert yoneda.domain() is sets
    assert yoneda.codomain() is presheaves
    assert yoneda(two) in presheaves


def test_cat_arrow_subcategories_classify_endomorphisms_isomorphisms_monos_and_epis() -> None:
    r"""A transposition is an automorphism; a point inclusion is monic; the three-to-two collapse is epic."""
    sets = Sets()
    arrows = sets.ArrowCategory()
    swap = arrows(_transposition_of_two())
    collapse = arrows(_collapse_three_to_two())
    point = Sets.Δ[0]
    two = Sets.Δ[1]
    at_zero = Sets().Mor(point, two)(lambda _p: two(0))
    inclusion = arrows(at_zero)
    injections = sets.WideSubcategory(sets.MonomorphismArrowCategory())

    assert swap in sets.EndArrowCategory()
    assert swap in sets.IsoArrowCategory()
    assert swap in sets.AutomorphismArrowCategory()
    assert collapse not in sets.EndArrowCategory()
    assert collapse in sets.EpimorphismArrowCategory()
    assert inclusion in sets.MonomorphismArrowCategory()
    assert inclusion in injections


def test_cat_slice_coslice_subobject_superobject_and_quotient_categories_retain_the_base() -> None:
    r"""Slice-like constructions remember the object over or under which their arrows are taken."""
    sets = Sets()
    point = Sets.Δ[0]
    two = Sets.Δ[1]
    three = Sets.Δ[2]

    assert sets.SliceOver(two).base_object() is two
    assert sets.CosliceUnder(point).base_object() is point
    assert sets.SubobjectCategory(three).base_object() is three
    assert sets.SuperobjectCategory(point).base_object() is point
    assert sets.CoveringObjectCategory(point).base_object() is point
    assert sets.CoveredObjectCategory(three).base_object() is three
    assert sets.Subobjects(three).base_object() is three
    assert sets.Superobjects(point).base_object() is point
    assert sets.CoveringObjects(point).base_object() is point
    assert sets.CoveredObjects(three).base_object() is three
