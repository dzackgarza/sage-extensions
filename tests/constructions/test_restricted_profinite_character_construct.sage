r"""Restriction of a continuous profinite character remains continuous."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclotomic_character_restricted_to_its_kernel_is_continuous() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    character = CyclotomicCharacter(galois, 5)
    kernel = character.kernel()
    restricted = character.restrict(kernel)

    assert restricted.is_continuous()
    assert restricted(kernel.one()) == 1

