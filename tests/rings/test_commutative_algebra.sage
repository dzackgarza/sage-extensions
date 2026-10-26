r"""Commutative algebra: spectra, localization, completion, ideals and modules."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_localizing_a_polynomial_ring_over_a_nondomain_retains_the_inverse_map() -> None:
    r"""For R=Z/4, R[x,x^-1]=R[x,t]/(xt-1), without domain hypotheses."""
    R = ZZ.quotient_ring(ZZ.ideal(4))
    ring = R["x"]
    x = ring.algebra_generator("x")
    localized = ring.localization(x)
    numerator = localized.fraction(x)
    inverse = localized.fraction(ring.one(), x)
    assert numerator * inverse == localized.one()
    assert localized.localization_source() is ring
    assert localized.localization_map()(x) == numerator
    assert localized._from_engine_element(localized._engine_element(inverse)) == inverse


def test_integer_residue_spectrum_counts_distinct_prime_divisors() -> None:
    assert Zmod(2).spectrum().cardinality() == 1
    assert Zmod(8).spectrum().cardinality() == 1
    assert Zmod(12).spectrum().cardinality() == 2
    assert Zmod(30).spectrum().cardinality() == 3


def test_finite_unit_localization_and_prime_localization_are_distinct() -> None:
    inverted_two = ZZ.localization(2)
    inverted_zero = ZZ.localization(0)
    assert inverted_two.localization_source() is ZZ
    assert tuple(inverted_two.inverted_elements()) == (ZZ(2),)
    assert inverted_two.localization_map()(ZZ(3)) == inverted_two(3)
    assert inverted_two(2).is_unit()
    assert inverted_two in AdditiveGroups().AdditiveCommutative()
    assert inverted_zero in AdditiveGroups().AdditiveCommutative()
    assert inverted_zero.is_zero() is True

    local_at_five = ZZ.localize_at_prime(5)
    rational = local_at_five.fraction_field()
    assert rational(1) / 2 in local_at_five
    assert rational(1) / 5 not in local_at_five
    assert local_at_five in LocalRings()
    assert local_at_five in AdditiveGroups().AdditiveCommutative()
    assert int(local_at_five.residue_field().cardinality()) == 5
    assert local_at_five.maximal_ideal() == local_at_five.ideal(local_at_five(5))


def test_polynomial_prime_localization_has_expected_residue_field() -> None:
    field = GF(5)
    polynomial = field.polynomial_ring("t")
    t = polynomial.algebra_generator("t")
    local = polynomial.localize_at_prime(polynomial.ideal(t))
    fraction = local.fraction_field()

    assert fraction((t + 1) / (t**2 + 1)) in local
    assert fraction(1 / t) not in local
    assert int(local.residue_field().cardinality()) == 5


def test_quotient_residue_field_dual_numbers_and_adic_completion() -> None:
    field = GF(5)
    polynomial = field.polynomial_ring("t")
    t = polynomial.algebra_generator("t")

    quotient = polynomial.quotient_ring(t**2)
    tbar = quotient.quotient_map()(t)
    assert quotient.characteristic().parent() is ZZ
    assert quotient.characteristic() == 5
    assert tbar != 0
    assert tbar**2 == 0

    residue = polynomial.quotient_ring(t)
    assert residue in LocalRings()
    assert int(residue.cardinality()) == 5

    dual = field.dual_numbers()
    epsilon = dual.algebra_generator("epsilon")
    assert dual in LocalRings()
    assert dual in ArtinianRings()
    assert epsilon != 0
    assert epsilon**2 == 0
    assert dual.residue_field() is field

    completion = polynomial.adic_completion(polynomial.ideal(t), precision=8)
    assert completion in CompleteLocalRings()
    assert completion.completion_source() is polynomial
    assert completion.computation_precision() == 8
    assert int(completion.residue_field().cardinality()) == 5


def test_formal_power_series_ring_is_complete_local_over_a_field() -> None:
    field = GF(7)
    power_series = field.power_series_ring("t")

    assert power_series in CompleteLocalRings()
    assert power_series.residue_field() is field
    (uniformizer,) = power_series.maximal_ideal().ideal_generators()
    assert uniformizer == power_series.power_series_variable()


def test_affine_prime_spectrum_zariski_basis_and_structure_sheaf_stalks() -> None:
    r"""On Spec Q[x]: the generic point specializes to (x); (x) lies in V(x) and not
    in D(x); O(D(x)) = Q[x][1/x]; O is a sheaf for {D(x), D(1-x)}; O_(x) = Q[x]_(x)
    (Hartshorne II.2.2)."""
    ring = QQ['x']
    x = ring.algebra_generator("x")
    spectrum = ring.spectrum()
    line = ring.affine_spectrum()

    generic = spectrum.generic_point()
    origin = spectrum(ring.ideal(x))
    assert generic.specializes_to(origin)
    assert not origin.specializes_to(generic)
    assert origin in spectrum.V(x)
    assert generic not in spectrum.V(x)
    assert origin not in spectrum.D(x)
    assert generic in spectrum.D(x)

    sheaf = line.structure_sheaf()
    sections = sheaf.sections_on_distinguished_open(spectrum.D(x))
    assert sections(x).is_unit()
    assert not sections(x - 1).is_unit()
    cover = line.distinguished_open_cover(x, 1 - x)
    assert sheaf in cover.coverage().sheaves(Modules(ring))

    stalk = sheaf.stalk(origin)
    assert stalk in LocalRings()
    assert stalk.residue_field().characteristic() == 0
    assert not stalk(x).is_unit()
    assert stalk(x + 1).is_unit()


def test_polynomial_ideals_are_module_subobjects_with_singular_arithmetic() -> None:

    ring = QQ.polynomial_ring(("x", "y"))
    x, y = ring.algebra_generators()
    ideal = ring.ideal(x**2, x * y)
    other = ring.ideal(y)

    subobjects = Modules(ring).Subobjects(ring.regular_module())
    assert ideal in subobjects
    assert ideal.inclusion().codomain() is ring.regular_module()
    assert ideal.inclusion().is_injective()
    assert ideal == ring.ideal(ring(x**2), ring(x * y))

    def same_ideal(left, right):
        return all(generator in right for generator in left.ideal_generators()) and all(
            generator in left for generator in right.ideal_generators()
        )

    assert same_ideal(ideal.radical(), ring.ideal(x))
    assert same_ideal(ideal.sum(other), ring.ideal(x**2, x * y, y))
    assert same_ideal(ideal.product(other), ring.ideal(x**2 * y, x * y**2))
    assert same_ideal(ideal.intersection(other), ring.ideal(x * y))


def test_special_fiber_of_xy_equals_t_is_the_node_with_its_local_ring_at_the_origin() -> None:
    r"""The family xy = t over Q[t] is a surface; its fiber over t = 0 is the node
    xy = 0, a curve whose origin (x, y) is maximal, with x, y nonunits and x+1, y+1
    units in the local ring there."""
    parameter = QQ['t']
    t = parameter.algebra_generator("t")
    plane = parameter['x,y']
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    family = plane.quotient_by_relations((x * y - t,))
    assert family.krull_dimension() == 2

    fiber = family.quotient_ring(family.ideal(family.algebra_structure_morphism()(t)))
    to_fiber = fiber.quotient_map()
    x0 = to_fiber(family.algebra_generator("x"))
    y0 = to_fiber(family.algebra_generator("y"))
    assert fiber.krull_dimension() == 1
    assert x0 * y0 == fiber.zero()
    assert x0 != fiber.zero()
    origin = fiber.ideal(x0, y0)
    assert origin.is_maximal()

    local = fiber.localize_at_prime(origin)
    assert not local(x0).is_unit()
    assert not local(y0).is_unit()
    assert local(x0 + 1).is_unit()
    assert local(y0 + 1).is_unit()
    assert local.residue_map()(local(x0)) == local.residue_field().zero()


def test_affine_spec_is_contravariant_on_commutative_algebra_maps() -> None:
    r"""Spec is a contravariant functor: Spec(g f) = Spec(f) Spec(g) and Spec(id) = id,
    for f: Q[x] -> Q[t], x -> t^2 and g: Q[t] -> Q[u], t -> u + 1."""
    source = QQ['x']
    middle = QQ['t']
    target = QQ['u']
    t = middle.algebra_generator("t")
    u = target.algebra_generator("u")
    first = source.Mor(middle)({"x": t**2})
    second = middle.Mor(target)({"t": u + 1})

    spec = Algebras(QQ).Associative().Unital().Commutative().spectrum()
    assert spec(second * first) == spec(first) * spec(second)
    assert spec(source.Mor(source).identity()) == spec(source).categorical_identity_morphism()
    assert spec(second * first) != spec(first) * spec(middle.Mor(target)({"t": u}))


def test_commutative_algebra_pushout_imposes_common_source_relations() -> None:
    common = QQ.polynomial_ring("s")
    left = QQ.polynomial_ring("x")
    right = QQ.polynomial_ring("y")
    s = common.algebra_generator("s")
    x = left.algebra_generator("x")
    y = right.algebra_generator("y")
    left_span = common.Mor(left)({"s": x**2})
    right_span = common.Mor(right)({"s": y**3})

    pushout = Algebras(QQ).Associative().Unital().Commutative().pushout(left_span, right_span)
    left_map, right_map = pushout.pushout_maps()
    assert left_map(x) ** 2 == right_map(y) ** 3

    target = QQ.polynomial_ring("t")
    t = target.algebra_generator("t")
    left_cocone = left.Mor(target)({"x": t**3})
    right_cocone = right.Mor(target)({"y": t**2})
    induced = pushout.from_pushout_cocone(left_cocone, right_cocone)
    assert induced(left_map(x)) == t**3
    assert induced(right_map(y)) == t**2
    assert left_cocone(left_span(s)) == right_cocone(right_span(s)) == t**6


def test_module_local_fiber_rank_generic_rank_and_fitting_loci() -> None:
    r"""For M = Q[x]/(x): generic rank 0, fiber rank 1 at (x), Fitt_0(M) = Ann(M) = (x),
    Supp M = {(x)}; Q[x]^2 has rank 2 at every point."""
    ring = QQ['x']
    x = ring.algebra_generator("x")
    module = Modules(ring).direct_sum_of_cyclics((x,))
    spectrum = ring.spectrum()
    generic = spectrum.generic_point()
    origin = spectrum(ring.ideal(x))

    assert module.generic_rank() == 0
    assert module.rank_at(generic) == 0
    assert module.rank_at(origin) == 1
    assert module.fitting_ideal(0) == ring.ideal(x)
    assert module.annihilator() == ring.ideal(x)
    assert origin in module.support()
    assert generic not in module.support()
    assert spectrum(ring.ideal(x - 1)) not in module.support()
    assert module.localize_at_prime(origin).minimal_number_of_generators() == 1

    free_rank_two = ring.free_module(2)
    assert free_rank_two.generic_rank() == 2
    assert free_rank_two.rank_at(origin) == 2


def test_annihilators_and_fiber_ranks_of_integer_modules() -> None:
    r"""Ann(Z/6) = (6), Ann(Z) = 0, Ann(0) = Z; dim_{F_p} (Z/6) (x) F_p is 1 at p = 2, 3
    and 0 at p = 5."""
    torsion = Modules(ZZ).direct_sum_of_cyclics((6,))
    assert torsion.annihilator() == ZZ.ideal(6)
    assert ZZ.free_module(1).annihilator() == ZZ.ideal(0)
    assert Modules(ZZ).zero_object().annihilator() == ZZ.ideal(1)
    assert torsion.rank_at(ZZ.spectrum()(2)) == 1
    assert torsion.rank_at(ZZ.spectrum()(3)) == 1
    assert torsion.rank_at(ZZ.spectrum()(5)) == 0


def test_localized_cyclic_module_vanishes_exactly_when_its_ideal_meets_the_inverted_set() -> None:
    r"""S^{-1}(R/I) = 0 iff I meets S: (Q[x]/(x^2))[1/x] = 0, (Q[x]/(x+1))[1/x] != 0;
    at the prime (x) of Q[x,y], Q[x,y]/(x) survives and Q[x,y]/(y) dies;
    (Z/6)_(2) != 0 and (Z/6)_(5) = 0 (Atiyah-Macdonald 3.1-3.3)."""
    line = QQ['x']
    x = line.algebra_generator("x")
    inverted_x = line.localization(x)
    assert Modules(line).direct_sum_of_cyclics((x**2,)).localize(inverted_x).is_zero()
    assert not Modules(line).direct_sum_of_cyclics((x + 1,)).localize(inverted_x).is_zero()

    plane = QQ['x,y']
    xp = plane.algebra_generator("x")
    yp = plane.algebra_generator("y")
    point = plane.spectrum()(plane.ideal(xp))
    assert not Modules(plane).direct_sum_of_cyclics((xp,)).localize_at_prime(point).is_zero()
    assert Modules(plane).direct_sum_of_cyclics((yp,)).localize_at_prime(point).is_zero()

    six = Modules(ZZ).direct_sum_of_cyclics((6,))
    assert not six.localize_at_prime(ZZ.spectrum()(2)).is_zero()
    assert six.localize_at_prime(ZZ.spectrum()(5)).is_zero()


def test_z_mod_six_with_two_inverted_is_z_mod_three() -> None:
    r"""(Z/6)[1/2] = Z/3: the class of 3 dies (2 * 3 = 0), 1 survives, and 1/2 = 2."""
    module = Modules(ZZ).direct_sum_of_cyclics((6,))
    one = module.module_generator(0)
    localized = module.localize(ZZ.localization(2))

    assert localized.cardinality() == 3
    assert localized.fraction(3 * one) == localized.zero()
    assert localized.fraction(one) != localized.zero()
    assert localized.fraction(one, 2) == localized.fraction(2 * one)


def test_ideal_localization_extension_contraction_colon_and_saturation() -> None:
    integer_ideal = ZZ.ideal(6)
    inverted_two = ZZ.localization(2)
    extended_integer_ideal = integer_ideal.extension_to_localization(inverted_two)

    assert extended_integer_ideal.inclusion().is_injective()
    assert 3 in extended_integer_ideal
    assert 1 not in extended_integer_ideal
    assert extended_integer_ideal.contraction() == ZZ.ideal(ZZ(3))

    ring = QQ.polynomial_ring(("x", "y"))
    x, y = ring.algebra_generators()
    ideal = ring.ideal(x * y, y**2)
    divisor = ring.ideal(x)

    assert ideal.colon(divisor) == ring.ideal(ring(y))
    assert ideal.saturation(divisor) == ring.ideal(ring(y))

    localized_ring = ring.localization(x)
    extended = ideal.extension_to_localization(localized_ring)
    assert extended.inclusion().is_injective()
    assert localized_ring(y) in extended
    assert localized_ring.one() not in extended
    assert extended.contraction() == ring.ideal(ring(y))


def test_quotient_localization_comparison_is_an_actual_ring_isomorphism() -> None:
    quotient = ZZ.quotient_ring(ZZ.ideal(6))
    localization = ZZ.localization(2)
    comparison = quotient.localization_comparison(localization)

    left = comparison.localized_quotient()
    right = comparison.quotient_after_localization()
    forward = comparison.forward()
    inverse = comparison.inverse()
    quotient_map = quotient.quotient_map()

    half = left.fraction(quotient_map(1), quotient_map(2))
    assert forward(half) == right(localization(1) / 2)
    assert inverse(forward(half)) == half

    right_half = right(localization(1) / 2)
    assert forward(inverse(right_half)) == right_half
    assert comparison.extended_ideal().contraction() == ZZ.ideal(ZZ(3))

    ring = QQ.polynomial_ring(("x", "y"))
    x, y = ring.algebra_generators()
    polynomial_quotient = ring.quotient_ring(ring.ideal(x * y, y**2))
    polynomial_localization = ring.localization(x)
    polynomial_comparison = polynomial_quotient.localization_comparison(
        polynomial_localization
    )
    polynomial_left = polynomial_comparison.localized_quotient()
    polynomial_right = polynomial_comparison.quotient_after_localization()
    polynomial_quotient_map = polynomial_quotient.quotient_map()

    assert polynomial_left(polynomial_quotient_map(y)) == polynomial_left.zero()
    assert polynomial_comparison.forward()(
        polynomial_left(polynomial_quotient_map(y))
    ) == polynomial_right.zero()
    element = polynomial_right(polynomial_localization(y + 1))
    assert polynomial_comparison.forward()(
        polynomial_comparison.inverse()(element)
    ) == element


def test_selected_presented_algebra_localization_has_exact_fraction_equality() -> None:

    presentation = QQ.polynomial_ring(("x", "y"))
    x, y = presentation.algebra_generators()
    axes = (presentation).quotient_by_relations((x * y,))
    xbar = axes.algebra_generator("x")
    ybar = axes.algebra_generator("y")
    localized = axes.localization(xbar)

    # In A_x for A = k[x,y]/(xy), x is invertible and therefore y vanishes.
    assert localized(ybar) == localized.zero()
    assert localized(xbar) != localized.zero()
    assert localized.one() != localized.zero()

    origin = axes.ideal(xbar, ybar)
    localized_origin = origin.extension_to_localization(localized)
    assert localized_origin.contraction() == axes.ideal(axes.one())
    assert localized_origin.contains_ambient_element(localized.one())

    squared_x = axes.ideal(xbar**2)
    radical = squared_x.radical()
    assert radical.contains_ambient_element(xbar)
    assert radical == axes.ideal(xbar)


def test_fitting_ideals_commute_with_selected_presented_localization() -> None:
    presentation = QQ.polynomial_ring(("x", "y"))
    x, y = presentation.algebra_generators()
    axes = (presentation).quotient_by_relations((x * y,))
    xbar = axes.algebra_generator("x")
    ybar = axes.algebra_generator("y")
    omega = axes.kahler_differentials()

    assert omega.fitting_ideal(1) == axes.ideal(xbar, ybar)

    localized = axes.localization(xbar)
    localized_omega = omega.localize(localized)
    localized_fitting = localized_omega.fitting_ideal(1)

    # Fitt_1(Omega)_x = (x,y)A_x = A_x because x is inverted.
    assert localized_fitting.contraction() == axes.ideal(axes.one())
    assert localized_fitting.contains_ambient_element(localized.one())


def test_localization_commutes_with_cokernels() -> None:
    r"""Localization is exact, so S^{-1} coker(6: Z -> Z) = coker(6: Z[1/2] -> Z[1/2]),
    both Z/3 (Atiyah-Macdonald 3.3)."""
    inverted_two = ZZ.localization(2)
    free = ZZ.free_module(1)
    multiplication_by_six = free.Mor(free)({0: 6 * free.module_generator(0)})

    functor = inverted_two.localization_functor()
    assert functor.is_exact()
    comparison = functor.cokernel_comparison(multiplication_by_six)
    assert comparison.domain().cardinality() == 3
    assert comparison.codomain().cardinality() == 3
    assert comparison.forward().is_injective()
    assert comparison.forward().is_surjective()


def test_nakayama_minimal_generators_and_surjectivity_are_local_module_operations() -> None:
    r"""Over R = Q[x]_(x) and M = R/(x): mu(M) = dim M/mM = 1; R -> M is surjective
    (surjective mod m, Nakayama) while multiplication by x on R is not
    (Atiyah-Macdonald 2.8)."""
    ring = QQ['x']
    x = ring.algebra_generator("x")
    local = ring.spectrum()(ring.ideal(x)).local_ring()
    quotient = Modules(local).direct_sum_of_cyclics((local(x),))

    assert quotient.minimal_number_of_generators() == 1
    assert quotient.residue_module().dimension() == 1

    free = local.free_module(1)
    projection = free.Mor(quotient)({0: quotient.module_generator(0)})
    assert projection.is_surjective_by_nakayama()
    assert projection.is_surjective()

    multiplication_by_x = free.Mor(free)({0: local(x) * free.module_generator(0)})
    assert not multiplication_by_x.is_surjective_mod_maximal_ideal()
    assert not multiplication_by_x.is_surjective_by_nakayama()


def test_map_induced_out_of_a_localization_is_independent_of_the_representative() -> None:
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    inverted = ring.localization(x)
    assert inverted.inverted_element() == x

    to_fractions = ring.fraction_field_map()
    induced = inverted.induced_morphism(to_fractions)

    over_x = inverted.fraction(ring.one(), x)
    over_x_squared = over_x * inverted.fraction(x, x)
    assert over_x == over_x_squared
    assert induced(over_x) == induced(over_x_squared)

    assert induced(inverted.localization_map()(x + 1)) == to_fractions(x + 1)
    assert induced(over_x) * to_fractions(x) == to_fractions(ring.one())

    # A rational constant is an element of QQ[x][1/x] like any other, and the
    # induced map sends it where the universal property says: 1/2 to 1/2.
    half = inverted(ring.one() / ring(2))
    assert induced(half) * to_fractions(ring(2)) == to_fractions(ring.one())

    plane = QQ.polynomial_ring(("x", "y"))
    x_plane, y_plane = plane.algebra_generators()
    inverted_plane = plane.localization(x_plane, y_plane)
    plane_to_fractions = plane.fraction_field_map()
    plane_induced = inverted_plane.induced_morphism(plane_to_fractions)

    assert plane_induced(inverted_plane.localization_map()(x_plane + y_plane)) == (
        plane_to_fractions(x_plane + y_plane)
    )
    inverse_product = inverted_plane.fraction(plane.one(), x_plane * y_plane)
    assert plane_induced(inverse_product) * plane_to_fractions(x_plane * y_plane) == (
        plane_to_fractions(plane.one())
    )


def test_integer_localization_universal_map_factors_exactly_when_two_becomes_a_unit() -> None:
    inverted_two = ZZ.localization(2)
    to_rationals = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    factor = inverted_two.induced_morphism(to_rationals)
    half = inverted_two.fraction(ZZ.one(), ZZ(2))

    assert factor.domain() is inverted_two
    assert factor.codomain() is QQ
    assert factor * inverted_two.localization_map() == to_rationals
    assert factor(half) == QQ(1) / QQ(2)

    with pytest.raises(ValueError):
        inverted_two.induced_morphism(ZZ.Mor(ZZ).identity())


def test_affine_and_projective_plane_over_f5_have_the_textbook_point_counts_and_zeta_functions() -> None:
    r"""#A^2(F_{q^n}) = q^{2n}, #P^2(F_{q^n}) = 1 + q^n + q^{2n}; Z(A^2) = 1/(1-q^2 T),
    Z(P^2) = 1/((1-T)(1-qT)(1-q^2T)) (Hartshorne, Appendix C, Ex. 1.1)."""
    field = GF(5)
    affine_plane = AffineSpaces(field)(2)
    projective_plane = ProjectiveSpaces(field)(2)

    affine_counts = affine_plane.point_counts(3)
    assert (affine_counts[0], affine_counts[1], affine_counts[2]) == (25, 625, 15625)
    projective_counts = projective_plane.point_counts(3)
    assert (projective_counts[0], projective_counts[1], projective_counts[2]) == (31, 651, 15751)

    affine_zeta = affine_plane.zeta_function()
    (T,) = affine_zeta.parent().algebra_generators()
    assert affine_zeta == 1 / (1 - 25 * T)

    projective_zeta = projective_plane.zeta_function()
    (T,) = projective_zeta.parent().algebra_generators()
    assert projective_zeta == 1 / ((1 - T) * (1 - 5 * T) * (1 - 25 * T))


def test_commutative_algebra_coproduct_of_two_polynomial_rings_is_the_polynomial_ring_in_two_variables() -> None:
    r"""In commutative Q-algebras, Q[x] + Q[y] = Q[x] (x)_Q Q[y] = Q[x, y]; the copairing
    of x -> t, y -> t^2 sends x to t and y to t^2."""
    left = QQ['x']
    right = QQ['y']
    coproduct = Algebras(QQ).Associative().Unital().Commutative().coproduct((left, right))
    left_map, right_map = coproduct.coproduct_injections()
    x = left.algebra_generator("x")
    y = right.algebra_generator("y")

    assert coproduct.krull_dimension() == 2
    assert left_map(x) * right_map(y) != right_map(y) * right_map(y)

    plane = QQ['x,y']
    comparison = coproduct.from_cocone(
        left.Mor(plane)({"x": plane.algebra_generator("x")}),
        right.Mor(plane)({"y": plane.algebra_generator("y")}),
    )
    assert comparison.is_injective()
    assert comparison.is_surjective()

    line = QQ['t']
    s = line.algebra_generator("t")
    induced = coproduct.from_cocone(left.Mor(line)({"x": s}), right.Mor(line)({"y": s**2}))
    assert induced(left_map(x)) == s
    assert induced(right_map(y)) == s**2
    assert induced(left_map(x) * right_map(y)) == s**3
