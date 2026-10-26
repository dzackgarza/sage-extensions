r"""Finite products and free products, including empty diagrams and infinite factors.

These are source-level mathematical specimens; execution follows terminal T.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_group_product_retains_abelianity_from_factors_not_selected_category() -> None:
    r"""The product of abelian groups remains abelian when selected in Grp."""
    cyclic = Groups.C(2)
    product = Groups().product_construction((cyclic, cyclic))
    result = product.object()
    diagram = product.diagram()
    first, second = diagram.domain()(0), diagram.domain()(1)
    left = product.structure_morphism(first)
    right = product.structure_morphism(second)

    assert result in AbelianGroups()
    assert result.cardinality() == cardinal(4)
    assert left.codomain() is cyclic and right.codomain() is cyclic


def test_empty_group_diagrams_have_the_trivial_group_and_unique_maps() -> None:
    category = Groups().FinitelyPresentedAsGroup()
    cyclic = Groups.C(2)
    product = category.product_construction(())
    coproduct = category.coproduct_construction(())
    assert product.object() in category and coproduct.object() in category
    assert product.object().cardinality() == cardinal(1)
    assert coproduct.object().cardinality() == cardinal(1)

    cone = product.diagram().Cones().cone(cyclic, lambda _index: None)
    terminal = product.factor(cone).apex_map()
    assert terminal.domain() is cyclic and terminal.codomain() is product.object()
    assert terminal(next(iter(cyclic.group_generators()))) == product.object().one()

    cocone = coproduct.diagram().Cocones().cocone(cyclic, lambda _index: None)
    initial = coproduct.factor(cocone).apex_map()
    assert initial.domain() is coproduct.object() and initial.codomain() is cyclic
    assert initial(coproduct.object().one()) == cyclic.one()


def test_abelian_coproduct_of_two_cyclic_groups_is_product_not_free_product() -> None:
    r"""``C2 ⊕ C2`` has commuting injections and their universal sum map."""
    abelian = AbelianGroups()
    cyclic = Groups.C(2)
    generator = next(iter(cyclic.group_generators()))
    construction = abelian.coproduct_construction((cyclic, cyclic))
    coproduct = construction.object()
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    left = construction.costructure_morphism(first)
    right = construction.costructure_morphism(second)
    identity = cyclic.Mor(cyclic).identity()
    cocone = construction.diagram().Cocones().cocone(
        cyclic, lambda _index: identity
    )
    fold = construction.factor(cocone).apex_map()

    assert coproduct in abelian
    assert coproduct.cardinality() == cardinal(4)
    assert left(generator) * right(generator) == right(generator) * left(generator)
    assert fold * left == identity
    assert fold * right == identity
    assert fold(left(generator) * right(generator)) == cyclic.one()


def test_mixed_abelian_coproduct_injections_are_sections_of_selected_projections() -> None:
    r"""The coproduct ``Z ⊕ C2`` reuses the product's canonical coordinates."""
    abelian = AbelianGroups()
    integers = Groups.Free(1)
    label = next(iter(integers.free_basis()))
    generator = integers.free_generator(label)
    cyclic = Groups.C(2)
    involution = next(iter(cyclic.group_generators()))
    factors = (integers, cyclic)
    coproduct = abelian.coproduct_construction(factors)
    diagram = coproduct.diagram()
    first, second = diagram.domain()(0), diagram.domain()(1)
    injection_z = coproduct.costructure_morphism(first)
    injection_c2 = coproduct.costructure_morphism(second)
    to_z = coproduct.factor(diagram.Cocones().cocone(
        integers,
        lambda index: integers.Mor(integers).identity()
        if index is first else cyclic.Mor(integers).elementwise(
            lambda _element: integers.one()
        ),
    )).apex_map()
    to_c2 = coproduct.factor(diagram.Cocones().cocone(
        cyclic,
        lambda index: integers.Mor(cyclic).elementwise(
            lambda _element: cyclic.one()
        ) if index is first else cyclic.Mor(cyclic).identity(),
    )).apex_map()

    assert coproduct.object() in abelian
    assert to_z(injection_z(generator)) == generator
    assert to_c2(injection_z(generator)) == cyclic.one()
    assert to_z(injection_c2(involution)) == integers.one()
    assert to_c2(injection_c2(involution)) == involution


def test_product_of_two_infinite_free_groups_retains_projections_and_universal_factor() -> None:
    r"""For F1 = Z, the product F1 x F1 has the two selected projections.

    The map n -> (n,2n) is characterized by those projections, not by
    identifying either factor with a product subgroup.
    """
    free = Groups.Free(1)
    label = next(iter(free.free_basis()))
    generator = free.free_generator(label)
    construction = Groups().product_construction((free, free))
    product = construction.object()
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    identity = free.Mor(free).identity()
    doubling = free.Mor(free)({label: generator**2})
    cone = construction.diagram().Cones().cone(
        free, lambda index: identity if index is first else doubling
    )
    factor = construction.factor(cone).apex_map()

    assert product in Groups().FinitelyPresentedAsGroup()
    assert construction.structure_morphism(first)(factor(generator)) == generator
    assert construction.structure_morphism(second)(factor(generator)) == generator**2
    assert construction.structure_morphism(first) * factor == identity
    assert construction.structure_morphism(second) * factor == doubling


