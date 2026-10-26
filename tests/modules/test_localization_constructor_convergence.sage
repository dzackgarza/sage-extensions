r"""Localization of abelian groups at a prime is exact."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_determinant_three_endomorphism_of_z2_becomes_invertible_at_the_prime_2() -> None:
    r"""$f(e) = e + f'$, $f(f') = 3f'$ has $\operatorname{coker} f = \mathbb Z/3$; since localization is
    exact, $f_{(2)}$ is an isomorphism ($3$ is a unit in $\mathbb Z_{(2)}$) while $f_{(3)}$ is not.

    Source: Atiyah–Macdonald, Introduction to Commutative Algebra, 3.3 and 3.8.
    """
    M = ZZ**2
    e, f = M.module_generator(0), M.module_generator(1)
    endomorphism = M.End()({0: e + f, 1: 3 * f})
    cokernel = endomorphism.cokernel()
    assert cokernel.cardinality() == 3
    assert cokernel.localize_at_prime(ZZ.ideal(2)).is_zero()
    assert not cokernel.localize_at_prime(ZZ.ideal(3)).is_zero()
    assert M.localize_at_prime(ZZ.ideal(2)).module_rank() == 2
