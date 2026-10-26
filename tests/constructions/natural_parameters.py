"""Elementary arithmetic of the natural parameters the property tests range over.

Pure Python with PEP 316 contracts, so CrossHair can check it:

    uvx --from crosshair-tool crosshair check tests/constructions/natural_parameters.py

These are the expected values the property tests compare the session
against: what elementary number theory says about an integer before any
ring is built from it.  Everything Sage-backed is opaque to CrossHair, so
this file holds only what a symbolic checker can see through.
"""

from math import isqrt


def is_prime(n: int) -> bool:
    """
    pre: n >= 0
    post: __return__ == (n >= 2 and all(n % d for d in range(2, n)))
    """
    if n < 2:
        return False
    for d in range(2, isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def prime_factorization(n: int) -> dict[int, int]:
    """
    pre: n >= 1
    post: all(is_prime(p) and e >= 1 for p, e in __return__.items())
    post: __import__("math").prod(p**e for p, e in __return__.items()) == n
    """
    factors: dict[int, int] = {}
    remaining = n
    p = 2
    while p * p <= remaining:
        while remaining % p == 0:
            factors[p] = factors.get(p, 0) + 1
            remaining //= p
        p += 1
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors


def euler_phi(n: int) -> int:
    """
    pre: n >= 1
    post: 1 <= __return__ <= n
    post: __return__ == sum(1 for k in range(1, n + 1) if __import__("math").gcd(k, n) == 1)
    """
    result = n
    for p in prime_factorization(n):
        result = result // p * (p - 1)
    return result


def number_of_divisors(n: int) -> int:
    """
    pre: n >= 1
    post: __return__ == sum(1 for d in range(1, n + 1) if n % d == 0)
    """
    result = 1
    for exponent in prime_factorization(n).values():
        result *= exponent + 1
    return result


def squarefree_part(n: int) -> int:
    """
    pre: n != 0
    post: __return__ != 0
    post: all(e == 1 for e in prime_factorization(abs(__return__)).values())
    post: (n // __return__) > 0 and isqrt(n // __return__) ** 2 == n // __return__
    """
    sign = -1 if n < 0 else 1
    result = 1
    for p, exponent in prime_factorization(abs(n)).items():
        if exponent % 2:
            result *= p
    return sign * result


def is_squarefree(n: int) -> bool:
    """
    pre: n != 0
    post: __return__ == (squarefree_part(n) == n)
    """
    return all(exponent == 1 for exponent in prime_factorization(abs(n)).values())


def quadratic_field_discriminant(d: int) -> int:
    """
    The discriminant of Q(sqrt d) for squarefree d: d if d = 1 mod 4, else 4d.

    pre: d != 0 and d != 1 and is_squarefree(d)
    post: __return__ % 4 in (0, 1)
    post: squarefree_part(__return__) == d
    """
    return d if d % 4 == 1 else 4 * d


def binomial(n: int, k: int) -> int:
    """
    pre: n >= 0
    post: __return__ >= 0
    post: (0 <= k <= n) or __return__ == 0
    """
    if k < 0 or k > n:
        return 0
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def determinant_2x2(gram: list[list[int]]) -> int:
    """
    pre: len(gram) == 2 and all(len(row) == 2 for row in gram)
    post: __return__ == gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
    """
    return gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]


def signature_2x2(gram: list[list[int]]) -> tuple[int, int]:
    """
    The inertia (p, q) of a symmetric 2x2 integer matrix by Sylvester's criterion.

    pre: len(gram) == 2 and all(len(row) == 2 for row in gram) and gram[0][1] == gram[1][0]
    post: __return__[0] + __return__[1] <= 2
    post: (determinant_2x2(gram) > 0) == (__return__ in ((2, 0), (0, 2)))
    post: (determinant_2x2(gram) < 0) == (__return__ == (1, 1))
    """
    det = determinant_2x2(gram)
    trace = gram[0][0] + gram[1][1]
    if det > 0:
        return (2, 0) if trace > 0 else (0, 2)
    if det < 0:
        return (1, 1)
    if trace > 0:
        return (1, 0)
    if trace < 0:
        return (0, 1)
    return (0, 0)
