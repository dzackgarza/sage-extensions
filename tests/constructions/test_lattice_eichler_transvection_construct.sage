r"""An Eichler transvection fixes its isotropic vector and acts by the defining formula."""

from sage_extensions.all import *  # noqa: F401,F403


def test_u_plus_a2_eichler_transvection_fixes_isotropic_vector() -> None:
    lattice = NamedLattices.U + NamedLattices.A2
    isotropic, partner, root, _second_root = lattice.module_generators()
    transvection = lattice.eichler_transvection(isotropic, root)

    assert transvection(isotropic) == isotropic
    assert transvection(partner) == partner + root + isotropic
