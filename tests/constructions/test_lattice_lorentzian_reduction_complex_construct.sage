r"""The even unimodular Lorentzian lattice (E_{10}) has a complete perfect-domain traversal."""

from sage_extensions.all import *  # noqa: F401,F403


def test_e10_lorentzian_reduction_complex_is_complete_and_nonempty() -> None:
    lattice = NamedLattices.E10
    traversal = lattice.lorentzian_reduction_complex()

    assert traversal.lattice() is lattice
    assert traversal.is_complete()
    assert traversal.cells().cardinality() >= cardinal(1)
    assert traversal.unpaired_facets().cardinality() == cardinal(0)
