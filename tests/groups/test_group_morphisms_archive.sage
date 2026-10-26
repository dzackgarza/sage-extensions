r"""Group homomorphisms: kernels, images, cokernels, composites and automorphism groups."""

from sage_extensions.all import *


def test_reduction_c4_to_c2_has_kernel_of_order_two_and_c4_mod_kernel_is_the_image() -> None:
    r"""First isomorphism theorem for $C_4 \to C_2$, $g \mapsto h$: $\ker = \langle g^2 \rangle$ and $C_4/\ker \cong C_2$."""
    source = Groups.C(4)
    target = Groups.C(2)
    (g,) = source.group_generators()
    (h,) = target.group_generators()
    reduction = source.Mor(target)({g: h})

    kernel = reduction.kernel()
    assert kernel.order() == 2
    assert g**2 in kernel
    assert g not in kernel
    assert reduction.image().order() == 2
    assert kernel.inclusion().cokernel().is_isomorphic_to(reduction.image())
    assert reduction(reduction.lift(h)) == h


def test_finite_group_mor_cardinality_uses_the_represented_gap_mor() -> None:
    assert Groups.C(2).Mor(Groups.C(3)).cardinality() == 1
    assert Groups.C(4).Mor(Groups.C(6)).cardinality() == 2
    assert Groups.C(12).Mor(Groups.C(18)).cardinality() == 6


def test_the_image_epimorphism_has_a_set_section_but_no_group_section() -> None:
    r"""Squaring C4 -> C4 factors onto C2, but C4 ->> C2 does not split in Grp."""
    cyclic = Groups.C(4)
    generator = next(iter(cyclic.group_generators()))
    square = cyclic.Mor(cyclic)({generator: generator**2})
    image = square.image()
    epic = square.factor_through(image.inclusion())
    section = square.image_section()

    assert square.image() is image
    assert section.domain() is image and section.codomain() is cyclic
    assert epic.domain() is cyclic and epic.codomain() is image
    assert all(epic(section(value)) == value for value in image)
    assert all(image.inclusion()(epic(value)) == square(value) for value in cyclic)
    lift = section(image(generator**2))
    assert lift * lift != section(image.one())


def test_free_group_reduction_has_a_section_of_its_finite_image_as_sets() -> None:
    free, cyclic = Groups.Free(1), Groups.C(2)
    label = next(iter(free.free_basis()))
    generator = next(iter(cyclic.group_generators()))
    reduction = free.Mor(cyclic)({label: generator})
    image = reduction.image()
    section = reduction.image_section()
    epic = reduction.factor_through(image.inclusion())

    assert section.domain() is image and section.codomain() is free
    assert all(epic(section(value)) == value for value in image)
    assert image.inclusion()(epic(free.free_generator(label))) == generator


def test_elementwise_free_group_map_to_finite_group_has_decided_surjectivity() -> None:
    r"""The selected generator of ``F1`` maps onto ``C2`` without an enumerated source."""
    free = Groups.Free(1)
    cyclic = Groups.C(2)
    label = next(iter(free.free_basis()))
    h = next(iter(cyclic.group_generators()))
    generator_map = free.Mor(cyclic)({label: h})
    elementwise = free.Mor(cyclic).elementwise(lambda word: generator_map(word))

    assert elementwise.is_surjective() is True
    assert elementwise(free.free_generator(label)) == h


def test_elementwise_free_group_reduction_has_decided_noninjectivity() -> None:
    r"""Reduction ``F1 -> C2`` has kernel containing the square of its generator."""
    free = Groups.Free(1)
    cyclic = Groups.C(2)
    label = next(iter(free.free_basis()))
    h = next(iter(cyclic.group_generators()))
    reduction = free.Mor(cyclic)({label: h})
    elementwise = free.Mor(cyclic).elementwise(lambda word: reduction(word))

    assert elementwise.is_injective() is False
    assert elementwise(free.free_generator(label)**2) == cyclic.one()


def test_finite_group_cannot_surject_onto_infinite_group() -> None:
    r"""The trivial map ``C2 -> F1`` has a cardinality obstruction to surjectivity."""
    finite = Groups.C(2)
    infinite = Groups.Free(1)
    trivial = finite.Mor(infinite).elementwise(lambda _element: infinite.one())

    assert finite in Groups().Finite()
    assert infinite in Groups().Infinite()
    assert trivial.is_surjective() is False


