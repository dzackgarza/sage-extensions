r"""Two orthogonal isotropic basis vectors in (Uoplus U) define a rank-(1<2) isotropic flag."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_u_builds_a_two_step_isotropic_flag() -> None:
    lattice = NamedLattices.U + NamedLattices.U
    first = lattice.module_generators()[0]
    second = lattice.module_generators()[2]
    flag = lattice.isotropic_flag(first, second)

    assert flag.flag_length() == cardinal(2)
    assert flag.top().module_rank() == cardinal(2)


def test_two_u_flag_lies_in_rank_one_two_isotropic_flag_locus() -> None:
    lattice = NamedLattices.U + NamedLattices.U
    first = lattice.module_generators()[0]
    second = lattice.module_generators()[2]
    flag = lattice.isotropic_flag(first, second)

    assert flag in lattice.isotropic_flag_locus((1, 2))
