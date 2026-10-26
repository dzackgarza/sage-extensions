r"""Ring constructions a mathematician expects, over every named ring.

Written from the mathematics: each test states what is true of the class of
rings it ranges over, and asks the session for it in the session's own words.
Nothing here was chosen because it currently builds; a red row is a dead end a
mathematician would hit in a notebook.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Placement: a ring is where its class says it is.
# ---------------------------------------------------------------------------


def test_every_ring_is_a_ring(ring) -> None:
    assert ring in Rings()
    assert ring in OwnedRings()


def test_commutative_rings_are_commutative(commutative_ring) -> None:
    assert commutative_ring in CommutativeRings()
    assert commutative_ring.is_commutative()


@pytest.mark.parametrize("name", ["M_2(QQ)", "M_2(ZZ)", "QQ<a,b>"])
def test_noncommutative_rings_are_not_commutative(build, name) -> None:
    ring = build(name)
    assert ring in Rings()
    assert ring not in CommutativeRings()


def test_integral_domains_are_integral_domains(integral_domain) -> None:
    assert integral_domain in IntegralDomains()
    assert integral_domain in NoetherianRings()


def test_dedekind_domains_are_noetherian_domains_of_dimension_at_most_one(dedekind_domain) -> None:
    assert dedekind_domain in IntegralDomains()
    assert dedekind_domain in NoetherianRings()
    assert dedekind_domain.krull_dimension() <= 1


def test_principal_ideal_domains_are_principal_ideal_domains(pid) -> None:
    assert pid in PrincipalIdealDomains()


def test_fields_are_fields(field) -> None:
    assert field in Fields()
    assert field in PrincipalIdealDomains()
    assert field in LocalRings()
    assert field in ArtinianRings()
    assert field.krull_dimension() == 0


def test_local_rings_are_local(local_ring) -> None:
    assert local_ring in LocalRings()
    assert local_ring.maximal_ideal() in CommutativeIdeals(local_ring)
    assert local_ring.residue_field() in Fields()


def test_complete_local_rings_are_complete_and_local(complete_local_ring) -> None:
    assert complete_local_ring in CompleteLocalRings()
    assert complete_local_ring in LocalRings()


def test_artinian_rings_are_artinian_of_dimension_zero(artinian_ring) -> None:
    assert artinian_ring in ArtinianRings()
    assert artinian_ring in NoetherianRings()
    assert artinian_ring.krull_dimension() == 0


def test_discrete_valuation_rings_are_local_principal_ideal_domains(discrete_valuation_ring) -> None:
    assert discrete_valuation_ring in LocalRings()
    assert discrete_valuation_ring in PrincipalIdealDomains()
    assert discrete_valuation_ring not in Fields()
    assert discrete_valuation_ring.krull_dimension() == 1


def test_maximal_orders_are_maximal_orders(maximal_order) -> None:
    assert maximal_order in OwnedOrders()
    assert maximal_order.is_maximal()
    assert maximal_order.krull_dimension() == 1


@pytest.mark.parametrize(
    "name", ["ZZ/12", "ZZ/8", "QQ[e]/(e^2)", "QQ[x]/(x^3)", "GF(2)[t]/(t^2)", "QQ[x,y]/(xy)"]
)
def test_non_domains_are_not_integral_domains(build, name) -> None:
    assert build(name) not in IntegralDomains()
    assert build(name) not in Fields()


@pytest.mark.parametrize(
    "name", ["ZZ[sqrt-5]", "ZZ[(1+sqrt-23)/2]", "ZZ[x]", "QQ[x,y]", "QQ[x,y]/(y^2-x^3)"]
)
def test_domains_that_are_not_principal_are_not_principal(build, name) -> None:
    assert build(name) in IntegralDomains()
    assert build(name) not in PrincipalIdealDomains()
    assert build(name) not in Fields()


@pytest.mark.parametrize("name", ["ZZ", "QQ[x]", "ZZ[i]", "ZZ[x]", "QQ[x,y]", "ZZ/12", "ZZ[sqrt-5]"])
def test_rings_with_several_maximal_ideals_are_not_local(build, name) -> None:
    assert build(name) not in LocalRings()


@pytest.mark.parametrize("name", ["QQ", "GF(5)"])
def test_prime_fields_are_prime_fields(build, name) -> None:
    assert build(name) in PrimeFields()


@pytest.mark.parametrize("name", ["GF(4)", "QQ(i)", "QQ_3", "RR"])
def test_proper_extensions_of_prime_fields_are_not_prime_fields(build, name) -> None:
    assert build(name) not in PrimeFields()


# ---------------------------------------------------------------------------
# Known invariants.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, dimension",
    [
        ("ZZ", 1),
        ("QQ", 0),
        ("GF(4)", 0),
        ("ZZ_3", 1),
        ("ZZ_(5)", 1),
        ("QQ[x]", 1),
        ("QQ[x,y]", 2),
        ("ZZ[x]", 2),
        ("ZZ[i]", 1),
        ("ZZ[sqrt-5]", 1),
        ("QQ[[t]]", 1),
        ("QQ[[x,y]]", 2),
        ("QQ[x,y]_(x,y)", 2),
        ("ZZ/12", 0),
        ("QQ[e]/(e^2)", 0),
        ("QQ[x,y]/(xy)", 1),
        ("QQ[x,y]/(y^2-x^3)", 1),
    ],
)
def test_krull_dimension(build, name, dimension) -> None:
    assert build(name).krull_dimension() == dimension


@pytest.mark.parametrize(
    "name, size",
    [
        ("GF(4)", 4),
        ("GF(27)", 27),
        ("ZZ/12", 12),
        ("ZZ/8", 8),
        ("GF(2)[t]/(t^2)", 4),
    ],
)
def test_finite_rings_have_their_cardinality(build, name, size) -> None:
    ring = build(name)
    assert ring.cardinality() == cardinal(size)
    assert ring in FiniteSets()


@pytest.mark.parametrize(
    "name", ["ZZ", "QQ", "ZZ[i]", "QQ[x]", "QQ[x]/(x^3)", "AA", "QQbar", "QQ(zeta5)", "ZZ[x]"]
)
def test_countable_rings_are_countably_infinite(build, name) -> None:
    ring = build(name)
    assert ring.cardinality() == aleph0
    assert ring in CountablyInfiniteSets()


@pytest.mark.parametrize("name", ["RR", "CC", "QQ_3", "ZZ_3", "QQ[[t]]", "ZZ^_2"])
def test_uncountable_rings_have_the_continuum(build, name) -> None:
    ring = build(name)
    assert ring.cardinality() == continuum
    assert ring in UncountableSets()


@pytest.mark.parametrize(
    "name, characteristic",
    [
        ("GF(4)", 2),
        ("GF(27)", 3),
        ("ZZ/12", 12),
        ("GF(2)[t]/(t^2)", 2),
        ("GF(5)(t)", 5),
        ("QQ", 0),
        ("ZZ_3", 0),
        ("QQ_3", 0),
        ("ZZ[i]", 0),
    ],
)
def test_characteristic(build, name, characteristic) -> None:
    assert build(name).characteristic() == characteristic


# ---------------------------------------------------------------------------
# Constructions on every commutative ring.
# ---------------------------------------------------------------------------


def test_fraction_field_of_a_domain_is_a_field(integral_domain) -> None:
    fractions = integral_domain.fraction_field()
    assert fractions in Fields()
    assert fractions.characteristic() == integral_domain.characteristic()


def test_fraction_field_of_a_field_is_itself(field) -> None:
    assert field.fraction_field() is field


def test_polynomial_ring_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    polynomials = ring.polynomial_ring("x")
    x = polynomials.algebra_generator("x")

    assert polynomials in CommutativeRings()
    assert polynomials in Algebras(ring).Associative().Unital().Commutative()
    assert polynomials.base_ring() is ring
    assert (x + polynomials.one()) ** 2 == x**2 + 2 * x + polynomials.one()
    assert (polynomials in IntegralDomains()) == (ring in IntegralDomains())
    assert (polynomials in NoetherianRings()) == (ring in NoetherianRings())
    assert (polynomials in PrincipalIdealDomains()) == (ring in Fields())
    assert polynomials not in LocalRings()
    assert polynomials.cardinality() == cardinal(max(ring.cardinality(), aleph0))


def test_polynomial_ring_in_two_variables_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    polynomials = ring.polynomial_ring(("x", "y"))
    x = polynomials.algebra_generator("x")
    y = polynomials.algebra_generator("y")

    assert polynomials in Algebras(ring).Associative().Unital().Commutative()
    assert x * y == y * x
    assert (polynomials in IntegralDomains()) == (ring in IntegralDomains())
    assert polynomials not in PrincipalIdealDomains()


@pytest.mark.parametrize("name", ["ZZ", "QQ", "GF(5)", "ZZ[i]", "QQ[x]", "ZZ/12", "QQ_3"])
def test_polynomial_ring_raises_krull_dimension_by_one(build, name) -> None:
    ring = build(name)
    assert ring.polynomial_ring("x").krull_dimension() == ring.krull_dimension() + 1
    assert ring.polynomial_ring(("x", "y")).krull_dimension() == ring.krull_dimension() + 2


def test_laurent_polynomials_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    laurent = ring.laurent_polynomial_ring("x")
    x = laurent.algebra_generator("x")

    assert laurent in Algebras(ring).Associative().Unital().Commutative()
    assert x * x**-1 == laurent.one()
    assert (laurent in IntegralDomains()) == (ring in IntegralDomains())


def test_power_series_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    series = ring.power_series_ring("t")
    t = series.power_series_variable()

    assert series in FormalPowerSeriesRings(ring)
    assert series in Algebras(ring).Associative().Unital().Commutative()
    assert (series in IntegralDomains()) == (ring in IntegralDomains())
    assert (series in NoetherianRings()) == (ring in NoetherianRings())
    assert (series in LocalRings()) == (ring in LocalRings())
    assert (series in PrincipalIdealDomains()) == (ring in Fields())
    geometric = (series.one() - t).inverse_of_unit()
    assert geometric.coefficient(0) == ring.one()
    assert geometric.coefficient(7) == ring.one()


def test_dual_numbers_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    dual = ring.dual_numbers()
    epsilon = dual.algebra_generator("epsilon")

    assert dual in Algebras(ring).Associative().Unital().Commutative()
    assert epsilon != dual.zero()
    assert epsilon * epsilon == dual.zero()
    assert dual not in IntegralDomains()
    assert (dual in LocalRings()) == (ring in LocalRings())
    assert (dual in ArtinianRings()) == (ring in ArtinianRings())
    assert dual.krull_dimension() == ring.krull_dimension()


def test_matrix_algebra_over_every_ring(ring) -> None:
    matrices = ring.matrix_space(2)
    e01 = matrices.matrix_unit(0, 1)
    e10 = matrices.matrix_unit(1, 0)

    assert matrices in MatrixAlgebras(ring)
    assert matrices in Algebras(ring)
    assert matrices in Rings()
    assert matrices not in CommutativeRings()
    assert e01 * e10 != e10 * e01
    assert matrices.identity_matrix().determinant() == ring.one()
    assert (e01 + e10).determinant() == -ring.one()
    assert (e01 + e10) * (e01 + e10) == matrices.identity_matrix()


@pytest.mark.parametrize("name, size", [("GF(4)", 256), ("ZZ/12", 12**4), ("GF(5)", 625)])
def test_matrix_algebra_over_a_finite_ring_is_finite(build, name, size) -> None:
    assert build(name).matrix_space(2).cardinality() == cardinal(size)


def test_a_commutative_ring_is_an_algebra_over_itself(commutative_ring) -> None:
    ring = commutative_ring
    assert ring in Algebras(ring)
    assert ring in Algebras(ring).Associative().Unital().Commutative()
    assert ring.as_algebra_over(ring) in Algebras(ring).Associative().Unital().Commutative()


def test_a_commutative_ring_is_an_algebra_over_the_integers(commutative_ring) -> None:
    ring = commutative_ring
    algebra = ring.as_ZZ_algebra()
    assert algebra in Algebras(ZZ).Associative().Unital().Commutative()
    assert algebra.algebra_structure_morphism()(1) == algebra.one()


def test_the_integers_are_initial(ring) -> None:
    r"""$\operatorname{Hom}_{\mathbf{Ring}}(\mathbb Z, R)$ is a point for every ring $R$."""
    homset = ZZ.Mor(ring)
    assert homset.cardinality() == cardinal(1)
    unique = homset.an_element()
    assert unique(1) == ring.one()
    assert unique(7) == 7 * ring.one()


def test_identity_ring_morphism(ring) -> None:
    identity = ring.Mor(ring).identity()
    assert identity(ring.one()) == ring.one()
    assert identity * identity == identity


@pytest.mark.parametrize(
    "source, target, count",
    [
        ("QQ", "ZZ", 0),
        ("GF(5)", "GF(4)", 0),
        ("GF(4)", "GF(5)", 0),
        ("QQ", "QQ", 1),
        ("GF(4)", "GF(4)", 2),
        ("QQ(i)", "QQ(i)", 2),
        ("QQ(cbrt2)", "QQ(cbrt2)", 1),
        ("ZZ/12", "ZZ/8", 0),
        ("ZZ/8", "ZZ/8", 1),
    ],
)
def test_counting_ring_morphisms(build, source, target, count) -> None:
    assert build(source).Mor(build(target)).cardinality() == cardinal(count)


# ---------------------------------------------------------------------------
# Ideals, quotients, localizations, completions, spectra.
# ---------------------------------------------------------------------------


def test_zero_and_unit_ideals_of_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    zero = ring.ideal(ring.zero())
    unit = ring.ideal(ring.one())

    assert zero in CommutativeIdeals(ring)
    assert unit in CommutativeIdeals(ring)
    assert zero.is_prime() == (ring in IntegralDomains())
    assert zero.is_maximal() == (ring in Fields())
    assert not unit.is_prime()


def test_ideal_arithmetic_with_zero_and_unit_ideals(commutative_ring) -> None:
    ring = commutative_ring
    zero = ring.ideal(ring.zero())
    unit = ring.ideal(ring.one())

    assert zero.sum(unit) == unit
    assert zero.intersection(unit) == zero
    assert zero.product(unit) == zero
    assert unit.quotient_ring().cardinality() == cardinal(1)


def test_ideal_arithmetic_in_the_integers() -> None:
    four = ZZ.ideal(4)
    six = ZZ.ideal(6)
    assert four.sum(six) == ZZ.ideal(2)
    assert four.intersection(six) == ZZ.ideal(12)
    assert four.product(six) == ZZ.ideal(24)
    assert ZZ.ideal(12).radical() == ZZ.ideal(6)
    assert ZZ.ideal(12).quotient_ring().cardinality() == cardinal(12)
    assert four.colon(six) == ZZ.ideal(2)
    assert ZZ.ideal(5).is_prime()
    assert ZZ.ideal(5).is_maximal()
    assert not ZZ.ideal(6).is_prime()


def test_polynomial_ideals_over_the_rationals() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axis = plane.ideal(x)
    origin = plane.ideal(x, y)

    assert axis.is_prime()
    assert not axis.is_maximal()
    assert origin.is_prime()
    assert origin.is_maximal()
    assert origin.quotient_ring() in Fields()
    assert axis.intersection(plane.ideal(y)) == plane.ideal(x * y)
    assert plane.ideal(x**2).radical() == axis


@pytest.mark.parametrize(
    "name, generator, residue_size",
    [
        ("ZZ", 5, 5),
        ("ZZ", 2, 2),
        ("ZZ[i]", 3, 9),
        ("QQ[x]", "x", aleph0),
        ("GF(5)[t]", "t", 5),
        ("ZZ_3", 3, 3),
        ("ZZ_(5)", 5, 5),
    ],
)
def test_a_maximal_ideal_has_a_residue_field(build, name, generator, residue_size) -> None:
    ring = build(name)
    element = ring.algebra_generator(generator) if isinstance(generator, str) else ring(ZZ(generator))
    maximal = ring.ideal(element)

    assert maximal.is_prime()
    assert maximal.is_maximal()
    residue = maximal.quotient_ring()
    assert residue in Fields()
    assert residue.cardinality() == cardinal(residue_size)


@pytest.mark.parametrize(
    "name, generator",
    [("ZZ", 6), ("ZZ[i]", 5), ("ZZ[i]", 2), ("ZZ[sqrt-5]", 2), ("QQ[x]", None), ("ZZ/12", 4)],
)
def test_a_composite_generator_gives_a_non_prime_ideal(build, name, generator) -> None:
    ring = build(name)
    if generator is None:
        x = ring.algebra_generator("x")
        element = x**2 - ring.one()
    else:
        element = ring(ZZ(generator))
    assert not ring.ideal(element).is_prime()


def test_gaussian_primes(build) -> None:
    gaussian = build("ZZ[i]")
    fractions = gaussian.fraction_field()
    i = fractions.primitive_element()
    assert gaussian.ideal(gaussian(fractions.one() + i)).is_prime()
    assert gaussian.ideal(gaussian(7)).is_prime()
    assert not gaussian.ideal(gaussian(5)).is_prime()
    assert gaussian.ideal(gaussian(fractions.one() + i)).quotient_ring().cardinality() == cardinal(2)
    assert gaussian.ideal(gaussian(7)).quotient_ring().cardinality() == cardinal(49)


def test_direct_integer_mod_ring_refines_prime_moduli_to_fields() -> None:
    seven = Zmod(7)
    twelve = Zmod(12)

    assert seven in Fields()
    assert seven in IntegralDomains()
    assert twelve not in Fields()
    assert twelve not in IntegralDomains()


def test_quotient_rings_of_the_integers() -> None:
    twelve = ZZ.quotient_ring(ZZ.ideal(12))
    seven = ZZ.quotient_ring(ZZ.ideal(7))

    assert twelve in ArtinianRings()
    assert twelve not in IntegralDomains()
    assert twelve.cardinality() == cardinal(12)
    assert twelve.characteristic() == 12
    assert seven in Fields()
    assert seven.cardinality() == cardinal(7)
    assert twelve.quotient_map()(13) == twelve.one()


def test_quotient_of_a_polynomial_ring_by_an_irreducible_is_a_field() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    gaussian_rationals = polynomials.quotient_ring(polynomials.ideal(x**2 + polynomials.one()))

    assert gaussian_rationals in Fields()
    assert gaussian_rationals.characteristic() == 0
    i = gaussian_rationals.quotient_map()(x)
    assert i * i == -gaussian_rationals.one()
    assert gaussian_rationals.cardinality() == aleph0


def test_quotient_of_the_integer_polynomials_by_x_squared_plus_one_is_a_domain() -> None:
    polynomials = ZZ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    gaussian = polynomials.quotient_ring(polynomials.ideal(x**2 + polynomials.one()))

    assert gaussian in IntegralDomains()
    assert gaussian not in Fields()
    assert gaussian.krull_dimension() == 1
    assert gaussian.fraction_field() in Fields()


def test_localizing_the_integers_at_a_prime_gives_a_discrete_valuation_ring() -> None:
    local = ZZ.localize_at_prime(7)
    assert local in LocalRings()
    assert local in PrincipalIdealDomains()
    assert local not in Fields()
    assert local.residue_field().cardinality() == cardinal(7)
    assert local(3).is_unit()
    assert not local(7).is_unit()
    assert local.maximal_ideal() == local.ideal(local(7))
    assert local.fraction_field() is QQ


def test_inverting_a_set_of_elements_of_the_integers() -> None:
    inverted = ZZ.localization(6)
    collapsed = ZZ.localization(0)

    assert inverted(2).is_unit()
    assert inverted(3).is_unit()
    assert not inverted(5).is_unit()
    assert inverted in IntegralDomains()
    assert inverted not in LocalRings()
    assert inverted.fraction_field() is QQ
    assert inverted.cardinality() == aleph0
    assert collapsed.cardinality() == cardinal(1)


@pytest.mark.parametrize(
    "name, prime_generators, residue_size",
    [
        ("ZZ[i]", (3,), 9),
        ("ZZ[sqrt-5]", (2, "1+s"), 2),
        ("ZZ[x]", (2, "x"), 2),
        ("QQ[x,y]", ("x", "y"), aleph0),
    ],
)
def test_localizing_at_a_maximal_ideal(build, name, prime_generators, residue_size) -> None:
    ring = build(name)

    def element(datum):
        if datum == "1+s":
            return ring(ring.fraction_field().one() + ring.fraction_field().primitive_element())
        if datum in ("x", "y"):
            return ring.algebra_generator(datum)
        return ring(ZZ(datum))

    prime = ring.ideal(*(element(datum) for datum in prime_generators))
    local = ring.localize_at_prime(prime)

    assert prime.is_maximal()
    assert local in LocalRings()
    assert local in NoetherianRings()
    assert local.krull_dimension() == ring.krull_dimension()
    assert local.residue_field() in Fields()
    if residue_size is aleph0:
        assert local.residue_field().cardinality() == aleph0
    else:
        assert local.residue_field().cardinality() == cardinal(residue_size)


def test_completing_the_integers_at_a_prime() -> None:
    completion = ZZ.adic_completion(ZZ.ideal(3))
    assert completion in CompleteLocalRings()
    assert completion in PrincipalIdealDomains()
    assert completion.residue_field().cardinality() == cardinal(3)
    assert completion.characteristic() == 0
    assert completion.completion_map()(5).is_unit()
    assert not completion.completion_map()(3).is_unit()


def test_the_p_adic_integers_and_numbers() -> None:
    integers = Zp(3)
    numbers = Qp(3)
    assert integers in CompleteLocalRings()
    assert integers in PrincipalIdealDomains()
    assert integers not in Fields()
    assert numbers in Fields()
    assert integers.fraction_field() == numbers
    assert integers.residue_field().cardinality() == cardinal(3)
    assert integers.maximal_ideal() == integers.ideal(integers(3))
    assert integers(2).is_unit()
    assert not integers(3).is_unit()
    assert integers(18).valuation(3) == 2
    assert numbers.characteristic() == 0


def test_completing_a_polynomial_ring_at_the_origin() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    completion = polynomials.adic_completion(polynomials.ideal(x))
    assert completion in CompleteLocalRings()
    assert completion.residue_field() in Fields()
    assert completion.residue_field().characteristic() == 0


def test_prime_spectrum_of_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    spectrum = ring.spectrum()
    assert spectrum.ring() is ring
    assert spectrum.closed_set(ring.ideal(ring.zero()))
    assert spectrum.distinguished_open(ring.one())


def test_prime_spectrum_of_a_domain_has_a_generic_point(integral_domain) -> None:
    spectrum = integral_domain.spectrum()
    generic = spectrum.generic_point()
    assert generic in spectrum
    assert generic.ideal() == integral_domain.ideal(integral_domain.zero())
    assert generic.residue_field() in Fields()
    assert generic.residue_field().characteristic() == integral_domain.characteristic()


def test_points_of_the_spectrum_of_the_integers() -> None:
    spectrum = ZZ.spectrum()
    five = spectrum(ZZ.ideal(5))
    generic = spectrum.generic_point()

    assert five in spectrum
    assert spectrum.le(generic, five)
    assert not spectrum.le(five, generic)
    assert generic.specializes_to(five)
    assert five.local_ring() in LocalRings()
    assert five.local_ring().residue_field().cardinality() == cardinal(5)
    assert five.residue_field().cardinality() == cardinal(5)
    assert generic.residue_field() is QQ
    assert five in spectrum.closed_set(ZZ.ideal(10))
    assert five not in spectrum.distinguished_open(5)
    assert generic in spectrum.distinguished_open(5)


def test_a_non_prime_ideal_is_not_a_point_of_the_spectrum() -> None:
    with pytest.raises((ValueError, TypeError, AssertionError)):
        ZZ.spectrum()(ZZ.ideal(6))


# ---------------------------------------------------------------------------
# Number fields and their rings of integers.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, degree, discriminant, real_places, complex_places, class_number, galois",
    [
        ("QQ", 1, 1, 1, 0, 1, True),
        ("QQ(i)", 2, -4, 0, 1, 1, True),
        ("QQ(sqrt5)", 2, 5, 2, 0, 1, True),
        ("QQ(sqrt-5)", 2, -20, 0, 1, 2, True),
        ("QQ(sqrt-23)", 2, -23, 0, 1, 3, True),
        ("QQ(zeta5)", 4, 125, 0, 2, 1, True),
        ("QQ(cbrt2)", 3, -108, 1, 1, 1, False),
    ],
)
def test_number_field_invariants(
    build, name, degree, discriminant, real_places, complex_places, class_number, galois
) -> None:
    field = build(name)
    assert field.degree() == degree
    assert field.discriminant() == discriminant
    assert field.signature() == signature_pair(real_places, complex_places)
    assert field.class_number() == class_number
    assert field.is_galois() is galois


@pytest.mark.parametrize(
    "name, degree, real_places",
    [("QQ", 1, 1), ("QQ(i)", 2, 0), ("QQ(sqrt5)", 2, 2), ("QQ(zeta5)", 4, 0), ("QQ(cbrt2)", 3, 1)],
)
def test_real_and_complex_embeddings_of_a_number_field(build, name, degree, real_places) -> None:
    field = build(name)
    assert field.embeddings(AA).cardinality() == cardinal(real_places)
    assert field.embeddings(RR).cardinality() == cardinal(real_places)
    assert field.embeddings(CC).cardinality() == cardinal(degree)


def test_ring_of_integers_of_every_number_field(number_field) -> None:
    field = number_field
    order = field.ring_of_integers()

    assert order in OwnedOrders()
    assert order.is_maximal()
    assert order in IntegralDomains()
    assert order in NoetherianRings()
    assert order.fraction_field() is field
    assert order.module_rank() == cardinal(field.degree())
    assert order.integral_basis().cardinality() == cardinal(field.degree())
    framing = order.framing_morphism()
    assert framing.codomain() is order
    assert order.framing_source() is framing.domain()
    for label in order.module_generating_set():
        assert order.module_generator(label) == framing(
            order.framing_source().module_generator(label)
        )
    assert order.cardinality() == aleph0
    assert (order in PrincipalIdealDomains()) == (field.class_number() == 1)


@pytest.mark.parametrize(
    "name, prime, count",
    [
        ("QQ(i)", 2, 1),
        ("QQ(i)", 3, 1),
        ("QQ(i)", 5, 2),
        ("QQ(sqrt5)", 2, 1),
        ("QQ(sqrt5)", 5, 1),
        ("QQ(sqrt5)", 11, 2),
        ("QQ(zeta5)", 2, 1),
        ("QQ(zeta5)", 5, 1),
        ("QQ(zeta5)", 11, 4),
        ("QQ(zeta5)", 19, 2),
        ("QQ(cbrt2)", 2, 1),
        ("QQ(cbrt2)", 3, 1),
        ("QQ(cbrt2)", 5, 2),
        ("QQ(cbrt2)", 31, 3),
        ("QQ(sqrt-5)", 2, 1),
        ("QQ(sqrt-5)", 3, 2),
    ],
)
def test_primes_above_a_rational_prime(build, name, prime, count) -> None:
    field = build(name)
    primes = field.primes_above(prime)
    assert primes.cardinality() == cardinal(count)
    for prime_ideal in primes:
        assert prime_ideal.is_prime()
        assert prime_ideal.is_maximal()


@pytest.mark.parametrize(
    "name, ramified",
    [
        ("QQ(i)", (2,)),
        ("QQ(sqrt5)", (5,)),
        ("QQ(zeta5)", (5,)),
        ("QQ(cbrt2)", (2, 3)),
        ("QQ(sqrt-5)", (2, 5)),
        ("QQ(sqrt-23)", (23,)),
    ],
)
def test_ramified_primes(build, name, ramified) -> None:
    primes = build(name).ramified_primes()
    assert primes.cardinality() == cardinal(len(ramified))
    for prime in ramified:
        assert ZZ(prime) in primes


@pytest.mark.parametrize("name, order", [("QQ(i)", 2), ("QQ(sqrt5)", 2), ("QQ(zeta5)", 4)])
def test_galois_group_of_a_galois_number_field(build, name, order) -> None:
    group = build(name).galois_group()
    assert group.order() == order
    assert group.is_abelian()


def test_normal_closure_of_a_non_galois_cubic(build) -> None:
    field = build("QQ(cbrt2)")
    closure = field.normal_closure()
    assert closure.degree() == 6
    assert closure.is_galois()
    assert field.normal_closure_galois_group().order() == 6
    assert not field.normal_closure_galois_group().is_abelian()


def test_the_rationals_are_their_own_number_field() -> None:
    assert QQ.ring_of_integers() is ZZ
    assert QQ.degree() == 1
    assert QQ.primes_above(7).cardinality() == cardinal(1)


# ---------------------------------------------------------------------------
# Finite fields, subrings.
# ---------------------------------------------------------------------------


def test_finite_field_is_a_finite_field(finite_field) -> None:
    field = finite_field
    size = field.cardinality()
    assert field in Fields()
    assert field in FiniteSets()
    assert field in ArtinianRings()
    generator = field.multiplicative_generator()
    assert generator.multiplicative_order() == size.finite_value() - 1
    element = field.an_element()
    assert element ** int(size.finite_value()) == element


def test_finite_field_extensions_and_their_morphisms() -> None:
    assert GF(4).Mor(GF(16)).cardinality() == cardinal(2)
    assert GF(4).Mor(GF(8)).cardinality() == cardinal(0)
    assert GF(2).Mor(GF(8)).cardinality() == cardinal(1)
    assert GF(9).Mor(GF(81)).cardinality() == cardinal(2)


def test_a_subring_cut_out_by_a_predicate() -> None:
    integers_in_rationals = QQ.predicate_subring(
        lambda element: element.denominator() == 1, "the denominator is one"
    )
    assert integers_in_rationals in OwnedRings()
    assert QQ(3) in integers_in_rationals
    assert QQ(1) / QQ(2) not in integers_in_rationals
    assert integers_in_rationals.ambient_ring() is QQ
    inclusion = integers_in_rationals.inclusion()
    assert inclusion.codomain() is QQ
    assert inclusion(integers_in_rationals.one()) == QQ.one()
