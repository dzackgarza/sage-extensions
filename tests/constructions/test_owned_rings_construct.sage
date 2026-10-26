r"""The integers expose the foundational owned-ring constructions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_ring_exposes_fraction_module_polynomial_and_matrix_constructions() -> None:
    polynomials = ZZ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    laurent = ZZ.laurent_polynomial_ring("t")
    t = laurent.algebra_generator("t")
    series = ZZ.power_series_ring("q")
    q = series.power_series_variable()
    matrices = ZZ.matrix_space(2)
    module = ZZ.free_module(2)

    assert ZZ in OwnedRings()
    assert ZZ.cardinality() == aleph0
    assert ZZ.fraction_field() is QQ
    assert ZZ.fraction_field() in OwnedOrderedRings()
    assert module.module_rank() == 2
    assert x in polynomials
    assert t * t**-1 == laurent.one()
    assert q.coefficient(1) == ZZ.one()
    assert matrices.identity_matrix().determinant() == ZZ.one()
    assert ZZ.is_central(ZZ(2))
    assert ZZ.regular_module().module_rank() == 1
    assert ZZ.unit_group().order() == 2
    assert ZZ.Mor(QQ).cardinality() == cardinal(1)


def test_native_ring_and_extension_constructions_retain_the_additive_group_spine() -> None:
    r"""Ring, polynomial, quotient and fraction-field owners construct additive groups."""
    polynomials = QQ.polynomial_ring("x")
    quotient = polynomials.quotient_ring(polynomials.ideal(polynomials.algebra_generator("x") ** 2 - 2))
    zero_quotient = polynomials.quotient_ring(polynomials.unit_ideal())
    quotient_fraction_field = quotient.fraction_field()
    fraction_field = polynomials.fraction_field()
    fraction_map = polynomials.fraction_field_map()
    quotient_fraction_map = quotient.fraction_field_map()

    additive_groups = AdditiveGroups().AdditiveCommutative()
    assert OwnedRings().is_subcategory(additive_groups)
    assert OwnedRings().Commutative().is_subcategory(additive_groups)
    assert ZZ in additive_groups
    assert polynomials in additive_groups
    assert polynomials in OwnedRings().Commutative()
    assert polynomials in OwnedIntegralDomains()
    assert polynomials in OwnedRings().Noetherian()
    assert polynomials.is_framed_algebra()
    assert polynomials.algebra_framing_source() is polynomials
    assert polynomials.algebra_framing_morphism().domain() is polynomials
    assert polynomials.algebra_framing_morphism().codomain() is polynomials
    assert polynomials.algebra_framing_morphism() is polynomials.Mor(polynomials).identity()
    polynomial_module = Modules.ParentMethods._native_module_presentation(polynomials)
    assert polynomial_module is not None
    assert polynomial_module.base_ring() is QQ
    assert polynomial_module.module_basis().is_basis()
    basis_label = polynomial_module.module_basis().source().module_generating_set().an_element()
    assert polynomial_module.module_basis().image(basis_label) in polynomials
    assert quotient in additive_groups
    assert quotient in OwnedRings().Commutative()
    assert quotient in OwnedIntegralDomains()
    quotient_module = Modules.ParentMethods._native_module_presentation(quotient)
    assert quotient_module is not None
    assert quotient_module.module() is quotient
    assert quotient_module.base_ring() is quotient.base_ring()
    assert quotient_module.unit() == quotient.one()
    assert quotient_module.multiplication().codomain() is quotient
    quotient_basis_coordinates = quotient_module.module_basis().coordinates(quotient.one())
    assert len(quotient_basis_coordinates) == 1
    assert next(iter(quotient_basis_coordinates.values())) == quotient.base_ring().one()
    quotient_generator_coordinates = quotient_module.module_basis().coordinates(
        quotient.quotient_map()(polynomials.algebra_generator("x"))
    )
    assert quotient_generator_coordinates == {1: quotient.base_ring().one()}
    assert quotient_fraction_field in additive_groups
    assert quotient_fraction_field in OwnedRings().Division().Commutative()
    assert quotient_fraction_field.fraction_field_localization().localization_source() is quotient
    assert quotient_fraction_map.domain() is quotient
    assert quotient_fraction_map.codomain() is quotient_fraction_field
    quotient_fraction_module = Modules.ParentMethods._native_module_presentation(
        quotient_fraction_field
    )
    assert quotient_fraction_module is not None
    assert quotient_fraction_module.module() is quotient_fraction_field
    assert quotient_fraction_module.base_ring() is quotient_fraction_field.base_ring()
    assert quotient_fraction_module.unit() == quotient_fraction_field.one()
    quotient_generator = quotient.quotient_map()(polynomials.algebra_generator("x"))
    assert quotient_fraction_map(quotient_generator) ** 2 == quotient_fraction_field(2)
    assert zero_quotient in additive_groups
    assert zero_quotient.is_zero() is True
    assert zero_quotient.quotient_source() is polynomials
    assert fraction_field in additive_groups
    assert fraction_field.fraction_field_localization() in additive_groups
    assert fraction_field in OwnedRings().Division().Commutative()
    assert fraction_field in OwnedIntegralDomains()
    assert fraction_field in OwnedRings().Noetherian()
    assert fraction_field.base_ring() is QQ
    assert fraction_map.domain() is polynomials
    assert fraction_map.codomain() is fraction_field
    localization = polynomials.fraction_field_localization()
    assert localization in additive_groups
    assert localization.localization_source() is polynomials
    localization_module = Modules.ParentMethods._native_module_presentation(localization)
    assert localization_module is not None
    assert localization_module.module() is localization
    assert localization_module.base_ring() is localization.base_ring()
    assert localization_module.unit() == localization.one()
    punctured = polynomials.localization(polynomials.algebra_generator("x"))
    punctured_module = Modules.ParentMethods._native_module_presentation(punctured)
    assert punctured_module is not None
    assert punctured_module.module() is punctured
    assert punctured_module.base_ring() is punctured.base_ring()
    assert punctured_module.unit() == punctured.one()
    assert punctured.localization_source() is polynomials
    tensor_algebra = QQ.free_module(2).tensor_algebra()
    assert tensor_algebra in OwnedRings().NoZeroDivisors()
    assert tensor_algebra in OwnedRings().Nontrivial()
    assert tensor_algebra not in OwnedRings().Commutative()
    assert tensor_algebra not in OwnedIntegralDomains()
    assert tensor_algebra.is_framed_algebra()
    assert tensor_algebra.algebra_framing_source() is tensor_algebra
    assert tensor_algebra.algebra_framing_morphism() is tensor_algebra.Mor(tensor_algebra).identity()
    tensor_module = Modules.ParentMethods._native_module_presentation(tensor_algebra)
    assert tensor_module is not None
    assert tensor_module.module() is tensor_algebra
    assert tensor_module.base_ring() is QQ
    assert tensor_module.module_basis().is_basis()
    assert tensor_module.multiplication().codomain() is tensor_algebra
    assert tensor_module.unit() == tensor_algebra.one()


def test_cyclic_double_cover_presentation_has_square_equal_to_branch_coefficient() -> None:
    cover = QQ.cyclic_cover_presentation(QQ.one(), 2)
    z = cover.algebra_generator("z")

    assert z**2 == cover.one()


def test_predicate_subring_constructor_recovers_integers_inside_rationals() -> None:
    integers = QQ.predicate_subring(
        lambda element: element.denominator() == 1,
        "the denominator is one",
    )

    assert QQ(3) in integers
    assert QQ(1) / 2 not in integers
    native_module = Modules.ParentMethods._native_module_presentation(integers)
    assert native_module is not None
    assert native_module.module() is integers
    assert native_module.base_ring() is ZZ
    assert native_module.unit() == integers.one()
    assert native_module.multiplication().codomain() is integers
