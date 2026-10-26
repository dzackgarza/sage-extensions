r"""Property-based expectations: claims uniform in a natural parameter or a catalogue member.

Hypothesis draws the parameter; the test states what elementary mathematics
determines from it and asks the session for the same thing.  Every claim
here holds for every value the strategy can produce, so a failure names a
concrete counterexample the session mishandles.
"""

from math import factorial, gcd, lcm, prod

from conftest import COMMUTATIVE_RINGS, FIELDS, PRINCIPAL_IDEAL_DOMAINS, specimen
from construction_strategies import (
    cartan_types,
    cyclic_module_orders,
    cyclic_orders,
    even_gram_2x2,
    family,
    nondegenerate_gram_2x2,
    nonzero_rationals,
    positive_integers,
    positive_ranks,
    primes,
    radicands,
    ranks,
    small_integers,
    symmetric_groups,
)
from hypothesis import given, settings
from natural_parameters import (
    binomial,
    determinant_2x2,
    euler_phi,
    is_prime,
    number_of_divisors,
    prime_factorization,
    quadratic_field_discriminant,
    signature_2x2,
)

from sage_extensions.all import *  # noqa: F401,F403

survey = settings(max_examples=25r, deadline=None)


# ---------------------------------------------------------------------------
# Integers.
# ---------------------------------------------------------------------------


@survey
@given(n=small_integers)
def test_the_integers_modulo_n(n) -> None:
    residues = Zmod(n)
    assert residues.cardinality() == cardinal(n)
    assert residues.characteristic() == n
    assert (residues in Fields()) == is_prime(n)
    assert (residues in IntegralDomains()) == is_prime(n)
    assert (residues in LocalRings()) == (len(prime_factorization(n)) == 1)
    assert residues.condition_set(lambda a: a.is_unit()).cardinality() == cardinal(euler_phi(n))
    assert residues.spectrum().cardinality() == cardinal(len(prime_factorization(n)))
    assert ZZ.ideal(n).is_prime() == is_prime(n)
    assert ZZ(n).prime_divisors().cardinality() == cardinal(len(prime_factorization(n)))
    assert ZZ(n).divisors().cardinality() == cardinal(number_of_divisors(n))
    assert ZZ(n).euler_phi() == euler_phi(n)
    for p, exponent in prime_factorization(n).items():
        assert ZZ(n).valuation(p) == exponent


@survey
@given(n=cyclic_orders, m=cyclic_orders)
def test_cyclic_groups_and_their_homomorphisms(n, m) -> None:
    cyclic = Groups.C(n)
    groups = Groups()
    assert cyclic.order() == n
    assert cyclic in AbelianGroups()
    assert cyclic.Aut().order() == euler_phi(n)
    assert cyclic.Mor(Groups.C(m)).cardinality() == cardinal(gcd(n, m))
    product = groups.product((cyclic, Groups.C(m)))
    assert product.order() == n * m
    assert product.is_isomorphic_to(Groups.C(n * m)) == (gcd(n, m) == 1)
    assert cyclic.subgroups().cardinality() == cardinal(number_of_divisors(n))
    assert cyclic.group_generators()[0].order() == n