def test_infinite_group_cannot_inject_into_finite_group() -> None:
    r"""Reduction ``F1 -> C2`` is noninjective by endpoint cardinality."""
    infinite = Groups.Free(1)
    finite = Groups.C(2)
    label = next(iter(infinite.free_basis()))
    h = next(iter(finite.group_generators()))
    reduction = infinite.Mor(finite)({label: h})

    assert infinite in Groups().Infinite()
    assert finite in Groups().Finite()
    assert reduction.is_injective() is False


def test_finite_group_morphism_cardinality_obstructions() -> None:
    r"""No homomorphism ``C4 -> C2`` injects, and none ``C2 -> C4`` surjects."""
    four, two = Groups.C(4), Groups.C(2)
    to_two = four.Mor(two).elementwise(lambda _element: two.one())
    to_four = two.Mor(four).elementwise(lambda _element: four.one())

    assert to_two.is_injective() is False
    assert to_four.is_surjective() is False


def test_elementwise_finite_group_isomorphism_reuses_group_preimages() -> None:
    r"""An elementwise automorphism of ``C4`` has a group inverse."""
    cyclic = Groups.C(4)
    g = next(iter(cyclic.group_generators()))
    inversion = cyclic.Mor(cyclic).elementwise(lambda element: ~element)
    inverse = inversion.inverse()

    assert inversion.is_injective() is True
    assert inversion.is_surjective() is True
    assert inverse.domain() is cyclic and inverse.codomain() is cyclic
    assert inverse(inversion(g)) == g
    assert inversion(inverse(g)) == g


def test_noninjective_group_map_factors_through_its_proper_image() -> None:
    r"""For f:C4 -> C4, g -> g^2, the image is the proper subgroup <g^2>.

    The canonical factor C4 -> <g^2> is surjective, not injective;
    composing it with the subgroup inclusion recovers f.
    """
    cyclic = Groups.C(4)
    generator = next(iter(cyclic.group_generators()))
    square = cyclic.Mor(cyclic)({generator: generator**2})
    image = square.image()
    inclusion = image.inclusion()
    factor = square.factor_through(inclusion)

    assert image in Subgroups(cyclic)
    assert image.cardinality() == cardinal(2)
    assert generator not in image
    assert factor.domain() is cyclic and factor.codomain() is image
    assert inclusion.domain() is image and inclusion.codomain() is cyclic
    assert (inclusion * factor)(generator) == square(generator) == generator**2
    assert factor(generator**2) == image.one()
    assert factor.is_surjective() is True
    assert square.factor_through_or_none(cyclic.subgroup(()).inclusion()) is None


def test_image_factorization_retains_the_image_and_surjective_first_arrow() -> None:
    r"""The selected factorization is ``C4 ->> <g²> -> C4``, not a new image model."""
    cyclic = Groups.C(4)
    generator = next(iter(cyclic.group_generators()))
    square = cyclic.Mor(cyclic)({generator: generator**2})
    epic, inclusion = square.image_factorization()
    image = square.image()

    assert epic.domain() is cyclic and epic.codomain() is image
    assert inclusion.domain() is image and inclusion.codomain() is cyclic
    assert inclusion is image.inclusion()
    assert epic.is_surjective() is True
    assert epic.is_injective() is False
    assert inclusion * epic == square


def test_generated_subgroup_finite_image_lifts_use_its_selected_generators() -> None:
    r"""The subgroup ``<g²> <= C4`` supplies witnesses for its inclusion image."""
    cyclic = Groups.C(4)
    generator = next(iter(cyclic.group_generators()))
    subgroup = cyclic.subgroup((generator**2,))
    inclusion = subgroup.inclusion()
    witnesses = subgroup.finite_image_lifts(inclusion)

    assert subgroup in GeneratedSubgroups(cyclic)
    assert set(witnesses) == {cyclic.one(), generator**2}
    assert all(inclusion(lift) == value for value, lift in witnesses.items())