def test_free_product_of_infinite_free_and_finite_cyclic_groups() -> None:
    r"""Z * C2 admits factor maps into C2 extending both specified legs."""
    free = Groups.Free(1)
    source_label = next(iter(free.free_basis()))
    cyclic = Groups.C(2)
    involution = next(iter(cyclic.group_generators()))
    construction = Groups().coproduct_construction((free, cyclic))
    coproduct = construction.object()
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    reduction = free.Mor(cyclic)({source_label: involution})
    identity = cyclic.Mor(cyclic).identity()
    cocone = construction.diagram().Cocones().cocone(
        cyclic, lambda index: reduction if index is first else identity
    )
    factor = construction.factor(cocone).apex_map()

    assert coproduct in Groups().FinitelyPresentedAsGroup()
    assert factor.domain() is coproduct and factor.codomain() is cyclic
    assert factor(construction.costructure_morphism(first)(free.free_generator(source_label))) == involution
    assert factor(construction.costructure_morphism(second)(involution)) == involution
    assert factor * construction.costructure_morphism(first) == reduction
    assert factor * construction.costructure_morphism(second) == identity


def test_free_product_factors_a_cocone_into_a_non_gap_predicate_group() -> None:
    r"""The free product F1*C2 maps into a represented infinite predicate subgroup.

    The source keeps its GAP finitely presented free-product model, but the
    cocone apex has only its subgroup inclusion and exact membership law.
    This distinguishes the universal map from a GAP-to-GAP homomorphism.
    """
    free, cyclic = Groups.Free(1), Groups.C(2)
    label = next(iter(free.free_basis()))
    generator = free.free_generator(label)
    involution = next(iter(cyclic.group_generators()))
    reduction = free.Mor(cyclic)({label: involution})
    subgroup = free.predicate_subgroup(
        lambda element: reduction(element) == cyclic.one(),
        "even exponent subgroup of the free cyclic group",
    )
    from_free = free.Mor(subgroup)({label: subgroup(generator**2)})
    from_cyclic = cyclic.Mor(subgroup)(lambda _element: subgroup.one())

    construction = Groups().coproduct_construction((free, cyclic))
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    cocone = construction.diagram().Cocones().cocone(
        subgroup,
        lambda index: from_free if index is first else from_cyclic,
    )
    factor = construction.factor(cocone).apex_map()

    assert factor.domain() is construction.object()
    assert factor.codomain() is subgroup
    assert factor(construction.costructure_morphism(first)(generator)) == subgroup(generator**2)
    assert factor(construction.costructure_morphism(second)(involution)) == subgroup.one()
    assert (factor * construction.costructure_morphism(first))(generator) == from_free(generator)


def test_product_of_free_and_finite_cyclic_groups_transports_factor_maps() -> None:
    free = Groups.Free(1)
    label = next(iter(free.free_basis()))
    generator = free.free_generator(label)
    cyclic = Groups.C(2)
    involution = next(iter(cyclic.group_generators()))
    reduction = free.Mor(cyclic)({label: involution})
    identity = free.Mor(free).identity()
    construction = Groups().product_construction((free, cyclic))
    shape = construction.diagram().domain()
    left, right = shape(0), shape(1)
    cone = construction.diagram().Cones().cone(
        free, lambda index: identity if index is left else reduction
    )
    factor = construction.factor(cone).apex_map()

    assert construction.object() in Groups().FinitelyPresentedAsGroup()
    assert construction.structure_morphism(left)(factor(generator)) == generator
    assert construction.structure_morphism(right)(factor(generator)) == involution
    assert construction.structure_morphism(right) * factor == reduction


def test_group_product_factors_a_cone_with_no_apex_gap_realization() -> None:
    r"""A predicate kernel of Z is an infinite group with no selected GAP model.

    The universal product map into Z x C2 is determined by its literal
    legs, not by seeking GAP generators of the cone apex.
    """
    free, cyclic = Groups.Free(1), Groups.C(2)
    basis = next(iter(free.free_basis()))
    generator = free.free_generator(basis)
    involution = next(iter(cyclic.group_generators()))
    reduction = free.Mor(cyclic)({basis: involution})
    subgroup = free.predicate_subgroup(
        lambda element: reduction(element) == cyclic.one(),
        "kernel of reduction modulo two",
    )
    inclusion = subgroup.inclusion()
    construction = Groups().product_construction((free, cyclic))
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    cone = construction.diagram().Cones().cone(
        subgroup,
        lambda index: inclusion if index is first else reduction * inclusion,
    )
    factor = construction.factor(cone).apex_map()
    even_word = subgroup(generator**2)

    assert factor.domain() is subgroup
    assert factor.codomain() is construction.object()
    assert construction.structure_morphism(first)(factor(even_word)) == generator**2
    assert construction.structure_morphism(second)(factor(even_word)) == cyclic.one()
    assert (construction.structure_morphism(first) * factor)(even_word) == inclusion(even_word)


