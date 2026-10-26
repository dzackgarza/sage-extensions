r"""Lattice orthogonal-group spellings all name the owned automorphism group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_bilinear_orthogonal_group_is_its_automorphism_group() -> None:
    lattice = NamedLattices.U

    assert lattice.bilinear_orthogonal_group() is lattice.Aut()


def test_hyperbolic_plane_quadratic_orthogonal_group_is_the_same_group() -> None:
    lattice = NamedLattices.U

    assert lattice.quadratic_orthogonal_group() is lattice.Aut()
    assert lattice.quadratic_orthogonal_group() is lattice.bilinear_orthogonal_group()
