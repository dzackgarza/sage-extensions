r"""Building the span of a few vectors asks the ambient lattice for no display.

The span basis names itself after the lattice it spans -- "the canonical span
basis in \(L\)" -- and a lattice's display computes its signature from its Gram.
A construction that renders that name has computed a signature for a reader who
does not exist, which is what the plane rows paid once per transported plane.
The contract is the display's, so the display is what this test counts: the
guard below is the class's rendering, and it is shown to be live by rendering
the lattice once by hand.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_building_a_subobject_asks_the_ambient_lattice_for_no_display() -> None:
    r"""Constructing \(L.subobject_on(\text{basis})\) renders no lattice."""
    lattice = Lattices(ZZ)([[2, 1], [1, 4]])
    basis = lattice.module_generators()
    rendering = Lattices(ZZ).ParentMethods
    rendered = []

    def counted_display(self):
        rendered.append(1)
        return "a lattice"

    rendering.__repr__ = counted_display
    span = lattice.subobject_on(basis)
    lattice.__repr__()
    del rendering.__repr__

    assert tuple(rendered) == (1,)
    assert span.ambient_lattice() is lattice
    assert span.module_rank() == lattice.module_rank()
