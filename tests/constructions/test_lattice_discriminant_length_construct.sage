r"""A lattice reports the minimal number of generators of its discriminant group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_unimodular_hyperbolic_plane_has_discriminant_length_zero() -> None:
    lattice = NamedLattices.U

    assert lattice.discriminant_length() == ZZ.zero()


def test_a2_has_cyclic_discriminant_group_of_length_one() -> None:
    lattice = Lattices(ZZ)("A2")

    assert lattice.discriminant_length() == ZZ.one()
