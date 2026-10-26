r"""The A2 lattice is a finitely presented bilinear-form module."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_lattice_lies_in_the_finitely_presented_bilinear_refinement() -> None:
    form = Lattices(ZZ)("A2")
    category = BilinearFormModules(ZZ).FinitelyPresented()

    assert form in category
    assert form.is_finitely_presented()
    assert form.b(form.module_generator(0), form.module_generator(1)) == -1
