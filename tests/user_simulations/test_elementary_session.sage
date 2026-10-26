r"""An elementary session parameterized by a natural number.

For one integer $n$: its factorization, the ring $\mathbb Z/n$, the cyclic
group of order $n$, the lattice $\langle n\rangle$, the quadratic field
$\mathbb Q(\sqrt n)$, the finite set of size $n$, the cardinal $n$ and the
ordinal $n$, each asked for what elementary arithmetic determines.
"""

import math

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


def _prime_factors(n: int) -> dict:
    factors = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def _euler_phi(n: int) -> int:
    result = n
    for p in _prime_factors(n):
        result = result // p * (p - 1)
    return result


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 8, 9, 12, 15, 16, 30, 97])
def test_an_elementary_session(n) -> None:
    factors = _prime_factors(n)
    is_prime = factors == {n: 1}
    is_prime_power = len(factors) == 1
    squarefree = all(exponent == 1 for exponent in factors.values())

    # The integer itself.
    integer = ZZ(n)
    rendered(integer)
    assert integer.prime_divisors() == Set(tuple(factors))
    for p, exponent in factors.items():
        assert integer.valuation(p) == exponent
        assert ZZ(p).divides(integer)
    assert integer.is_prime() == is_prime
    assert integer.is_square() == all(exponent % 2 == 0 for exponent in factors.values())
    assert integer.gcd(ZZ(6)) == math.gcd(n, 6)
    assert integer.lcm(ZZ(6)) == n * 6 // math.gcd(n, 6)

    # The ring of integers modulo n.
    residues = Zmod(n)
    rendered(residues)
    assert residues.cardinality() == cardinal(n)
    assert residues.characteristic() == n
    assert residues in ArtinianRings()
    assert (residues in Fields()) == is_prime
    assert (residues in IntegralDomains()) == is_prime
    assert (residues in LocalRings()) == is_prime_power
    assert (residues in PrincipalIdealDomains()) == is_prime
    units = residues.condition_set(lambda a: a.is_unit())
    rendered(units)
    assert units.cardinality() == cardinal(_euler_phi(n))
    assert residues(n - 1) * residues(n - 1) == residues.one()
    assert ZZ.ideal(n).is_prime() == is_prime
    assert ZZ.quotient_ring(ZZ.ideal(n)).cardinality() == cardinal(n)
    assert (residues).affine_spectrum().underlying_space().cardinality() == cardinal(len(factors))
    assert residues.spectrum().cardinality() == cardinal(len(factors))

    # The cyclic group and the cyclic module.
    cyclic = Groups.C(n)
    rendered(cyclic)
    assert cyclic.order() == n
    assert cyclic in AbelianGroups()
    assert cyclic.Aut().order() == _euler_phi(n)
    assert cyclic.group_generators()[0].order() == n
    assert cyclic.Mor(Groups.C(6)).cardinality() == cardinal(math.gcd(n, 6))
    module = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((n,))
    rendered(module)
    assert module.cardinality() == cardinal(n)
    assert module.annihilator() == ZZ.ideal(n)
    assert module.is_torsion()

    # The rank one lattice <n> and its discriminant group.
    lattice = Lattices(ZZ)([[n]])
    rendered(lattice)
    assert lattice.determinant() == n
    assert lattice.discriminant_group().cardinality() == cardinal(n)
    assert lattice.is_even() == (n % 2 == 0)
    assert lattice.is_positive_definite()
    assert lattice.O().order() == 2
    assert lattice.dual_lattice().determinant() == QQ(1) / n

    # The quadratic field Q(sqrt n) when n is not a square.
    if not integer.is_square():
        field = QuadraticField(n, "s")
        rendered(field)
        assert field.degree() == 2
        assert field.is_galois()
        root = field.primitive_element()
        assert root * root == field(n)
        assert field.discriminant() in (n, 4 * n) if squarefree else field.discriminant() != 0
        assert field.ring_of_integers().module_rank() == cardinal(2)
        assert RR(n).sqrt() ** 2 == RR(n)
        assert AA(n).sqrt().minpoly().degree() == 2
    else:
        assert AA(n).sqrt().minpoly().degree() == 1
        assert RR(n).sqrt() == RR(math.isqrt(n))

    # Finite sets, cardinals and ordinals of size n.
    finite = Sets.Δ[n - 1]
    rendered(finite)
    assert finite.cardinality() == cardinal(n)
    assert finite.cardinality() == cardinal(n)
    assert finite.power_set().cardinality() == cardinal(2**n)
    assert finite.subsets_of_size(2).cardinality() == cardinal(n * (n - 1) // 2)
    assert Sets().Mor(finite, finite).cardinality() == cardinal(n**n)
    assert finite.Aut().order() == math.factorial(n)
    assert cardinal(n) + cardinal(n) == cardinal(2 * n)
    assert cardinal(n) * cardinal(n) == cardinal(n * n)
    assert ordinal(n).cardinality() == cardinal(n)
    assert ordinal(n).ordinal_sum(1) == ordinal(n + 1)
    assert ordinal(1).ordinal_sum(ordinal(n)) == ordinal(n + 1)
