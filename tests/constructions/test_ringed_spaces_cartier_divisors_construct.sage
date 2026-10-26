r"""On a ringed space, Cartier divisors are global sections of K_X^*/O_X^*."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cartier_divisor_group_is_global_sections_of_cartier_sheaf() -> None:
    line = AffineSpaces(QQ)(1)
    sheaf = line.cartier_divisor_sheaf()
    group = line.cartier_divisor_group()

    assert sheaf.global_sections() is group
    assert group.quotient_sheaf() is sheaf
