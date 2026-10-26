r"""Research sessions over Hypothesis-generated inputs.

The same sessions a mathematician runs by hand, with the starting datum
drawn by Hypothesis: a squarefree radicand for a quadratic field, a
nondegenerate Gram matrix for a lattice, an integer for a finite group, a
prime for a local session.  Most of the proof is that each session runs to
the end for every drawn input.
"""

from math import factorial

from construction_strategies import nondegenerate_gram_2x2, primes, radicands, small_integers
from hypothesis import given, settings
from natural_parameters import determinant_2x2, euler_phi, is_prime, prime_factorization, quadratic_field_discriminant, signature_2x2
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403

session = settings(max_examples=15r, deadline=None)


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


@session
@given(d=radicands)
def test_a_generated_quadratic_field_session(d) -> None:
    field = QuadraticField(d, "s")
    rendered(field)
    integers = field.ring_of_integers()
    rendered(integers)
    assert integers.module_rank() == cardinal(2)
    assert field.discriminant() == quadratic_field_discriminant(d)
    for p in (2, 3, 5, 7, 11):
        primes_above = field.primes_above(p)
        rendered(primes_above)
        for prime_ideal in primes_above:
            rendered(prime_ideal)
            assert prime_ideal.is_prime()
            assert prime_ideal.quotient_ring().cardinality() in (cardinal(p), cardinal(p * p))
    first = next(iter(field.primes_above(2)))
    local = integers.localize_at_prime(first)
    rendered(local)
    assert local in LocalRings()
    completion = integers.adic_completion(first)
    rendered(completion)
    assert completion in CompleteLocalRings()
    assert completion.residue_field().characteristic() == 2
    galois = field.galois_group()
    rendered(galois)
    assert galois.order() == 2
    unit_rank = 1 if d > 0 else 0
    assert field.unit_group().module_rank() == cardinal(unit_rank)
    rendered(field.class_group())
    assert field.class_group().order() == field.class_number()


@session
@given(gram=nondegenerate_gram_2x2)
def test_a_generated_lattice_session(gram) -> None:
    lattice = Lattices(ZZ)(gram)
    rendered(lattice)
    det = determinant_2x2(gram)
    assert lattice.determinant() == det
    assert lattice.signature_pair() == signature_pair(*signature_2x2(gram))
    dual = lattice.dual_lattice()
    rendered(dual)
    discriminant = lattice.discriminant_group()
    rendered(discriminant)
    assert discriminant.cardinality() == cardinal(abs(det))
    rendered(lattice.discriminant_bilinear_form())
    if lattice.is_even():
        rendered(lattice.discriminant_quadratic_form())
    line = lattice.subobject_on([lattice.basis_vector(0)])
    rendered(line)
    rendered(line.orthogonal_complement())
    assert line.module_rank() + line.orthogonal_complement().module_rank() == cardinal(2)
    bigger = lattice + Lattices(ZZ)("U")
    rendered(bigger)
    assert bigger.module_rank() == cardinal(4)
    assert bigger.discriminant_group().cardinality() == cardinal(abs(det))
    rendered(lattice.genus())
    assert lattice.genus().representative().genus() == lattice.genus()
    rendered(lattice.O())
    if lattice.is_definite():
        rendered(lattice.roots())
        rendered(lattice.shortest_vectors())
        assert lattice.O().is_finite()
        assert lattice.minimum() != 0
    else:
        rendered(lattice.isotropic_line_orbit_representatives())
    rational = lattice.base_change(ZZ.Mor(QQ)(lambda k: QQ(k)))
    rendered(rational)
    assert rational.determinant() == det


@session
@given(n=small_integers)
def test_a_generated_finite_group_session(n) -> None:
    cyclic = Groups.C(n)
    dihedral = Groups.D(n)
    rendered(cyclic)
    rendered(dihedral)
    assert cyclic.order() == n
    assert dihedral.order() == 2 * n
    assert dihedral.is_abelian() == (n <= 2)
    rendered(cyclic.Aut())
    assert cyclic.Aut().order() == euler_phi(n)
    rendered(dihedral.center())
    assert dihedral.center().order() == (4 if n == 2 else 2 if n % 2 == 0 else 1)
    rendered(Groups().abelianization()(dihedral))
    assert Groups().abelianization()(dihedral).order() == (4 if n % 2 == 0 else 2)
    rotation = next(g for g in dihedral.group_generators() if g.order() == n)
    rotations = dihedral.subgroup([rotation])
    rendered(rotations)
    assert rotations.order() == n
    assert rotations.is_normal()
    assert dihedral.left_cosets(rotations).cardinality() == cardinal(2)
    assert rotations.inclusion().cokernel().order() == 2
    rendered(dihedral.conjugacy_classes_representatives())
    assert dihedral.conjugacy_classes_representatives().cardinality() == cardinal((n + 6) // 2 if n % 2 == 0 else (n + 3) // 2)
    points = tuple(range(1, n + 1))
    polygon = FiniteGSets(dihedral)(points, lambda g, point: g(point))
    rendered(polygon)
    assert FiniteGSets(dihedral).orbits_functor()(polygon).cardinality() == cardinal(1)
    assert polygon.fixed_points().cardinality() == cardinal(0)
    assert Groups.S(n).order() == factorial(n)
    assert dihedral.Mor(Groups.S(n)).cardinality() >= cardinal(1)


@session
@given(p=primes)
def test_a_generated_local_session(p) -> None:
    local = ZZ.localize_at_prime(p)
    rendered(local)
    assert local in LocalRings()
    assert local in PrincipalIdealDomains()
    assert local.residue_field().cardinality() == cardinal(p)
    completion = local.adic_completion(local.maximal_ideal())
    rendered(completion)
    assert completion in CompleteLocalRings()
    assert completion == Zp(p)
    assert completion.residue_field().cardinality() == cardinal(p)
    field = GF(p)
    rendered(field)
    assert field.multiplicative_generator().multiplicative_order() == p - 1
    extension = GF(p**2)
    rendered(extension)
    assert extension.cardinality() == cardinal(p * p)
    assert extension.Mor(extension).cardinality() == cardinal(2)
    assert field.Mor(extension).cardinality() == cardinal(1)
    line = AffineSpaces(field)(1)
    rendered(line)
    assert line.point_count() == p
    assert line.point_count(2) == p * p
    assert ProjectiveSpaces(field)(1).point_count() == p + 1
    lattice = Lattices(field)([[2, 1], [1, 2]])
    rendered(lattice)
    assert lattice.is_nondegenerate() == (p != 3)
    torsion = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((p, p * p))
    rendered(torsion)
    assert torsion.cardinality() == cardinal(p**3)
    assert torsion.localize_at_prime(ZZ.spectrum()(ZZ.ideal(p))).cardinality() == cardinal(p**3)
    other = 2 if p != 2 else 3
    assert torsion.localize_at_prime(ZZ.spectrum()(ZZ.ideal(other))).cardinality() == cardinal(1)
    assert is_prime(p) and prime_factorization(p) == {p: 1}
