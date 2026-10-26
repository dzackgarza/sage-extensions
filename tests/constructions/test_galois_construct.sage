r"""Galois theory a mathematician expects: finite and absolute Galois groups, decomposition and inertia, characters.

Decomposition and inertia groups at rational primes in Galois number fields,
Frobenius classes, open subgroups of the absolute Galois group of the
rationals and their fixed fields, cyclotomic and quadratic characters
evaluated at Frobenius, and embeddings between number fields.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

SPLITTING = {
    # (field, prime): (number of primes above, e, f)
    ("QQ(i)", 2): (1, 2, 1),
    ("QQ(i)", 3): (1, 1, 2),
    ("QQ(i)", 5): (2, 1, 1),
    ("QQ(sqrt5)", 5): (1, 2, 1),
    ("QQ(sqrt5)", 2): (1, 1, 2),
    ("QQ(sqrt5)", 11): (2, 1, 1),
    ("QQ(zeta5)", 5): (1, 4, 1),
    ("QQ(zeta5)", 2): (1, 1, 4),
    ("QQ(zeta5)", 11): (4, 1, 1),
    ("QQ(zeta5)", 19): (2, 1, 2),
}


@pytest.mark.parametrize("name, prime", sorted(SPLITTING))
def test_decomposition_and_inertia_groups(build, name, prime) -> None:
    field = build(name)
    count, ramification, residue_degree = SPLITTING[(name, prime)]
    galois = field.galois_group()
    primes = field.primes_above(prime)
    prime_above = next(iter(primes))
    decomposition = galois.decomposition_group(prime_above)
    inertia = galois.inertia_group(prime_above)

    assert primes.cardinality() == cardinal(count)
    assert count * ramification * residue_degree == field.degree()
    assert decomposition.order() == ramification * residue_degree
    assert inertia.order() == ramification
    assert galois.left_cosets(decomposition).cardinality() == cardinal(count)
    if ramification == 1:
        frobenius = galois.frobenius_class(prime, prime_above)
        assert frobenius.representative().order() == residue_degree
        assert frobenius.representative() in decomposition


def test_the_absolute_galois_group_of_the_rationals_and_its_open_subgroups() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    gaussian = QuadraticField(-1, "i")
    open_subgroup = galois.open_subgroup(gaussian)

    assert galois in AbsoluteGaloisGroups()
    assert galois in ProfiniteGroups()
    assert not galois.is_abelian()
    assert not galois.is_finite()
    assert open_subgroup in OpenAbsoluteGaloisSubgroups(galois)
    assert open_subgroup.index() == 2
    assert open_subgroup.supergroup() is galois
    assert open_subgroup.fixed_field() is gaussian
    assert open_subgroup.inclusion().is_injective()
    assert galois.one() in open_subgroup
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    cubic = (x**3 - polynomials(2)).number_field("c")
    assert galois.open_subgroup(cubic).index() == 3


def test_frobenius_elements_and_galois_characters() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    frobenius_seven = galois.frobenius(7)
    frobenius_three = galois.frobenius(3)
    cyclotomic = CyclotomicCharacter(galois, 5)
    quadratic = QuadraticCharacter(galois, -4)

    assert frobenius_seven in galois
    assert frobenius_seven.conjugacy_class().representative() in galois
    assert cyclotomic(frobenius_seven) == 2
    assert cyclotomic(galois.frobenius(11)) == 1
    assert quadratic(galois.frobenius(5)) == 1
    assert quadratic(frobenius_three) == -1
    assert quadratic(galois.frobenius(13)) == 1
    assert cyclotomic(galois.one()) == 1
    assert cyclotomic(frobenius_seven * frobenius_three) == cyclotomic(frobenius_seven) * cyclotomic(frobenius_three)


def test_the_absolute_galois_group_of_a_finite_field() -> None:
    galois = AbsoluteGaloisGroup(GF(5))
    frobenius = galois.frobenius()
    assert galois in AbsoluteGaloisGroupsOfFiniteFields()
    assert galois.is_abelian()
    assert not galois.is_finite()
    assert galois.topological_group_generators().cardinality() == cardinal(1)
    assert frobenius in galois
    assert frobenius != galois.one()
    assert frobenius * frobenius.inverse() == galois.one()
    assert galois.finite_extension(3).cardinality() == cardinal(125)
    assert galois.characteristic() == 5


def test_embeddings_between_number_fields() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    quadratic = QuadraticField(2, "s")
    quartic = (x**4 - polynomials(2)).number_field("t")
    embeddings = quadratic.exact_embeddings(quartic)
    first = quadratic.first_exact_embedding(quartic)

    assert embeddings.cardinality() == cardinal(2)
    assert first.domain() is quadratic
    assert first.codomain() is quartic
    assert first(quadratic.primitive_element()) ** 2 == quartic(2)
    assert first.is_injective()
    assert quartic.exact_embeddings(quadratic).cardinality() == cardinal(0)
    eighth_roots = (x**4 + polynomials.one()).number_field("z")
    assert QuadraticField(-1, "i").exact_embeddings(eighth_roots).cardinality() == cardinal(2)
    assert QuadraticField(3, "s").exact_embeddings(eighth_roots).cardinality() == cardinal(0)
