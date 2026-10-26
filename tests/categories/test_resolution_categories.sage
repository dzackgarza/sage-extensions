r"""Chosen resolution categories and their classifier projections.

Sources: Weibel, An Introduction to Homological Algebra, 2.2 and 8.6; the
degree-one integer examples are the standard free resolutions of cyclic
modules.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_6_finite_presentation_is_a_degree_one_resolution_object() -> None:
    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6)))
    resolutions = Modules(ZZ).FinitelyPresented().resolution_category()
    resolution = resolutions.from_selected_presentation(M)

    assert resolution is M.selected_module_resolution()
    assert resolutions.target_functor()(resolution) is M
    assert resolution.truncation() == 1
    assert resolution.level(0) in FinitelyGeneratedFreeModules(ZZ)
    assert resolution.level(1) in FinitelyGeneratedFreeModules(ZZ)
    assert resolution.differential(1) == M.presentation()
    assert resolution.augmentation().codomain() is M


def test_q_as_a_z_module_has_a_canonical_degree_zero_resolution_without_being_finitely_generated() -> None:
    Q = QQ.regular_module().restrict_scalars(ZZ.fraction_field_map())
    resolutions = Modules(ZZ).resolutions(0)
    resolution = resolutions.comonadic(
        Sets().free_module_adjunction(ZZ),
        Q,
    )

    assert resolution.target() is Q
    assert resolution.level(0) in Modules(ZZ).Projective()
    assert resolution.augmentation().codomain() is Q
    assert Q not in Modules(ZZ).FinitelyGenerated()


def test_q_as_a_z_module_has_the_infinite_canonical_comonadic_resolution() -> None:
    Q = QQ.regular_module().restrict_scalars(ZZ.fraction_field_map())
    resolutions = Modules(ZZ).resolutions(omega0)
    resolution = resolutions.comonadic(
        Sets().free_module_adjunction(ZZ),
        Q,
    )

    assert resolution.target() is Q
    assert resolution.truncation() is omega0
    assert resolution.level(0) in Modules(ZZ).Projective()
    assert resolution.level(3) in Modules(ZZ).Projective()
    assert resolution.length() is omega0


def test_infinite_module_resolution_category_represents_length_zero_chain_data() -> None:
    free = ZZ.free_module(("e",))
    resolutions = Resolutions(
        Modules(ZZ),
        Modules(ZZ).Projective(),
        omega0,
        Modules(ZZ).Free(),
    ).dold_kan_image()
    resolution = resolutions.constant(free)

    assert resolution.truncation() is omega0
    assert resolution.length() == 0
    assert resolution.level(0) is free
    assert resolution.level(4).is_zero()


def test_one_generator_polynomial_algebra_resolution_transports_to_its_monomial_module_resolution() -> None:
    algebra = ZZ.free_module(("x",)).symmetric_algebra()
    owner = algebra.algebra_framing_owner()
    algebra_resolutions = Resolutions(owner, SymmetricAlgebras(ZZ), 0)
    algebra_resolution = algebra_resolutions.from_selected_framing(algebra, owner)

    forget = owner.underlying_module()
    module_resolutions = Resolutions(
        Modules(ZZ),
        Modules(ZZ).Projective(),
        0,
        Modules(ZZ).Free(),
    ).dold_kan_image()
    transport = algebra_resolutions.transport_degree_zero(
        forget,
        module_resolutions,
    )
    module_resolution = transport(algebra_resolution)

    assert module_resolution.target() is algebra
    assert module_resolution.level(0) in Modules(ZZ).Free()
    assert module_resolution.augmentation().domain() is algebra
    assert module_resolution.augmentation().codomain() is algebra


def test_presented_algebra_stores_its_chosen_presentation_as_a_resolution() -> None:
    presentation_ring = ZZ.free_module(("x",)).symmetric_algebra()
    algebra = presentation_ring.quotient_by_relations((presentation_ring.algebra_generator("x") ** 2,))
    selected = algebra.selected_algebra_resolution()
    resolutions = (
        Algebras(ZZ)
        .Associative()
        .Unital()
        .FinitelyPresentedAsAlgebra()
        .resolution_category()
    )

    assert selected.resolution_category() is resolutions
    assert selected.truncation() == 1
    assert selected.level(0) is algebra.presentation_ring()
    assert selected.augmentation() is algebra.algebra_presentation_morphism()
    assert selected.relations() is algebra.relations()


def test_a_framed_free_module_is_a_length_zero_resolution() -> None:
    free = ZZ.free_module(("e",))
    selected = free.selected_module_resolution()
    finite_presentations = Modules(ZZ).FinitelyPresented().resolution_category()

    assert selected.resolution_category() is finite_presentations
    assert selected.truncation() == 1
    assert selected.length() == 0
    assert selected.level(0) is free
    assert selected.level(1).is_zero()

    resolutions = Resolutions(
        Modules(ZZ),
        Modules(ZZ).Projective(),
        2,
        Modules(ZZ).Free(),
    ).dold_kan_image()
    resolution = resolutions.constant(free)

    assert resolution.target() is free
    assert resolution.length() == 0
    assert resolution.level(0) is free
    assert resolution.level(1).is_zero()
    assert resolution.level(2).is_zero()


def test_two_resolutions_of_z_mod_6_are_compared_over_the_same_target() -> None:
    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6)))
    resolutions = Modules(ZZ).FinitelyPresented().resolution_category()
    minimal = resolutions.from_selected_presentation(M)

    F0 = ZZ.free_module(("a", "b"))
    F1 = ZZ.free_module(("r", "s"))
    a = F0.module_generator("a")
    b = F0.module_generator("b")
    generator = M.module_generator(0)
    augmentation = F0.Mor(M)({"a": generator, "b": M.zero()})
    differential = F1.Mor(F0)({"r": 6 * a, "s": b})
    redundant = resolutions.chain(
        M,
        {0: F0, 1: F1},
        {1: differential},
        augmentation,
        length=1,
    )

    source_zero = minimal.level(0)
    source_one = minimal.level(1)
    zero_label = next(iter(source_zero.module_generating_set()))
    one_label = next(iter(source_one.module_generating_set()))
    degree_zero = source_zero.Mor(F0)({zero_label: a})
    lifted_relation = differential.preimage(
        degree_zero(
            minimal.differential(1)(source_one.module_generator(one_label))
        )
    )
    degree_one = source_one.Mor(F1)({one_label: lifted_relation})
    identity = M.module_category().Mor(M, M).identity()
    comparison = resolutions.Mor(minimal, redundant)(
        {0: degree_zero, 1: degree_one},
        target_morphism=identity,
    )

    assert minimal is not redundant
    assert minimal.target() is M
    assert redundant.target() is M
    assert comparison.target_morphism() == identity
