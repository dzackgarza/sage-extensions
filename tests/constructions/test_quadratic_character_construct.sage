r"""The character of Q(i)/Q detects the splitting sign of odd Frobenius elements."""

from sage_extensions.all import *  # noqa: F401,F403


def test_gaussian_quadratic_character_has_the_expected_frobenius_values() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    character = QuadraticCharacter(galois, -4)
    square_class = character.square_class()
    square_root = character.square_root()

    assert (QQ(-4) / square_class).is_square()
    assert square_root * square_root == square_root.parent()(-4)
    assert character(galois.frobenius(3)) == -1
    assert character(galois.frobenius(5)) == 1
    assert character(galois.frobenius(13)) == 1
