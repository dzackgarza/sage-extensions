r"""Building the span of a few vectors asks the ambient lattice for no display.

The span basis names itself after the lattice it spans -- "the canonical span
basis in \(L\)" -- and a lattice's display computes its signature from its Gram.
A construction that renders that name has computed a signature for a reader who
does not exist.  The contract is the display's, so the display is what this test
counts: the guard is the lattice's own rendering, and it is shown to be live by
rendering the lattice once by hand.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_building_a_subobject_asks_the_ambient_lattice_for_no_display() -> None:
    r"""Constructing \(L.subobject_on(\text{basis})\) renders no lattice."""
    lattice = Lattices(ZZ)([[2, 1], [1, 4]])
    basis = lattice.module_generators()

    def build_and_display():
        span = lattice.subobject_on(basis)
        lattice.__repr__()
        return span

    span, rendered = displays_rendered_by(lattice, build_and_display)

    assert rendered == 1
    assert span.ambient_lattice() is lattice
    assert span.module_rank() == lattice.module_rank()