@survey
@given(n=symmetric_groups)
def test_symmetric_groups(n) -> None:
    symmetric = Groups.S(n)
    assert symmetric.order() == factorial(n)
    assert symmetric.is_abelian() == (n <= 2)
    assert symmetric.center().order() == (2 if n == 2 else 1)
    assert Groups().abelianization()(symmetric).order() == (1 if n == 1 else 2)
    assert symmetric.commutator_subgroup().order() == max(1, factorial(n) // 2)
    assert symmetric.Aut().order() == (factorial(n) if n not in (2, 6) else (1 if n == 2 else 1440))
    assert symmetric.conjugacy_classes_representatives().cardinality() == cardinal(partitions(n))


def partitions(n: int) -> int:
    table = [1] + [0] * n
    for part in range(1, n + 1):
        for total in range(part, n + 1):
            table[total] += table[total - part]
    return table[n]


@survey
@given(orders=cyclic_module_orders())
def test_finite_abelian_groups_as_torsion_modules(orders) -> None:
    module = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics(tuple(orders))
    exponent = lcm(*orders)
    assert module.cardinality() == cardinal(prod(orders))
    assert module.annihilator() == ZZ.ideal(exponent)
    assert module.is_torsion()
    assert module.invariant_factors().cardinality() <= cardinal(len(orders))
    assert Groups.Abelian(orders).order() == prod(orders)
    assert Groups.Abelian(orders).exponent() == exponent
    doubled = module.base_change(ZZ.Mor(GF(2))(lambda k: GF(2)(k)))
    assert doubled.cardinality() == cardinal(2 ** sum(1 for order in orders if order % 2 == 0))


# ---------------------------------------------------------------------------
# Rationals and quadratic fields.
# ---------------------------------------------------------------------------


@survey
@given(q=nonzero_rationals, r=nonzero_rationals)
def test_rational_arithmetic_and_rank_one_forms(q, r) -> None:
    a = QQ(q)
    b = QQ(r)
    assert a / b * b == a
    assert a.denominator() == q.denominator()
    assert a.numerator() == q.numerator()
    lattice = Lattices(QQ)([[a, 0], [0, b]])
    assert lattice.determinant() == a * b
    assert lattice.is_nondegenerate()
    assert lattice.dual_lattice().determinant() == QQ(1) / (a * b)
    assert lattice.signature_pair() == signature_pair(int(a > QQ(0)) + int(b > QQ(0)), int(a < QQ(0)) + int(b < QQ(0)))
    assert lattice.is_definite() == ((a > QQ(0)) == (b > QQ(0)))


@survey
@given(d=radicands)
def test_quadratic_fields(d) -> None:
    field = QuadraticField(d, "s")
    root = field.primitive_element()
    assert field.degree() == 2
    assert root * root == d
    assert field.discriminant() == quadratic_field_discriminant(d)
    assert field.signature() == signature_pair(2 if d > 0 else 0, 0 if d > 0 else 1)
    assert field.is_galois()
    assert field.galois_group().order() == 2
    assert field.ring_of_integers().module_rank() == cardinal(2)
    assert field.ring_of_integers().is_maximal()
    assert field.embeddings(CC).cardinality() == cardinal(2)
    assert field.class_number() >= 1
    assert (field.ring_of_integers() in PrincipalIdealDomains()) == (field.class_number() == 1)
    for p in (2, 3, 5, 7):
        primes_above = field.primes_above(p)
        assert cardinal(1) <= primes_above.cardinality() <= cardinal(2)
        assert (p in field.ramified_primes()) == (quadratic_field_discriminant(d) % p == 0)
        assert sum(P.ramification_index() * P.residue_degree() for P in primes_above) == 2
    assert field.ring_of_integers().as_algebra_over(ZZ).kahler_differentials().cardinality() == cardinal(abs(quadratic_field_discriminant(d)))


@survey
@given(p=primes)
def test_prime_fields_and_p_adics(p) -> None:
    field = GF(p)
    assert field.cardinality() == cardinal(p)
    assert field in PrimeFields()
    assert field.multiplicative_generator().multiplicative_order() == p - 1
    assert Zp(p) in CompleteLocalRings()
    assert Zp(p).residue_field().cardinality() == cardinal(p)
    assert Qp(p) in Fields()
    assert ZZ.localize_at_prime(p).residue_field().cardinality() == cardinal(p)
    assert ZZ.ideal(p).is_maximal()
    assert (ZZ).affine_spectrum().underlying_space()(ZZ.ideal(p)).residue_field().cardinality() == cardinal(p)
    assert Groups.C(p).Aut().order() == p - 1
    assert Groups.GL(2, field).order() == (p**2 - 1) * (p**2 - p)
    assert field.free_module(2).Aut().order() == (p**2 - 1) * (p**2 - p)
    assert AffineSpaces(field)(2).point_count() == p**2
    assert ProjectiveSpaces(field)(2).point_count() == p**2 + p + 1


# ---------------------------------------------------------------------------
# Lattices from Gram matrices.
# ---------------------------------------------------------------------------


@survey
@given(gram=nondegenerate_gram_2x2)
def test_rank_two_lattices_from_gram_matrices(gram) -> None:
    det = determinant_2x2(gram)
    lattice = Lattices(ZZ)(gram)
    assert lattice.module_rank() == cardinal(2)
    assert lattice.determinant() == det
    assert lattice.is_nondegenerate()
    assert lattice.signature_pair() == signature_pair(*signature_2x2(gram))
    assert lattice.is_even() == (gram[0][0] % 2 == 0 and gram[1][1] % 2 == 0)
    assert lattice.discriminant_group().cardinality() == cardinal(abs(det))
    assert lattice.dual_lattice().determinant() * det == 1
    assert lattice.twist(2).determinant() == 4 * det
    assert (lattice + lattice).determinant() == det * det
    assert lattice.is_unimodular() == (abs(det) == 1)
    assert lattice.is_definite() == (det > 0)
    assert lattice.b(lattice.module_generator(0), lattice.module_generator(1)) == gram[0][1]
    assert lattice.base_change(ZZ.Mor(GF(2))(lambda k: GF(2)(k))).is_nondegenerate() == (det % 2 != 0)
    assert lattice.O().order() >= 2
    assert lattice.is_isometric(lattice.LLL())


@survey
@given(gram=even_gram_2x2)
def test_even_rank_two_lattices_have_discriminant_quadratic_forms(gram) -> None:
    lattice = Lattices(ZZ)(gram)
    form = lattice.discriminant_quadratic_form()
    assert lattice in EvenLattices(ZZ)
    assert form.cardinality() == cardinal(abs(determinant_2x2(gram)))
    assert form.O().order() >= 1
    assert lattice.discriminant_bilinear_form().cardinality() == form.cardinality()
    assert lattice.genus().representative().genus() == lattice.genus()


@survey
@given(cartan_type=cartan_types)
def test_root_lattices_of_every_simply_laced_type(cartan_type) -> None:
    name = cartan_type[0] + str(cartan_type[1])
    lattice = Lattices(ZZ)(name)
    weyl = Groups.Coxeter(cartan_type)
    assert lattice in RootLattices()
    assert lattice.module_rank() == cardinal(cartan_type[1])
    assert lattice.is_even()
    assert lattice.is_definite()
    assert lattice.simple_roots().cardinality() == cardinal(cartan_type[1])
    assert lattice.roots().cardinality() == cardinal(cartan_type[1] * lattice.coxeter_number())
    assert lattice.O().order() % weyl.order() == 0
    assert lattice.highest_root().height() == lattice.coxeter_number() - 1
    assert CoxeterDiagrams().from_cartan_type(cartan_type).is_elliptic()


# ---------------------------------------------------------------------------
# Modules over catalogue members.
# ---------------------------------------------------------------------------


@survey
@given(name=family(COMMUTATIVE_RINGS), r=ranks, s=ranks)
def test_ranks_of_free_module_constructions(name, r, s) -> None:
    ring = specimen(name)
    left = ring.free_module(r)
    right = ring.free_module(s)
    modules = Modules(ring)
    assert left.module_rank() == cardinal(r)
    assert left.tensor_product(right).module_rank() == cardinal(r * s)
    assert left.Mor(right).module_rank() == cardinal(r * s)
    assert modules.biproduct((left, right)).module_rank() == cardinal(r + s)
    assert left.dual_module().module_rank() == cardinal(r)
    assert left.exterior_forms(2).module_rank() == cardinal(binomial(r, 2))
    assert left.divided_square().module_rank() == cardinal(binomial(r + 1, 2))
    assert modules.tensor_product((left, left)).module_rank() == cardinal(r * r)
    assert left in FinitelyGeneratedFreeModules(ring)
    assert (left.cardinality() == cardinal(1)) == (r == 0)


@survey
@given(name=family(PRINCIPAL_IDEAL_DOMAINS), orders=cyclic_module_orders())
def test_torsion_modules_over_principal_ideal_domains(name, orders) -> None:
    ring = specimen(name)
    module = FinitelyPresentedTorsionModules(ring).direct_sum_of_cyclics(tuple(ring(k) for k in orders))
    assert module in TorsionModules(ring)
    assert module.cardinality() == cardinal(prod(ring.quotient_ring(ring.ideal(ring(k))).cardinality() for k in orders))
    assert module.annihilator() == ring.ideal(ring(lcm(*orders)))
    assert (module.cardinality() == cardinal(1)) == all(ring(k).is_unit() for k in orders)


@survey
@given(name=family(FIELDS), r=positive_ranks)
def test_vector_spaces_over_catalogue_fields(name, r) -> None:
    field = specimen(name)
    space = field.free_module(r)
    assert space in VectorSpaces(field)
    assert space.module_rank() == cardinal(r)
    assert space.Mor(space).module_rank() == cardinal(r * r)
    assert space.Aut().one() == space.Aut()(space.Mor(space).identity())
    if field.cardinality().is_finite():
        q = field.cardinality()
        assert space.cardinality() == cardinal(q**r)
        assert space.Aut().order() == prod(q**r - q**i for i in range(r))
    line = field.free_module(1)
    morphism = space.Mor(line)(
        {label: line.module_generator(0) for label in range(r)}
    )
    kernel = morphism.kernel()
    assert kernel.module_rank() == cardinal(r - 1)


# ---------------------------------------------------------------------------
# Sets.
# ---------------------------------------------------------------------------


@survey
@given(n=positive_integers, m=positive_integers)
def test_finite_set_constructions(n, m) -> None:
    left = Sets.Δ[n - 1]
    right = Sets.Δ[m - 1]
    sets = Sets()
    assert left.cardinality() == cardinal(n)
    assert sets.product((left, right)).cardinality() == cardinal(n * m)
    assert sets.coproduct((left, right)).cardinality() == cardinal(n + m)
    assert left.exponential(right).cardinality() == cardinal(n**m)
    assert Sets().Mor(right, left).cardinality() == cardinal(n**m)
    assert left.power_set().cardinality() == cardinal(2**n)
    assert left.Aut().order() == factorial(n)
    assert Sets().Mono(right, left).cardinality() == cardinal(factorial(n) // factorial(n - m) if m <= n else 0)
    for k in range(0, min(n, 4) + 1):
        assert left.subsets_of_size(k).cardinality() == cardinal(binomial(n, k))
    assert cardinal(n) + cardinal(m) == cardinal(n + m)
    assert cardinal(n) * cardinal(m) == cardinal(n * m)
    assert cardinal(n) ** cardinal(m) == cardinal(n**m)


@survey
@given(name=family(COMMUTATIVE_RINGS), n=small_integers)
def test_polynomials_and_ideals_over_catalogue_rings(name, n) -> None:
    ring = specimen(name)
    polynomials = ring.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    assert polynomials in Algebras(ring).Associative().Unital().Commutative()
    assert (x**n).degree() == n
    assert ((x + polynomials.one()) ** n).degree() == n
    assert ((x + polynomials.one()) ** n)(ring.one()) == 2**n * ring.one()
    ideal = ring.ideal(ring(n))
    assert ideal in CommutativeIdeals(ring)
    assert ideal.quotient_ring().cardinality() == ring.quotient_ring(ideal).cardinality()
    assert (ideal.quotient_ring().cardinality() == cardinal(1)) == ring(n).is_unit()
    assert ideal.sum(ring.ideal(ring.one())) == ring.ideal(ring.one())
    assert ideal.intersection(ideal) == ideal
    assert ideal.product(ring.ideal(ring.one())) == ideal
