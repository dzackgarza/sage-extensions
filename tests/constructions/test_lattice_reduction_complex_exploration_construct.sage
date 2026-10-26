r"""A lattice retains explicitly supplied cells in a finite reduction-complex exploration."""

from sage_extensions.all import *  # noqa: F401,F403


def test_one_cell_reduction_complex_retains_lattice_and_cell() -> None:
    lattice = NamedLattices.U
    cell = lattice.reduction_cell(((1, 0),))
    exploration = lattice.reduction_complex_exploration((cell,), ())

    assert exploration.lattice() is lattice
    assert exploration.cells().cardinality() == cardinal(1)
    assert exploration.cells()[0] is cell


def test_one_cell_reduction_complex_is_not_declared_complete() -> None:
    lattice = NamedLattices.U
    cell = lattice.reduction_cell(((1, 0),))
    exploration = lattice.reduction_complex_exploration((cell,), ())

    assert exploration.adjacencies().cardinality() == cardinal(0)
    assert not exploration.is_complete()
