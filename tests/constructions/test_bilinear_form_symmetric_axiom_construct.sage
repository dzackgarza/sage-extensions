r"""Lattice pairings lie in the symmetric bilinear refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_lattice_lies_in_the_symmetric_bilinear_refinement() -> None:
    form = Lattices(ZZ)("A2")
    category = BilinearFormModules(ZZ).Symmetric()
    e0, e1 = form.module_generator(0), form.module_generator(1)

    assert form in category
    assert form.b(e0, e1) == form.b(e1, e0)