def test_free_product_with_a_trivial_factor_preserves_finiteness() -> None:
    finite = Groups().Finite()
    trivial, cyclic = Groups.C(1), Groups.C(2)
    construction = finite.coproduct_construction((trivial, cyclic))
    assert construction.object() in finite
    assert construction.object().cardinality() == cardinal(2)


def test_group_equalizer_has_its_subgroup_inclusion_and_universal_map() -> None:
    r"""The equalizer of g -> g^3 and g -> g in C4 is the subgroup <g^2>."""
    cyclic = Groups.C(4)
    g = next(iter(cyclic.group_generators()))
    cubing = cyclic.Mor(cyclic)({g: g**3})
    identity = cyclic.Mor(cyclic).identity()
    construction = Groups().equalizer_construction(cubing, identity)
    equalizer = construction.object()
    shape = construction.diagram().domain()
    inclusion = construction.structure_morphism(shape.source())
    two = Groups.C(2)
    h = next(iter(two.group_generators()))
    into_four = two.Mor(cyclic)({h: g**2})
    cone = construction.diagram().Cones().cone(
        two,
        lambda index: into_four if index is shape.source() else cubing * into_four,
    )
    factor = construction.factor(cone).apex_map()

    assert equalizer in Subgroups(cyclic)
    assert equalizer.cardinality() == cardinal(2)
    assert inclusion.codomain() is cyclic and inclusion.domain() is equalizer
    assert inclusion(factor(h)) == g**2
    assert inclusion * factor == into_four


def test_group_coequalizer_has_quotient_projection_and_universal_map() -> None:
    r"""Coequalizing g -> g^3 and g -> g in C4 gives C4/<g^2> = C2."""
    cyclic = Groups.C(4)
    g = next(iter(cyclic.group_generators()))
    cubing = cyclic.Mor(cyclic)({g: g**3})
    identity = cyclic.Mor(cyclic).identity()
    construction = Groups().coequalizer_construction(cubing, identity)
    coequalizer = construction.object()
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())
    two = Groups.C(2)
    h = next(iter(two.group_generators()))
    reduction = cyclic.Mor(two)({g: h})
    cocone = construction.diagram().Cocones().cocone(
        two,
        lambda index: reduction * cubing if index is shape.source() else reduction,
    )
    factor = construction.factor(cocone).apex_map()

    assert coequalizer.cardinality() == cardinal(2)
    assert projection.domain() is cyclic and projection.codomain() is coequalizer
    assert projection(g**2) == coequalizer.one()
    assert factor * projection == reduction
    assert factor(projection(g)) == h


def test_group_coequalizer_from_generated_subgroup_uses_its_selected_relator() -> None:
    r"""Maps from ``<g²> <= C4`` impose ``g² = 1`` on ``C4``."""
    cyclic = Groups.C(4)
    g = next(iter(cyclic.group_generators()))
    subgroup = cyclic.subgroup((g**2,))
    inclusion = subgroup.inclusion()
    trivial = subgroup.Mor(cyclic).elementwise(lambda _element: cyclic.one())
    construction = Groups().coequalizer_construction(inclusion, trivial)
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())

    assert construction.object().cardinality() == cardinal(2)
    assert projection(g**2) == construction.object().one()
    assert projection * inclusion == projection * trivial

    two = Groups.C(2)
    h = next(iter(two.group_generators()))
    reduction = cyclic.Mor(two)({g: h})
    cocone = construction.diagram().Cocones().cocone(
        two,
        lambda index: reduction * inclusion if index is shape.source() else reduction,
    )
    factor = construction.factor(cocone).apex_map()
    assert factor * projection == reduction
    assert factor(projection(g)) == h


def test_infinite_presented_group_coequalizer_descends_homomorphism() -> None:
    r"""The quotient of Z by the relation a^3=a is C2, with its descent."""
    free = Groups.Free(1)
    label = next(iter(free.free_basis()))
    generator = free.free_generator(label)
    cubing = free.Mor(free)({label: generator**3})
    identity = free.Mor(free).identity()
    construction = Groups().coequalizer_construction(cubing, identity)
    quotient = construction.object()
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())
    two = Groups.C(2)
    h = next(iter(two.group_generators()))
    reduction = free.Mor(two)({label: h})
    cocone = construction.diagram().Cocones().cocone(
        two,
        lambda index: reduction * cubing if index is shape.source() else reduction,
    )
    factor = construction.factor(cocone).apex_map()

    assert quotient in GroupsWithChosenFinitePresentation()
    assert projection(generator**2) == quotient.one()
    assert factor(projection(generator)) == h
    assert factor * projection == reduction
