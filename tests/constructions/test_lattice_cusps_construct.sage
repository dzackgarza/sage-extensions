r"""The hyperbolic plane has one primitive isotropic-line orbit and no isotropic planes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_has_one_line_cusp() -> None:
    lattice = NamedLattices.U

    assert lattice.cusps(1).cardinality() == cardinal(1)


def test_hyperbolic_plane_has_no_plane_cusps() -> None:
    lattice = NamedLattices.U

    assert lattice.cusps(2).cardinality() == cardinal(0)
