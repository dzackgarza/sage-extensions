r"""The standard square lattice has successive minima one and one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_rank_two_lattice_has_unit_successive_minima() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    minima = lattice.successive_minima()

    assert minima.cardinality() == cardinal(2)
    assert minima[0] ** 2 == 1
    assert minima[1] ** 2 == 1
