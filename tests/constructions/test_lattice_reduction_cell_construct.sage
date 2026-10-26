r"""A lattice reduction cell is a rational cone retaining its defining walls."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_reduction_cell_retains_inequality_wall() -> None:
    lattice = NamedLattices.U
    cell = lattice.reduction_cell(((1, 0),))

    assert cell.ambient_lattice() is lattice
    assert cell.halfspace_covectors().cardinality() == cardinal(1)


def test_hyperbolic_plane_reduction_cell_retains_equation_wall() -> None:
    lattice = NamedLattices.U
    cell = lattice.reduction_cell((), equations=((0, 1),))

    assert cell.equation_covectors().cardinality() == cardinal(1)
