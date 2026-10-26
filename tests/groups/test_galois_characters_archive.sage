r"""Continuous characters of $G_{\mathbb{F}_5}$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_mod_three_cyclotomic_character_of_f5_factors_through_f25() -> None:
    r"""$\chi_3(\mathrm{Frob}) = 5 \equiv 2 \bmod 3$ has order $2$, so $\chi_3$ factors through $\mathbb{F}_5(\mu_3) = \mathbb{F}_{25}$ and is multiplicative."""
    group = GF(5).absolute_galois_group()
    character = group.cyclotomic_character(3)
    frobenius = group.frobenius()

    assert character.factor_extension().degree() == 2
    assert character(frobenius).value() == 2
    assert character(group.one()) == character.codomain().one()
    assert character(frobenius**5) == character(frobenius**2) * character(frobenius**3)


def test_the_quadratic_character_of_two_over_f5_has_kernel_of_index_two() -> None:
    r"""$2$ is not a square mod $5$, so $\mathrm{Frob}(\sqrt2) = -\sqrt2$.

    The kernel fixes $\mathbb{F}_{25}$: index $2$, excluding $\mathrm{Frob}$
    and containing $\mathrm{Frob}^2$; the character restricted to its kernel
    is trivial.
    """
    group = GF(5).absolute_galois_group()
    character = group.quadratic_character(2)
    frobenius = group.frobenius()
    kernel = character.kernel()

    assert kernel.index() == 2
    assert frobenius not in kernel
    assert frobenius**2 in kernel
    assert character(frobenius) != character.codomain().one()
    assert character.restrict(kernel)(kernel.frobenius()) == character.codomain().one()
