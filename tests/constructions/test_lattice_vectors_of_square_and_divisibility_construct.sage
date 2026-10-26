r"""The two roots of (A_1) have square (-2) and divisibility (2)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_square_minus_two_divisibility_two_shell_is_its_two_roots() -> None:
    lattice = NamedLattices.A1
    root = lattice.basis_vector(0)
    shell = lattice.vectors_of_square_and_divisibility(-2, 2)

    assert shell.cardinality() == cardinal(2)
    assert root in shell
    assert -root in shell
