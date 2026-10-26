r"""Fractional ideals of $\mathbb Z$: membership, inverses, products, sums and intersections.

Every fractional ideal of $\mathbb Z$ is $q\mathbb Z$ for a unique positive rational $q$; they form a
group under multiplication with $(q)^{-1} = (1/q)$ and $(q)(r) = (qr)$, and $(q) + (r) =
(\gcd(q, r))$, $(q) \cap (r) = (\operatorname{lcm}(q, r))$, where for $q = a/b$ in lowest terms the
gcd and lcm of rationals are taken prime by prime on the valuations (by hand:
$\gcd(1/2, 1/3) = 1/6$, $\operatorname{lcm}(1/2, 1/3) = 1$).
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_one_half_z_contains_one_half_and_not_one_quarter() -> None:
    r"""$\tfrac12 \in \tfrac12\mathbb Z$, $\tfrac14 \notin \tfrac12\mathbb Z$, and $\tfrac12$ generates it."""
    half = ZZ.fractional_ideal(QQ(1) / 2)

    assert QQ(1) / 2 in half
    assert QQ(3) / 2 in half
    assert QQ(1) / 4 not in half
    assert half.principal_generator() == QQ(1) / 2


def test_the_inverse_of_one_half_z_is_two_z() -> None:
    r"""$(\tfrac12)^{-1} = (2)$ and $(\tfrac12)(2) = (1)$."""
    half = ZZ.fractional_ideal(QQ(1) / 2)

    assert half.inverse() == ZZ.fractional_ideal(2)
    assert half * half.inverse() == ZZ.fractional_ideal(1)


def test_the_product_of_two_thirds_z_and_three_quarters_z_is_one_half_z() -> None:
    r"""$(\tfrac23)(\tfrac34) = (\tfrac12)$."""
    assert ZZ.fractional_ideal(QQ(2) / 3) * ZZ.fractional_ideal(QQ(3) / 4) == ZZ.fractional_ideal(QQ(1) / 2)


def test_the_sum_and_intersection_of_one_half_z_and_one_third_z() -> None:
    r"""$(\tfrac12) + (\tfrac13) = (\tfrac16)$ and $(\tfrac12) \cap (\tfrac13) = (1)$."""
    half = ZZ.fractional_ideal(QQ(1) / 2)
    third = ZZ.fractional_ideal(QQ(1) / 3)

    assert half + third == ZZ.fractional_ideal(QQ(1) / 6)
    assert half.intersection(third) == ZZ.fractional_ideal(1)
