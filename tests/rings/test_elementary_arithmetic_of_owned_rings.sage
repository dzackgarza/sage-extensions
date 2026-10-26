r"""Elementary arithmetic in the integers, the rationals, a finite field and a polynomial ring.

Every value below is a hand computation from the definitions: Bezout's identity for
the greatest common divisor, ``gcd * lcm = |ab|``, Euclidean division, the prime
factorization ``360 = 2^3 3^2 5``, Euler's function ``phi(12) = 4``, the multiplicative
order of a primitive root modulo 7, and the resultant ``Res(f, x - a) = f(a)`` for a
polynomial ``f`` of even degree.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_gcd_lcm_and_bezout_in_the_integers() -> None:
    a = ZZ(12)
    b = ZZ(18)
    g, s, t = a.xgcd(b)

    assert a.gcd(b) == 6
    assert a.lcm(b) == 36
    assert a.gcd(b) * a.lcm(b) == a * b
    assert g == 6
    assert s * a + t * b == g


def test_euclidean_division_in_the_integers() -> None:
    quotient, remainder = ZZ(47).quo_rem(ZZ(5))

    assert quotient == 9
    assert remainder == 2
    assert ZZ(47) // ZZ(5) == quotient
    assert ZZ(47) % ZZ(5) == remainder
    assert ZZ(12).divides(ZZ(36))
    assert not ZZ(12).divides(ZZ(30))


def test_prime_factorization_and_divisor_functions_of_three_hundred_sixty() -> None:
    n = ZZ(360)
    factorization = n.factor()

    assert factorization.reconstruct() == n
    assert factorization.unit() == 1
    assert n.prime_divisors().cardinality() == 3
    assert ZZ(5) in n.prime_divisors()
    assert ZZ(7) not in n.prime_divisors()
    assert n.valuation(ZZ(2)) == 3
    assert n.valuation(ZZ(3)) == 2
    assert n.number_of_divisors() == 24
    assert n.divisors().cardinality() == 24
    assert n.euler_phi() == 96


def test_primality_factorial_binomial_and_square_roots() -> None:
    assert ZZ(7).is_prime()
    assert not ZZ(91).is_prime()
    assert ZZ(5).factorial() == 120
    assert ZZ(5).binomial(ZZ(2)) == 10
    assert ZZ(16).is_square()
    assert not ZZ(15).is_square()
    assert ZZ(16).sqrt() == 4


def test_rationals_in_lowest_terms_and_their_inverses() -> None:
    q = QQ(6) / QQ(8)

    assert q.numerator() == 3
    assert q.denominator() == 4
    assert q * ~q == 1
    assert QQ(1) / q == QQ(4) / QQ(3)
    assert q**(-2) == QQ(16) / QQ(9)
    assert q < QQ(1)
    assert abs(QQ(-3) / QQ(4)) == q


def test_the_owned_integers_coerce_canonically_into_the_rationals_and_reals() -> None:
    rational_coercion = QQ.coerce_map_from(ZZ)
    real_coercion = RR.coerce_map_from(ZZ)

    assert rational_coercion is not None
    assert real_coercion is not None
    assert rational_coercion(ZZ(4)) == QQ(4)
    assert real_coercion(ZZ(4)) == RR(4)


def test_three_is_a_primitive_root_modulo_seven() -> None:
    field = GF(7)
    three = field(3)

    assert field.characteristic() == 7
    assert three.multiplicative_order() == 6
    assert (field(2)).multiplicative_order() == 3
    assert three.additive_order() == 7


def test_x_squared_minus_two_is_irreducible_over_the_rationals() -> None:
    polynomial_ring = QQ["x"]
    x = polynomial_ring.algebra_generator("x")
    f = x**2 - 2

    assert f.degree() == 2
    assert f.is_irreducible()
    assert f.discriminant() == 8
    assert f.resultant(x - 3) == 7
    assert f.splitting_field().degree() == 2


def test_t_squared_minus_one_splits_over_the_integers() -> None:
    polynomial_ring = ZZ["t"]
    t = polynomial_ring.algebra_generator("t")
    f = t**2 - 1

    assert f.factor().reconstruct() == f
    assert not f.is_irreducible()
    assert (t**3 - t).gcd(f) == f


def test_three_hundred_sixty_has_three_distinct_prime_factors() -> None:
    assert ZZ(360).factor().cardinality() == 3


def test_x_squared_minus_two_has_no_rational_root() -> None:
    x = QQ["x"].algebra_generator("x")

    assert (x**2 - 2).roots().cardinality() == 0


def test_t_squared_minus_one_has_two_integer_roots_and_two_irreducible_factors() -> None:
    t = ZZ["t"].algebra_generator("t")

    assert (t**2 - 1).roots().cardinality() == 2
    assert (t**2 - 1).factor().cardinality() == 2
