r"""The mod-five cyclotomic character sends Frobenius at p to p modulo five."""

from sage_extensions.all import *  # noqa: F401,F403


def test_mod_five_cyclotomic_character_has_the_expected_frobenius_values() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    character = CyclotomicCharacter(galois, 5)
    primitive_root = character.primitive_root()

    assert character.modulus() == 5
    assert primitive_root**5 == primitive_root.parent().one()
    assert character(galois.frobenius(7)) == 2
    assert character(galois.frobenius(11)) == 1
    assert character(galois.one()) == 1

