r"""Cyclotomic characters are continuous profinite characters with open kernel."""

from sage_extensions.all import *  # noqa: F401,F403


def test_mod_five_cyclotomic_character_factors_through_a_finite_extension() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    character = CyclotomicCharacter(galois, 5)
    extension = character.extension()
    kernel = character.kernel()

    assert character.is_continuous()
    assert character.factor_extension() is extension
    assert kernel in OpenAbsoluteGaloisSubgroups(galois)
    assert kernel.index() == 4
    assert character(galois.one()) == 1


def test_restricting_cyclotomic_character_to_its_kernel_is_trivial_at_identity() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    character = CyclotomicCharacter(galois, 5)
    kernel = character.kernel()
    restricted = character.restrict(kernel)

    assert restricted.is_continuous()
    assert restricted(kernel.one()) == 1

