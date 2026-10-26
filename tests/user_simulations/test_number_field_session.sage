r"""A number theorist's session: a number field, its integers, its primes, its completions.

One long session per defining polynomial, written the way it would be typed
into a notebook: construct, look at the object, ask the next question of the
answer.  Correctness mostly follows from the session running to the end;
the assertions are the values a textbook table gives.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    r"""What the notebook shows: neither repr nor LaTeX may be Python's default."""
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


SESSIONS = {
    # name: (coefficients low to high, degree, discriminant, (r1, r2), class number, galois, ramified)
    "QQ(i)": ((1, 0, 1), 2, -4, (0, 1), 1, True, (2,)),
    "QQ(sqrt2)": ((-2, 0, 1), 2, 8, (2, 0), 1, True, (2,)),
    "QQ(sqrt-5)": ((5, 0, 1), 2, -20, (0, 1), 2, True, (2, 5)),
    "QQ(cbrt2)": ((-2, 0, 0, 1), 3, -108, (1, 1), 1, False, (2, 3)),
    "QQ(zeta8)": ((1, 0, 0, 0, 1), 4, 256, (0, 2), 1, True, (2,)),
}


@pytest.mark.parametrize("name", sorted(SESSIONS))
def test_a_number_field_session(name) -> None:
    coefficients, degree, discriminant, (real_places, complex_places), class_number, galois, ramified = SESSIONS[name]

    # The field, from its defining polynomial.
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    polynomial = sum(c * x**k for k, c in enumerate(coefficients))
    field = polynomial.number_field("a")
    rendered(field)
    a = field.primitive_element()
    rendered(a)
    assert polynomial(a) == field.zero()

    assert field in OwnedNumberFields()
    assert field in Fields()
    assert field.degree() == degree
    assert field.discriminant() == discriminant
    assert field.signature() == signature_pair(real_places, complex_places)
    assert field.class_number() == class_number
    assert field.is_galois() is galois
    assert field.cardinality() == aleph0

    # Its ring of integers and integral basis.
    integers = field.ring_of_integers()
    rendered(integers)
    assert integers in OwnedOrders()
    assert integers in IntegralDomains()
    assert integers in NoetherianRings()
    assert integers.is_maximal()
    assert integers.module_rank() == cardinal(degree)
    basis = integers.integral_basis()
    rendered(basis)
    assert basis.cardinality() == cardinal(degree)
    assert integers.fraction_field() is field
    assert (integers in PrincipalIdealDomains()) == (class_number == 1)
    assert integers.krull_dimension() == 1

    # Ramification, and the primes above the first few rational primes.
    assert field.ramified_primes().cardinality() == cardinal(len(ramified))
    for prime in ramified:
        assert prime in field.ramified_primes()
    for prime in (2, 3, 5, 7):
        primes = field.primes_above(prime)
        rendered(primes)
        assert primes.cardinality() >= cardinal(1)
        assert primes.cardinality() <= cardinal(degree)
        for prime_ideal in primes:
            rendered(prime_ideal)
            assert prime_ideal.is_prime()
            assert prime_ideal.is_maximal()
            residue = prime_ideal.quotient_ring()
            assert residue in Fields()
            assert residue.characteristic() == prime
            assert residue.cardinality() <= cardinal(prime**degree)

    # Localize at the first prime above 2, then complete.
    first = next(iter(field.primes_above(2)))
    local = integers.localize_at_prime(first)
    rendered(local)
    assert local in LocalRings()
    assert local in PrincipalIdealDomains()
    assert local.residue_field().characteristic() == 2
    assert local.maximal_ideal().is_maximal()
    completion = integers.adic_completion(first)
    rendered(completion)
    assert completion in CompleteLocalRings()
    assert completion.residue_field().characteristic() == 2
    assert completion.residue_field().cardinality() == local.residue_field().cardinality()

    # Galois theory.
    if galois:
        group = field.galois_group()
        rendered(group)
        assert group.order() == degree
        assert group.is_abelian()
    else:
        closure = field.normal_closure()
        rendered(closure)
        assert closure.degree() == 6
        assert field.normal_closure_galois_group().order() == 6

    # Embeddings into the reals and the complex numbers.
    assert field.embeddings(RR).cardinality() == cardinal(real_places)
    assert field.embeddings(CC).cardinality() == cardinal(degree)
    for embedding in field.embeddings(CC):
        rendered(embedding)
        assert embedding(field.one()) == CC.one()

    # Kähler differentials of the integers over ZZ are finite of order |disc|.
    omega = integers.as_algebra_over(ZZ).kahler_differentials()
    rendered(omega)
    assert omega.cardinality() == cardinal(abs(discriminant))

    # The arithmetic curve Spec O_K.
    curve = (integers).affine_spectrum()
    rendered(curve)
    assert curve in AffineSchemes(ZZ)
    assert curve.relative_dimension() == 0
    assert curve.coordinate_ring() is integers
    generic = curve.underlying_space().generic_point()
    assert generic.residue_field() is field
    closed = curve.underlying_space()(first)
    assert closed.residue_field().characteristic() == 2
    assert generic.specializes_to(closed)
    assert curve.stalk(closed) in LocalRings()
