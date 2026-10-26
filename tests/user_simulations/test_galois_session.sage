r"""A session in Galois theory: splitting of primes, decomposition and inertia, Frobenius, characters.

One long session per Galois number field, typed as into a notebook.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


SESSIONS = {
    # name: (constructor, degree, discriminant, ramified primes, a split prime, an inert prime)
    "QQ(i)": (lambda: QuadraticField(-1, "i"), 2, -4, (2,), 5, 3),
    "QQ(sqrt5)": (lambda: QuadraticField(5, "s"), 2, 5, (5,), 11, 2),
    "QQ(sqrt-3)": (lambda: QuadraticField(-3, "w"), 2, -3, (3,), 7, 2),
    "QQ(zeta5)": (lambda: CyclotomicField(5, "z"), 4, 125, (5,), 11, 2),
    "QQ(zeta8)": (lambda: CyclotomicField(8, "z"), 4, 256, (2,), 17, None),
}


@pytest.mark.parametrize("name", sorted(SESSIONS))
def test_a_galois_theory_session(name) -> None:
    build, degree, discriminant, ramified, split_prime, inert_prime = SESSIONS[name]

    field = build()
    rendered(field)
    assert field.is_galois()
    assert field.degree() == degree
    assert field.discriminant() == discriminant
    galois = field.galois_group()
    rendered(galois)
    assert galois in FiniteGroups()
    assert galois in AbelianGroups()
    assert galois.order() == degree
    for automorphism in galois:
        rendered(automorphism)
        assert automorphism(field.primitive_element()).minpoly() == field.primitive_element().minpoly()

    # Ramification and splitting: efg = n at every prime.
    for prime in (2, 3, 5, 7, 11, 13, 17):
        primes = field.primes_above(prime)
        rendered(primes)
        prime_above = next(iter(primes))
        decomposition = galois.decomposition_group(prime_above)
        inertia = galois.inertia_group(prime_above)
        rendered(decomposition)
        rendered(inertia)
        ramification = inertia.order()
        residue_degree = decomposition.order() // ramification
        assert primes.cardinality() * ramification * residue_degree == degree
        assert (ramification > 1) == (prime in ramified)
        assert prime_above.quotient_ring().cardinality() == cardinal(prime**residue_degree)
        assert prime_above.quotient_ring() in Fields()
        if prime not in ramified:
            frobenius = galois.frobenius_class(prime, prime_above)
            rendered(frobenius)
            assert frobenius.representative().order() == residue_degree
            assert frobenius.representative() in decomposition
    assert field.primes_above(split_prime).cardinality() == cardinal(degree)
    if inert_prime is not None:
        assert field.primes_above(inert_prime).cardinality() == cardinal(1)
        assert galois.inertia_group(next(iter(field.primes_above(inert_prime)))).order() == 1

    # The field inside the absolute Galois group of the rationals.
    absolute = AbsoluteGaloisGroup(QQ)
    rendered(absolute)
    assert absolute in ProfiniteGroups()
    open_subgroup = absolute.open_subgroup(field)
    rendered(open_subgroup)
    assert open_subgroup.index() == degree
    assert open_subgroup.fixed_field() is field
    assert absolute.one() in open_subgroup
    frobenius_split = absolute.frobenius(split_prime)
    rendered(frobenius_split)
    assert frobenius_split.restrict(field) == galois.one()
    if inert_prime is not None:
        assert absolute.frobenius(inert_prime).restrict(field) != galois.one()

    # Characters read off the splitting.
    if name == "QQ(zeta5)":
        chi = CyclotomicCharacter(absolute, 5)
        assert chi(absolute.frobenius(11)) == 1
        assert chi(absolute.frobenius(2)) == 2
        assert chi(absolute.frobenius(7)) == 2
        assert chi(absolute.frobenius(19)) == 4
    if degree == 2:
        chi = QuadraticCharacter(absolute, discriminant)
        rendered(chi)
        assert chi(absolute.frobenius(split_prime)) == 1
        assert chi(absolute.frobenius(inert_prime)) == -1


def test_the_absolute_galois_group_of_a_finite_field_session() -> None:
    field = GF(7)
    galois = AbsoluteGaloisGroup(field)
    rendered(galois)
    frobenius = galois.frobenius()
    rendered(frobenius)
    assert galois.is_abelian()
    assert not galois.is_finite()
    assert galois.topological_group_generators().cardinality() == cardinal(1)
    assert frobenius in galois
    for degree in (2, 3, 4):
        extension = galois.finite_extension(degree)
        rendered(extension)
        assert extension.cardinality() == cardinal(7**degree)
        assert extension in Fields()
        assert extension.characteristic() == 7
        assert (frobenius**degree)(extension.an_element()) == extension.an_element()
    assert frobenius(field.an_element()) == field.an_element()