def test_generated_subgroup_map_image_uses_its_retained_generator_family() -> None:
    r"""The image of ``<g²> <= C4`` under squaring is trivial."""
    cyclic = Groups.C(4)
    generator = next(iter(cyclic.group_generators()))
    subgroup = cyclic.subgroup((generator**2,))
    square = subgroup.Mor(cyclic).elementwise(
        lambda element: subgroup.inclusion()(element)**2
    )
    image = square.image()
    epic, inclusion = square.image_factorization()

    assert image in Subgroups(cyclic)
    assert image.cardinality() == cardinal(1)
    assert epic.domain() is subgroup and epic.codomain() is image
    assert inclusion.domain() is image and inclusion.codomain() is cyclic
    assert inclusion * epic == square


def test_elementwise_generated_subgroup_map_has_gap_realization() -> None:
    r"""A map defined on ``<g²> <= C4`` realizes its selected generator in GAP."""
    cyclic = Groups.C(4)
    g = next(iter(cyclic.group_generators()))
    subgroup = cyclic.subgroup((g**2,))
    inclusion = subgroup.inclusion()
    elementwise = subgroup.Mor(cyclic).elementwise(lambda element: inclusion(element))

    assert elementwise.is_injective() is True
    assert elementwise.is_surjective() is False


def test_generated_subgroup_homomorphisms_are_determined_by_generators() -> None:
    r"""Maps from ``<g²> <= C4`` agree precisely on their selected generator."""
    cyclic = Groups.C(4)
    g = next(iter(cyclic.group_generators()))
    subgroup = cyclic.subgroup((g**2,))
    inclusion = subgroup.inclusion()
    same = subgroup.Mor(cyclic).elementwise(lambda element: cyclic(element))
    trivial = subgroup.Mor(cyclic).elementwise(lambda _element: cyclic.one())

    assert inclusion == same
    assert inclusion != trivial


def test_composition_out_of_generated_subgroup_uses_its_generators() -> None:
    r"""Composition of selected maps on ``<g²>`` retains their group law."""
    cyclic = Groups.C(4)
    g = next(iter(cyclic.group_generators()))
    subgroup = cyclic.subgroup((g**2,))
    selected = next(iter(subgroup.selected_subgroup_generators()))
    inclusion = subgroup.Mor(cyclic)({selected: g**2})
    square = cyclic.Mor(cyclic)({g: g**2})
    composite = square * inclusion

    assert composite.domain() is subgroup and composite.codomain() is cyclic
    assert composite(selected) == cyclic.one()
    assert composite == subgroup.Mor(cyclic).elementwise(lambda _point: cyclic.one())


def test_finite_group_homomorphism_equality_uses_all_source_elements() -> None:
    r"""Maps ``C4 -> C2`` are distinguished by their actual pointwise action."""
    source = Groups.C(4)
    target = Groups.C(2)
    g = next(iter(source.group_generators()))
    h = next(iter(target.group_generators()))
    reduction = source.Mor(target)({g: h})
    same = source.Mor(target).elementwise(lambda element: reduction(element))
    trivial = source.Mor(target).elementwise(lambda _element: target.one())

    assert reduction == same
    assert reduction != trivial


def test_generated_subgroup_inclusion_has_presented_group_cokernel() -> None:
    r"""The cokernel of ``<a²> -> F(a)`` is the presented cyclic group C2."""
    free = Groups.Free(1)
    label = next(iter(free.free_basis()))
    generator = free.free_generator(label)
    subgroup = free.subgroup((generator**2,))
    inclusion = subgroup.inclusion()
    quotient = inclusion.cokernel()
    projection = inclusion.cokernel_projection()

    assert quotient in Groups().FinitelyPresentedAsGroup()
    assert projection.domain() is free and projection.codomain() is quotient
    assert projection(generator**2) == quotient.one()
    assert projection * inclusion == subgroup.Mor(quotient).elementwise(
        lambda _element: quotient.one()
    )


def test_infinite_free_source_factors_through_a_proper_cyclic_image() -> None:
    r"""The map Z -> C4 sending its free generator to g^2 factors via C2.

    This must use selected generators rather than enumerating its source.
    """
    free = Groups.Free(1)
    target = Groups.C(4)
    label = next(iter(free.free_basis()))
    generator = next(iter(target.group_generators()))
    morphism = free.Mor(target)({label: generator**2})
    image = morphism.image()
    inclusion = image.inclusion()
    factor = morphism.factor_through(inclusion)

    assert image.cardinality() == cardinal(2)
    assert factor.domain() is free and factor.codomain() is image
    assert (inclusion * factor)(free.free_generator(label)) == generator**2
    assert factor(free.free_generator(label)**2) == image.one()


