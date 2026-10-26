r"""A lattice reports the base-ring lattice category that owns it."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_reports_its_lattice_category() -> None:
    lattice = NamedLattices.U

    assert lattice.lattice_category() is Lattices(ZZ)
    assert lattice in lattice.lattice_category()
