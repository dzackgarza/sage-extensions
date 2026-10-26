r"""The hyperbolic plane has one isotropic-line orbit and no isotropic-plane orbit."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_has_one_isotropic_line_orbit_representative() -> None:
    lattice = NamedLattices.U

    assert lattice.isotropic_line_orbit_representatives().cardinality() == cardinal(1)


def test_hyperbolic_plane_has_no_isotropic_plane_orbit_representatives() -> None:
    lattice = NamedLattices.U

    assert lattice.isotropic_plane_orbit_representatives().cardinality() == cardinal(0)


def test_hyperbolic_plane_has_no_rank_two_isotropic_flag_orbit_representatives() -> None:
    lattice = NamedLattices.U

    assert lattice.isotropic_flag_orbit_representatives(rank=2).cardinality() == cardinal(0)
