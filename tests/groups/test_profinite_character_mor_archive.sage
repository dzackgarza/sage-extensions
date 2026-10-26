r"""The mod-3 cyclotomic character of the absolute Galois group of $\mathbf{F}_5$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_mod_three_cyclotomic_character_of_f5_has_kernel_of_index_two() -> None:
    r"""$\chi_3(\mathrm{Frob}_5) = 5 \equiv 2 \pmod 3$, of order 2 in $(\mathbf{Z}/3)^\times$.

    So $\chi_3$ is surjective onto $(\mathbf{Z}/3)^\times$ and its kernel,
    $\operatorname{Gal}(\overline{\mathbf{F}}_5/\mathbf{F}_{25})$, has index 2.
    """
    group = GF(5).absolute_galois_group()
    character = group.cyclotomic_character(3)
    frobenius = group.frobenius()
    one = character.codomain().one()

    assert character(frobenius) != one
    assert character(frobenius) ** 2 == one
    assert character.kernel().index() == 2
