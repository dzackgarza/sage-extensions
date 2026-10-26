r"""Quotienting a rank-two lattice by a rank-one radical leaves rank one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_lattice_with_one_dimensional_radical_has_rank_one_quotient() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, 0]])
    quotient = lattice.radical_quotient()

    assert lattice.radical().module_rank() == cardinal(1)
    assert quotient.module_rank() == cardinal(1)
    assert quotient.is_nondegenerate()