def test_finite_kernel_uses_the_exact_gap_structure_predicates() -> None:
    symmetric = Groups.S(3)
    target = Groups.C(2)
    target_generator = target.group_generators()[0]
    sign = symmetric.Mor(target)(
        {
            generator: (
                target_generator if generator.order() == 2 else target.one()
            )
            for generator in symmetric.group_generators()
        }
    )
    kernel = sign.kernel()

    assert kernel.cardinality() == 3
    assert kernel.is_abelian()


def test_group_cokernels_quotient_by_the_normal_closure_of_the_image() -> None:
    symmetric = Groups.S(3)
    target = Groups.C(2)
    target_generator = target.group_generators()[0]
    sign = symmetric.Mor(target)(
        {
            generator: (
                target_generator if generator.order() == 2 else target.one()
            )
            for generator in symmetric.group_generators()
        }
    )
    kernel = sign.kernel()

    inclusion = kernel.inclusion()
    assert kernel.inclusion() is inclusion
    quotient = inclusion.cokernel()
    quotient_projection = inclusion.cokernel_projection()
    assert quotient.order() == 2
    assert quotient_projection.domain() is symmetric
    assert quotient_projection.codomain() is quotient
    assert quotient_projection.is_surjective()

    trivial = sign.cokernel()
    trivial_projection = sign.cokernel_projection()
    assert trivial.order() == 1
    assert trivial_projection.domain() is target
    assert trivial_projection.codomain() is trivial
    assert trivial_projection.is_surjective()


def test_cokernel_of_squaring_on_an_infinite_presented_group() -> None:
    r"""The cokernel of 2:Z -> Z is Z/2, with its chosen quotient map.

    The map Z -> C2 kills the image, so it descends through this actual
    quotient, retaining the original free-group source and projection.
    """
    free, two = Groups.Free(1), Groups.C(2)
    label = next(iter(free.free_basis()))
    generator = free.free_generator(label)
    involution = next(iter(two.group_generators()))
    squaring = free.Mor(free)({label: generator**2})
    quotient = squaring.cokernel()
    projection = squaring.cokernel_projection()
    reduction = free.Mor(two)({label: involution})
    descent = quotient.descend_homomorphism(reduction, through=projection)

    assert quotient in GroupsWithChosenFinitePresentation()
    assert projection.domain() is free and projection.codomain() is quotient
    assert projection(generator**2) == quotient.one()
    assert descent.domain() is quotient and descent.codomain() is two
    assert descent(projection(generator)) == involution
    assert descent * projection == reduction


def test_reduction_then_inclusion_c4_to_c2_to_c4_is_the_squaring_endomorphism() -> None:
    r"""$C_4 \to C_2 \to C_4$, $g \mapsto h \mapsto g^2$, is $x \mapsto x^2$; its square is trivial since $x^4 = 1$."""
    c4 = Groups.C(4)
    c2 = Groups.C(2)
    (g,) = c4.group_generators()
    (h,) = c2.group_generators()
    reduction = c4.Mor(c2)({g: h})
    inclusion = c2.Mor(c4)({h: g**2})
    squaring = inclusion * reduction

    assert squaring(g) == g**2
    assert squaring(g**3) == g**2
    assert squaring.kernel().order() == 2
    assert squaring.image().order() == 2
    assert (squaring * squaring)(g) == c4.one()


def test_automorphism_groups_of_c4_c5_v4_and_s3() -> None:
    r"""$\operatorname{Aut}(C_n) \cong (\mathbb{Z}/n)^\times$; $\operatorname{Aut}(V_4) \cong \operatorname{GL}_2(\mathbb{F}_2) \cong S_3$; $\operatorname{Aut}(S_3) = \operatorname{Inn}(S_3) \cong S_3$ (Dummit--Foote 4.4)."""
    assert Groups.C(4).Aut().order() == 2
    assert Groups.C(5).Aut().is_isomorphic_to(Groups.C(4))
    assert Groups.V4().Aut().is_isomorphic_to(Groups.S(3))
    assert Groups.S(3).Aut().is_isomorphic_to(Groups.S(3))
