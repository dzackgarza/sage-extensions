r"""The Cartier divisor group of P^1 is the global sections of K_X^*/O_X^*."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cartier_divisor_group_of_projective_line() -> None:
    line = ProjectiveSpaces(QQ)(1)
    cartier = CartierDivisorGroups().of_scheme(line)

    assert cartier in CartierDivisorGroups()
    assert cartier.quotient_sheaf().global_sections() is cartier
    assert cartier.base_ring() is ZZ
